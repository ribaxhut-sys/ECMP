"""Escalation application service (no FastAPI imports)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.core.enums import ComplaintStatus, TimelineEvent
from app.core.errors import InvalidStateError, NotFoundError, ValidationAppError
from app.models import ComplaintEscalation
from app.modules.escalations.repository import EscalationRepository
from app.modules.escalations.schemas import (
    EscalateComplaintRequest,
    EscalateComplaintResult,
    EscalationResponse,
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


def _to_response(row: ComplaintEscalation) -> EscalationResponse:
    return EscalationResponse.model_validate(row)


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

    def list_escalations(self, complaint_id: uuid.UUID) -> list[EscalationResponse]:
        complaint = self._repo.get_complaint(complaint_id)
        if complaint is None:
            raise NotFoundError("Complaint not found")
        return [_to_response(row) for row in self._repo.list_escalations(complaint_id)]
