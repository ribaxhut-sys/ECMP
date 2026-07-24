"""SLA application service (no FastAPI imports)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from app.core.errors import NotFoundError, ValidationAppError
from app.modules.sla.evaluation import evaluate_statuses
from app.modules.sla.repository import SlaRepository
from app.modules.sla.schemas import (
    SlaPolicyCreateRequest,
    SlaPolicyResponse,
    SlaRecordResponse,
)
from app.modules.sla.timeline import (
    build_sla_timeline_metadata,
    iter_sla_stage_specs,
    timeline_event_for_transition,
    timeline_summary,
)

COMPLAINT_DELETE_RESTRICTED_MESSAGE = (
    "Complaint cannot be deleted while an SLA record exists."
)
DUPLICATE_SLA_MESSAGE = "Complaint already has an SLA record."
NO_ACTIVE_SLA_POLICY_MESSAGE = (
    "An active SLA policy is required before creating a complaint."
)


def _to_record_response(row: object) -> SlaRecordResponse:
    return SlaRecordResponse.model_validate(row)


def _to_policy_response(row: object) -> SlaPolicyResponse:
    return SlaPolicyResponse.model_validate(row)


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def calculate_deadlines(
    created_at: datetime,
    *,
    assignment_target_minutes: int,
    appointment_target_minutes: int,
    resolution_target_minutes: int,
    escalation_target_minutes: int,
    overall_target_minutes: int,
) -> dict[str, datetime]:
    """Pure deadline math (TASK-023 / DEC-012). No breach / countdown."""
    base = _ensure_utc(created_at)
    return {
        "assignment_due_at": base + timedelta(minutes=assignment_target_minutes),
        "appointment_due_at": base + timedelta(minutes=appointment_target_minutes),
        "resolution_due_at": base + timedelta(minutes=resolution_target_minutes),
        "escalation_due_at": base + timedelta(minutes=escalation_target_minutes),
        "overall_due_at": base + timedelta(minutes=overall_target_minutes),
    }


class SlaService:
    def __init__(self, repository: SlaRepository) -> None:
        self._repo = repository

    def get_for_complaint(self, complaint_id: uuid.UUID) -> SlaRecordResponse:
        """API-314 — return SLA record; re-evaluate statuses from due_at snapshots.

        Does not recalculate deadlines or re-read policy. Enables overdue
        BREACHED visibility without a scheduler (DEC-013).
        """
        complaint = self._repo.get_complaint(complaint_id)
        if complaint is None:
            raise NotFoundError("Complaint not found")

        row = self._repo.get_by_complaint_id(complaint_id)
        if row is None:
            raise NotFoundError("SLA record not found")

        evaluated = self.evaluate_for_complaint(complaint_id, commit=True)
        return evaluated if evaluated is not None else _to_record_response(row)

    def create_pending_for_complaint(
        self,
        complaint_id: uuid.UUID,
        *,
        commit: bool = False,
    ) -> SlaRecordResponse:
        """Internal legacy helper: PENDING row with NULL deadlines (TASK-021)."""
        existing = self._repo.get_by_complaint_id(complaint_id)
        if existing is not None:
            raise ValidationAppError(
                DUPLICATE_SLA_MESSAGE,
                details={"complaintId": str(complaint_id)},
            )
        row = self._repo.create_pending(complaint_id)
        if commit:
            self._repo.commit()
            self._repo.refresh(row)
        return _to_record_response(row)

    def create_for_complaint(
        self,
        complaint_id: uuid.UUID,
        *,
        created_at: datetime,
        commit: bool = False,
    ) -> SlaRecordResponse:
        """Create immutable SLA deadline snapshot from the active policy.

        Evaluates the active SLA policy once at complaint create (DEC-012).
        Rejects when no active policy exists. Does not recalculate later.
        Statuses remain PENDING — no breach / timer / scheduler logic.
        """
        existing = self._repo.get_by_complaint_id(complaint_id)
        if existing is not None:
            raise ValidationAppError(
                DUPLICATE_SLA_MESSAGE,
                details={"complaintId": str(complaint_id)},
            )

        policy = self._repo.get_active_policy()
        if policy is None:
            raise ValidationAppError(
                NO_ACTIVE_SLA_POLICY_MESSAGE,
                details={"complaintId": str(complaint_id)},
            )

        deadlines = calculate_deadlines(
            created_at,
            assignment_target_minutes=policy.assignment_target_minutes,
            appointment_target_minutes=policy.appointment_target_minutes,
            resolution_target_minutes=policy.resolution_target_minutes,
            escalation_target_minutes=policy.escalation_target_minutes,
            overall_target_minutes=policy.overall_target_minutes,
        )
        row = self._repo.create_with_deadlines(
            complaint_id,
            created_at=_ensure_utc(created_at),
            **deadlines,
        )
        # TASK-024 — evaluate statuses at create (typically all PENDING).
        self.evaluate_for_complaint(complaint_id, now=created_at, commit=False)
        row = self._repo.get_by_complaint_id(complaint_id) or row
        if commit:
            self._repo.commit()
            self._repo.refresh(row)
        return _to_record_response(row)

    def evaluate_for_complaint(
        self,
        complaint_id: uuid.UUID,
        *,
        now: datetime | None = None,
        commit: bool = False,
    ) -> SlaRecordResponse | None:
        """Evaluate SLA statuses from stored due_at snapshots (TASK-024 / DEC-013).

        Never reads SLA Policy. Never modifies *_due_at.
        Idempotent when business completion facts are unchanged.
        Emits complaint timeline events only when a stage status changes
        to COMPLETED or BREACHED (TASK-025 / DEC-014; SYSTEM actor).
        Returns None when no SLA row exists (e.g. legacy complaint).
        """
        row = self._repo.get_by_complaint_id(complaint_id)
        if row is None:
            return None

        when = now or datetime.now(UTC)
        old_statuses = {
            "assignment": row.assignment_status,
            "appointment": row.appointment_status,
            "resolution": row.resolution_status,
            "escalation": row.escalation_status,
            "overall": row.overall_status,
        }

        facts = self._repo.load_completion_facts(complaint_id)
        snapshot = evaluate_statuses(
            assignment_due_at=row.assignment_due_at,
            appointment_due_at=row.appointment_due_at,
            resolution_due_at=row.resolution_due_at,
            escalation_due_at=row.escalation_due_at,
            overall_due_at=row.overall_due_at,
            facts=facts,
            now=when,
        )

        frozen_dues = (
            row.assignment_due_at,
            row.appointment_due_at,
            row.resolution_due_at,
            row.escalation_due_at,
            row.overall_due_at,
        )
        self._repo.update_statuses(
            row,
            assignment_status=snapshot.assignment_status,
            appointment_status=snapshot.appointment_status,
            resolution_status=snapshot.resolution_status,
            escalation_status=snapshot.escalation_status,
            overall_status=snapshot.overall_status,
            now=when,
        )
        # Hard guard: deadlines remain immutable.
        assert (
            row.assignment_due_at,
            row.appointment_due_at,
            row.resolution_due_at,
            row.escalation_due_at,
            row.overall_due_at,
        ) == frozen_dues

        new_statuses = {
            "assignment": snapshot.assignment_status,
            "appointment": snapshot.appointment_status,
            "resolution": snapshot.resolution_status,
            "escalation": snapshot.escalation_status,
            "overall": snapshot.overall_status,
        }
        due_by_stage = {
            "assignment": row.assignment_due_at,
            "appointment": row.appointment_due_at,
            "resolution": row.resolution_due_at,
            "escalation": row.escalation_due_at,
            "overall": row.overall_due_at,
        }
        for stage, _due_attr, _status_attr, _c, _b in iter_sla_stage_specs():
            event = timeline_event_for_transition(
                stage=stage,
                old_status=old_statuses[stage],
                new_status=new_statuses[stage],
            )
            if event is None:
                continue
            self._repo.add_timeline(
                complaint_id=complaint_id,
                event_type=event.value,
                event_at=when,
                summary=timeline_summary(event),
                metadata=build_sla_timeline_metadata(
                    stage=stage,
                    old_status=old_statuses[stage],
                    new_status=new_statuses[stage],
                    due_at=due_by_stage[stage],
                    occurred_at=when,
                ),
            )

        if commit:
            self._repo.commit()
            self._repo.refresh(row)
        return _to_record_response(row)

    def assert_complaint_deletable(self, complaint_id: uuid.UUID) -> None:
        """Business rule: complaint deletion restricted while SLA exists."""
        if self._repo.get_by_complaint_id(complaint_id) is not None:
            raise ValidationAppError(
                COMPLAINT_DELETE_RESTRICTED_MESSAGE,
                details={"complaintId": str(complaint_id)},
            )

    # --- SLA policies (TASK-022 / API-315–317) ---

    def list_policies(self) -> list[SlaPolicyResponse]:
        """API-315 — list all SLA policies (active first)."""
        return [_to_policy_response(row) for row in self._repo.list_policies()]

    def create_policy(
        self,
        payload: SlaPolicyCreateRequest,
        *,
        commit: bool = True,
    ) -> SlaPolicyResponse:
        """API-316 — create policy.

        New policies are created inactive so activation is explicit and only
        one policy remains active. Existing complaint SLA rows are untouched.
        """
        row = self._repo.create_policy(
            name=payload.name,
            description=payload.description,
            assignment_target_minutes=payload.assignment_target_minutes,
            appointment_target_minutes=payload.appointment_target_minutes,
            resolution_target_minutes=payload.resolution_target_minutes,
            escalation_target_minutes=payload.escalation_target_minutes,
            overall_target_minutes=payload.overall_target_minutes,
            is_active=False,
        )
        if commit:
            self._repo.commit()
            self._repo.refresh(row)
        return _to_policy_response(row)

    def activate_policy(
        self,
        policy_id: uuid.UUID,
        *,
        commit: bool = True,
    ) -> SlaPolicyResponse:
        """API-317 — activate a policy; deactivate any previously active one.

        Does not recalculate existing complaint SLA deadlines.
        """
        policy = self._repo.get_policy(policy_id)
        if policy is None:
            raise NotFoundError("SLA policy not found")

        if policy.is_active:
            return _to_policy_response(policy)

        self._repo.deactivate_all_policies()
        self._repo.set_policy_active(policy, is_active=True)
        if commit:
            self._repo.commit()
            self._repo.refresh(policy)
        return _to_policy_response(policy)
