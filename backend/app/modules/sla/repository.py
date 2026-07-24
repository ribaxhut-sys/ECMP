"""SLA persistence repository (SQLAlchemy 2.x)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.core.enums import AppointmentStatus, EscalationRequestStatus, SlaStatus
from app.models import (
    Appointment,
    Complaint,
    ComplaintAssignment,
    ComplaintEscalation,
    ComplaintResolution,
    ComplaintTimeline,
    SlaPolicy,
    SlaRecord,
)
from app.modules.sla.evaluation import SlaCompletionFacts


class SlaRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    @property
    def session(self) -> Session:
        return self._session

    def get_complaint(self, complaint_id: uuid.UUID) -> Complaint | None:
        stmt = select(Complaint).where(
            Complaint.id == complaint_id,
            Complaint.deleted_at.is_(None),
        )
        return self._session.scalar(stmt)

    def get_by_complaint_id(self, complaint_id: uuid.UUID) -> SlaRecord | None:
        stmt = select(SlaRecord).where(SlaRecord.complaint_id == complaint_id)
        return self._session.scalar(stmt)

    def count_for_complaint(self, complaint_id: uuid.UUID) -> int:
        stmt = select(SlaRecord.id).where(SlaRecord.complaint_id == complaint_id)
        return len(list(self._session.scalars(stmt).all()))

    def load_completion_facts(self, complaint_id: uuid.UUID) -> SlaCompletionFacts:
        """Load business completion timestamps (never reads SLA Policy)."""
        assignment_completed_at = self._session.scalar(
            select(func.min(ComplaintAssignment.assigned_at)).where(
                ComplaintAssignment.complaint_id == complaint_id,
                ComplaintAssignment.deleted_at.is_(None),
            )
        )
        appointment_completed_at = self._session.scalar(
            select(func.min(Appointment.completed_at))
            .join(
                ComplaintEscalation,
                Appointment.escalation_id == ComplaintEscalation.id,
            )
            .where(
                ComplaintEscalation.complaint_id == complaint_id,
                ComplaintEscalation.deleted_at.is_(None),
                Appointment.deleted_at.is_(None),
                Appointment.completed_at.is_not(None),
                Appointment.status == AppointmentStatus.COMPLETED,
            )
        )
        # Resolution finalized: earliest of final_resolution_at or resolved_at.
        final_at = self._session.scalar(
            select(func.min(ComplaintResolution.final_resolution_at)).where(
                ComplaintResolution.complaint_id == complaint_id,
                ComplaintResolution.deleted_at.is_(None),
                ComplaintResolution.final_resolution_at.is_not(None),
            )
        )
        resolved_at = self._session.scalar(
            select(func.min(ComplaintResolution.resolved_at)).where(
                ComplaintResolution.complaint_id == complaint_id,
                ComplaintResolution.deleted_at.is_(None),
                ComplaintResolution.is_current.is_(True),
            )
        )
        resolution_candidates = [t for t in (final_at, resolved_at) if t is not None]
        resolution_completed_at = (
            min(resolution_candidates) if resolution_candidates else None
        )

        escalation_completed_at = self._session.scalar(
            select(func.min(ComplaintEscalation.closed_at)).where(
                ComplaintEscalation.complaint_id == complaint_id,
                ComplaintEscalation.deleted_at.is_(None),
                ComplaintEscalation.closed_at.is_not(None),
                ComplaintEscalation.status == EscalationRequestStatus.CLOSED,
            )
        )

        complaint = self.get_complaint(complaint_id)
        overall_completed_at = (
            complaint.closed_at if complaint is not None else None
        )

        return SlaCompletionFacts(
            assignment_completed_at=assignment_completed_at,
            appointment_completed_at=appointment_completed_at,
            resolution_completed_at=resolution_completed_at,
            escalation_completed_at=escalation_completed_at,
            overall_completed_at=overall_completed_at,
        )

    def update_statuses(
        self,
        row: SlaRecord,
        *,
        assignment_status: SlaStatus,
        appointment_status: SlaStatus,
        resolution_status: SlaStatus,
        escalation_status: SlaStatus,
        overall_status: SlaStatus,
        now: datetime | None = None,
    ) -> SlaRecord:
        """Update status columns only — never touches *_due_at."""
        when = now or datetime.now(UTC)
        if when.tzinfo is None:
            when = when.replace(tzinfo=UTC)
        row.assignment_status = assignment_status
        row.appointment_status = appointment_status
        row.resolution_status = resolution_status
        row.escalation_status = escalation_status
        row.overall_status = overall_status
        row.updated_at = when
        self._session.flush()
        return row

    def add_timeline(
        self,
        *,
        complaint_id: uuid.UUID,
        event_type: str,
        event_at: datetime,
        summary: str,
        metadata: dict[str, Any] | None = None,
    ) -> ComplaintTimeline:
        """Append SYSTEM-actor SLA timeline entry (TASK-025)."""
        when = event_at if event_at.tzinfo else event_at.replace(tzinfo=UTC)
        entry = ComplaintTimeline(
            complaint_id=complaint_id,
            actor_user_id=None,
            event_type=event_type,
            event_at=when,
            from_status=None,
            to_status=None,
            summary=summary,
            metadata_json=metadata,
            created_at=when,
            updated_at=when,
            created_by=None,
            updated_by=None,
        )
        self._session.add(entry)
        self._session.flush()
        return entry

    def create_pending(
        self,
        complaint_id: uuid.UUID,
        *,
        now: datetime | None = None,
    ) -> SlaRecord:
        """Create foundation SLA row (all statuses PENDING, deadlines NULL).

        Prefer ``create_with_deadlines`` for new complaints (TASK-023).
        """
        when = now or datetime.now(UTC)
        if when.tzinfo is None:
            when = when.replace(tzinfo=UTC)
        row = SlaRecord(
            complaint_id=complaint_id,
            assignment_due_at=None,
            resolution_due_at=None,
            appointment_due_at=None,
            escalation_due_at=None,
            overall_due_at=None,
            assignment_status=SlaStatus.PENDING,
            resolution_status=SlaStatus.PENDING,
            appointment_status=SlaStatus.PENDING,
            escalation_status=SlaStatus.PENDING,
            overall_status=SlaStatus.PENDING,
            created_at=when,
            updated_at=when,
        )
        self._session.add(row)
        self._session.flush()
        return row

    def create_with_deadlines(
        self,
        complaint_id: uuid.UUID,
        *,
        created_at: datetime,
        assignment_due_at: datetime,
        appointment_due_at: datetime,
        resolution_due_at: datetime,
        escalation_due_at: datetime,
        overall_due_at: datetime,
    ) -> SlaRecord:
        """Persist immutable SLA deadline snapshot (TASK-023 / DEC-012)."""
        when = created_at
        if when.tzinfo is None:
            when = when.replace(tzinfo=UTC)
        row = SlaRecord(
            complaint_id=complaint_id,
            assignment_due_at=assignment_due_at,
            resolution_due_at=resolution_due_at,
            appointment_due_at=appointment_due_at,
            escalation_due_at=escalation_due_at,
            overall_due_at=overall_due_at,
            assignment_status=SlaStatus.PENDING,
            resolution_status=SlaStatus.PENDING,
            appointment_status=SlaStatus.PENDING,
            escalation_status=SlaStatus.PENDING,
            overall_status=SlaStatus.PENDING,
            created_at=when,
            updated_at=when,
        )
        self._session.add(row)
        self._session.flush()
        return row

    # --- SLA policies (TASK-022) ---

    def list_policies(self) -> list[SlaPolicy]:
        stmt = select(SlaPolicy).order_by(
            SlaPolicy.is_active.desc(),
            SlaPolicy.created_at.desc(),
        )
        return list(self._session.scalars(stmt).all())

    def get_policy(self, policy_id: uuid.UUID) -> SlaPolicy | None:
        stmt = select(SlaPolicy).where(SlaPolicy.id == policy_id)
        return self._session.scalar(stmt)

    def get_active_policy(self) -> SlaPolicy | None:
        stmt = select(SlaPolicy).where(SlaPolicy.is_active.is_(True))
        return self._session.scalar(stmt)

    def create_policy(
        self,
        *,
        name: str,
        description: str | None,
        assignment_target_minutes: int,
        appointment_target_minutes: int,
        resolution_target_minutes: int,
        escalation_target_minutes: int,
        overall_target_minutes: int,
        is_active: bool,
        now: datetime | None = None,
    ) -> SlaPolicy:
        when = now or datetime.now(UTC)
        if when.tzinfo is None:
            when = when.replace(tzinfo=UTC)
        row = SlaPolicy(
            name=name,
            description=description,
            assignment_target_minutes=assignment_target_minutes,
            appointment_target_minutes=appointment_target_minutes,
            resolution_target_minutes=resolution_target_minutes,
            escalation_target_minutes=escalation_target_minutes,
            overall_target_minutes=overall_target_minutes,
            is_active=is_active,
            created_at=when,
            updated_at=when,
        )
        self._session.add(row)
        self._session.flush()
        return row

    def deactivate_all_policies(self, *, now: datetime | None = None) -> None:
        when = now or datetime.now(UTC)
        if when.tzinfo is None:
            when = when.replace(tzinfo=UTC)
        self._session.execute(
            update(SlaPolicy)
            .where(SlaPolicy.is_active.is_(True))
            .values(is_active=False, updated_at=when)
        )

    def set_policy_active(
        self,
        policy: SlaPolicy,
        *,
        is_active: bool,
        now: datetime | None = None,
    ) -> SlaPolicy:
        when = now or datetime.now(UTC)
        if when.tzinfo is None:
            when = when.replace(tzinfo=UTC)
        policy.is_active = is_active
        policy.updated_at = when
        self._session.flush()
        return policy

    def commit(self) -> None:
        self._session.commit()

    def refresh(self, obj: Any) -> Any:
        self._session.refresh(obj)
        return obj
