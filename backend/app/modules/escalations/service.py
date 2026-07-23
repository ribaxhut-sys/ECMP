"""Escalation application service (no FastAPI imports)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.core.enums import (
    ComplaintStatus,
    EscalationRequestStatus,
    TimelineEvent,
)
from app.core.errors import InvalidStateError, NotFoundError, ValidationAppError
from app.models import ComplaintEscalation
from app.modules.escalations.repository import EscalationRepository
from app.modules.escalations.schemas import (
    EscalateComplaintRequest,
    EscalateComplaintResult,
    EscalationRequestCreate,
    EscalationRequestResult,
    EscalationResponse,
    EscalationReviewRequest,
    EscalationReviewResult,
)

ALLOWED_STATUSES = frozenset(
    {ComplaintStatus.ASSIGNED, ComplaintStatus.IN_PROGRESS}
)
REJECTED_STATUSES: dict[str, str] = {
    ComplaintStatus.NEW: "NEW complaints cannot be escalated",
    ComplaintStatus.RESOLVED: "RESOLVED complaints cannot be escalated",
    ComplaintStatus.CLOSED: "CLOSED complaints cannot be escalated",
}
TARGET_STATUS = ComplaintStatus.ESCALATED
ESCALATION_RECORD_STATUS = "OPEN"

NOT_IN_PROGRESS_MESSAGE = (
    "Complaint must be IN_PROGRESS before requesting escalation."
)
HAS_RESOLUTION_MESSAGE = (
    "Complaint already has a resolution and cannot be escalated."
)
HAS_ACTIVE_ESCALATION_MESSAGE = "Complaint already has an active escalation."
NOT_REQUESTED_MESSAGE = "Only REQUESTED escalations can be reviewed."
ALREADY_REVIEWED_MESSAGE = "Escalation has already been reviewed."


def _to_response(row: ComplaintEscalation) -> EscalationResponse:
    requester = row.__dict__.get("requester")
    requested_by_name = (
        getattr(requester, "full_name", None) if requester is not None else None
    )
    reviewer = row.__dict__.get("reviewer")
    reviewed_by_name = (
        getattr(reviewer, "full_name", None) if reviewer is not None else None
    )
    data = EscalationResponse.model_validate(row)
    return data.model_copy(
        update={
            "requested_by_name": requested_by_name,
            "reviewed_by_name": reviewed_by_name,
        }
    )


class EscalationService:
    def __init__(self, repository: EscalationRepository) -> None:
        self._repo = repository

    def escalate(
        self,
        complaint_id: uuid.UUID,
        payload: EscalateComplaintRequest,
        *,
        actor_user_id: uuid.UUID,
    ) -> EscalateComplaintResult:
        complaint = self._repo.get_complaint(complaint_id)
        if complaint is None:
            raise NotFoundError("Complaint not found")

        status = complaint.status
        if status in REJECTED_STATUSES:
            raise InvalidStateError(
                REJECTED_STATUSES[status],
                details={"status": status},
            )
        if status not in ALLOWED_STATUSES:
            raise InvalidStateError(
                "Complaint cannot be escalated in its current status",
                details={"status": status, "allowed": sorted(ALLOWED_STATUSES)},
            )

        if payload.escalated_to_user_id is not None:
            if not self._repo.user_exists(payload.escalated_to_user_id):
                raise ValidationAppError(
                    "Escalation target user not found or inactive",
                    details={"escalatedToUserId": str(payload.escalated_to_user_id)},
                )
        if payload.escalated_to_role_id is not None:
            if not self._repo.role_exists(payload.escalated_to_role_id):
                raise ValidationAppError(
                    "Escalation target role not found or inactive",
                    details={"escalatedToRoleId": str(payload.escalated_to_role_id)},
                )
        if payload.escalated_from_user_id is not None:
            if not self._repo.user_exists(payload.escalated_from_user_id):
                raise ValidationAppError(
                    "Escalation source user not found or inactive",
                    details={"escalatedFromUserId": str(payload.escalated_from_user_id)},
                )

        from_user_id = (
            payload.escalated_from_user_id
            or self._repo.get_current_assignee_id(complaint_id)
        )

        now = datetime.now(UTC)
        from_status = complaint.status
        level = self._repo.next_level(complaint_id)

        escalation = ComplaintEscalation(
            complaint_id=complaint.id,
            escalated_from_user_id=from_user_id,
            escalated_to_user_id=payload.escalated_to_user_id,
            escalated_to_role_id=payload.escalated_to_role_id,
            reason=payload.reason,
            level=level,
            status=ESCALATION_RECORD_STATUS,
            escalated_at=now,
            resolved_at=None,
            created_at=now,
            updated_at=now,
            created_by=actor_user_id,
            updated_by=actor_user_id,
        )
        self._repo.add_escalation(escalation)

        complaint.status = TARGET_STATUS
        complaint.updated_at = now
        complaint.updated_by = actor_user_id

        self._repo.add_timeline(
            complaint_id=complaint.id,
            actor_user_id=actor_user_id,
            event_type=TimelineEvent.ESCALATED,
            event_at=now,
            from_status=from_status,
            to_status=TARGET_STATUS,
            summary=f"Complaint escalated to level {level}",
            metadata={
                "level": level,
                "reason": payload.reason,
                "escalatedToUserId": (
                    str(payload.escalated_to_user_id)
                    if payload.escalated_to_user_id
                    else None
                ),
                "escalatedToRoleId": (
                    str(payload.escalated_to_role_id)
                    if payload.escalated_to_role_id
                    else None
                ),
                "escalatedFromUserId": str(from_user_id) if from_user_id else None,
                "escalatedBy": str(actor_user_id),
            },
        )

        self._repo.commit()
        self._repo.refresh(escalation)
        self._repo.refresh(complaint)

        return EscalateComplaintResult(
            escalation=_to_response(escalation),
            complaintId=complaint.id,
            status=ComplaintStatus(complaint.status),
        )

    def request_escalation(
        self,
        complaint_id: uuid.UUID,
        payload: EscalationRequestCreate,
        *,
        actor_user_id: uuid.UUID,
    ) -> EscalationRequestResult:
        """API-301 — create Escalation Request (status REQUESTED; no review)."""
        complaint = self._repo.get_complaint(complaint_id)
        if complaint is None:
            raise NotFoundError("Complaint not found")

        if complaint.status != ComplaintStatus.IN_PROGRESS:
            raise ValidationAppError(
                NOT_IN_PROGRESS_MESSAGE,
                details={"status": complaint.status},
            )

        if self._repo.has_current_resolution(complaint_id):
            raise ValidationAppError(
                HAS_RESOLUTION_MESSAGE,
                details={"complaintId": str(complaint_id)},
            )

        active = self._repo.get_active_escalation(complaint_id)
        if active is not None:
            raise ValidationAppError(
                HAS_ACTIVE_ESCALATION_MESSAGE,
                details={
                    "complaintId": str(complaint_id),
                    "escalationId": str(active.id),
                    "status": active.status,
                },
            )

        now = datetime.now(UTC)
        level = self._repo.next_level(complaint_id)

        escalation = ComplaintEscalation(
            complaint_id=complaint.id,
            escalated_from_user_id=actor_user_id,
            escalated_to_user_id=None,
            escalated_to_role_id=None,
            reason=payload.reason_description,
            level=level,
            status=EscalationRequestStatus.REQUESTED,
            escalated_at=now,
            resolved_at=None,
            reason_code=payload.reason_code,
            reason_description=payload.reason_description,
            diagnosis=payload.diagnosis,
            notes=payload.notes,
            requested_by=actor_user_id,
            requested_at=now,
            created_at=now,
            updated_at=now,
            created_by=actor_user_id,
            updated_by=actor_user_id,
        )
        self._repo.add_escalation(escalation)

        # Complaint remains IN_PROGRESS — Review is TASK-012.
        complaint.updated_at = now
        complaint.updated_by = actor_user_id

        self._repo.add_timeline(
            complaint_id=complaint.id,
            actor_user_id=actor_user_id,
            event_type=TimelineEvent.ESCALATION_REQUESTED,
            event_at=now,
            from_status=complaint.status,
            to_status=complaint.status,
            summary="Escalation requested",
            metadata={
                "changeType": "ESCALATION_REQUESTED",
                "escalationId": str(escalation.id),
                "reasonCode": payload.reason_code,
                "reasonDescription": payload.reason_description,
                "requestedBy": str(actor_user_id),
            },
        )

        result = EscalationRequestResult(
            id=escalation.id,
            complaintId=complaint.id,
            status=EscalationRequestStatus.REQUESTED,
            requestedBy=actor_user_id,
            requestedAt=now,
        )
        self._repo.commit()
        return result

    def _review(
        self,
        escalation_id: uuid.UUID,
        payload: EscalationReviewRequest,
        *,
        actor_user_id: uuid.UUID,
        target_status: EscalationRequestStatus,
        event_type: TimelineEvent,
        summary: str,
        change_type: str,
    ) -> EscalationReviewResult:
        row = self._repo.get_by_id(escalation_id)
        if row is None:
            raise NotFoundError("Escalation not found")

        if row.status in {
            EscalationRequestStatus.APPROVED,
            EscalationRequestStatus.REJECTED,
        }:
            raise ValidationAppError(
                ALREADY_REVIEWED_MESSAGE,
                details={"status": row.status},
            )
        if row.status != EscalationRequestStatus.REQUESTED:
            raise ValidationAppError(
                NOT_REQUESTED_MESSAGE,
                details={"status": row.status},
            )

        complaint = self._repo.get_complaint(row.complaint_id)
        if complaint is None:
            raise NotFoundError("Complaint not found")

        now = datetime.now(UTC)
        row.status = target_status
        row.reviewed_by = actor_user_id
        row.reviewed_at = now
        row.review_notes = payload.review_notes
        row.updated_at = now
        row.updated_by = actor_user_id

        # Complaint remains IN_PROGRESS — no Appointment (TASK-012 STOP).
        complaint.updated_at = now
        complaint.updated_by = actor_user_id

        self._repo.add_timeline(
            complaint_id=complaint.id,
            actor_user_id=actor_user_id,
            event_type=event_type,
            event_at=now,
            from_status=complaint.status,
            to_status=complaint.status,
            summary=summary,
            metadata={
                "changeType": change_type,
                "escalationId": str(row.id),
                "status": target_status.value,
                "reviewNotes": payload.review_notes,
                "reviewedBy": str(actor_user_id),
            },
        )

        result = EscalationReviewResult(
            id=row.id,
            status=target_status,
            reviewedBy=actor_user_id,
            reviewedAt=now,
        )
        self._repo.commit()
        return result

    def approve(
        self,
        escalation_id: uuid.UUID,
        payload: EscalationReviewRequest,
        *,
        actor_user_id: uuid.UUID,
    ) -> EscalationReviewResult:
        """API-303 — approve REQUESTED escalation."""
        return self._review(
            escalation_id,
            payload,
            actor_user_id=actor_user_id,
            target_status=EscalationRequestStatus.APPROVED,
            event_type=TimelineEvent.ESCALATION_APPROVED,
            summary="Escalation approved",
            change_type="ESCALATION_APPROVED",
        )

    def reject(
        self,
        escalation_id: uuid.UUID,
        payload: EscalationReviewRequest,
        *,
        actor_user_id: uuid.UUID,
    ) -> EscalationReviewResult:
        """API-304 — reject REQUESTED escalation."""
        return self._review(
            escalation_id,
            payload,
            actor_user_id=actor_user_id,
            target_status=EscalationRequestStatus.REJECTED,
            event_type=TimelineEvent.ESCALATION_REJECTED,
            summary="Escalation rejected",
            change_type="ESCALATION_REJECTED",
        )

    def get_escalation(self, escalation_id: uuid.UUID) -> EscalationResponse:
        """API-302 — get escalation by id."""
        row = self._repo.get_by_id(escalation_id)
        if row is None:
            raise NotFoundError("Escalation not found")
        return _to_response(row)

    def get_active_for_complaint(
        self, complaint_id: uuid.UUID
    ) -> EscalationResponse | None:
        complaint = self._repo.get_complaint(complaint_id)
        if complaint is None:
            raise NotFoundError("Complaint not found")
        active = self._repo.get_active_escalation(complaint_id)
        if active is None:
            return None
        return _to_response(active)

    def get_latest_request_for_complaint(
        self, complaint_id: uuid.UUID
    ) -> EscalationResponse | None:
        complaint = self._repo.get_complaint(complaint_id)
        if complaint is None:
            raise NotFoundError("Complaint not found")
        latest = self._repo.get_latest_request_escalation(complaint_id)
        if latest is None:
            return None
        return _to_response(latest)

    def list_escalations(self, complaint_id: uuid.UUID) -> list[EscalationResponse]:
        complaint = self._repo.get_complaint(complaint_id)
        if complaint is None:
            raise NotFoundError("Complaint not found")
        return [_to_response(row) for row in self._repo.list_escalations(complaint_id)]
