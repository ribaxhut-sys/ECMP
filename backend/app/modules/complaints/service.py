"""Complaint application service (no FastAPI imports)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from app.core.enums import INITIAL_COMPLAINT_STATUS, ComplaintStatus, TimelineEvent
from app.core.errors import NotFoundError, ValidationAppError
from app.core.status_transitions import can_transition
from app.models import Complaint
from app.modules.complaints.repository import ComplaintRepository
from app.modules.complaints.schemas import (
    CloseComplaintRequest,
    CloseComplaintResult,
    ComplaintCreateRequest,
    ComplaintResponse,
    ComplaintStatusChangeRequest,
    ComplaintUpdateRequest,
)

CLOSABLE_STATUS = ComplaintStatus.IN_PROGRESS
TARGET_CLOSED_STATUS = ComplaintStatus.CLOSED
NOT_IN_PROGRESS_FOR_CLOSE_MESSAGE = (
    "Complaint must be IN_PROGRESS before closing."
)
ALREADY_CLOSED_MESSAGE = "Complaint is already CLOSED."
FINAL_RESOLUTION_REQUIRED_MESSAGE = (
    "Final Resolution must exist before closing the complaint."
)
ESCALATION_REQUIRED_MESSAGE = (
    "Escalation must exist before closing the complaint."
)


def _generate_complaint_number() -> str:
    return f"CMP-{uuid.uuid4().hex[:10].upper()}"


def _to_response(complaint: Complaint) -> ComplaintResponse:
    return ComplaintResponse.model_validate(complaint)


def _snapshot(complaint: Complaint) -> dict[str, Any]:
    return {
        "id": str(complaint.id),
        "complaintNumber": complaint.complaint_number,
        "customerId": str(complaint.customer_id),
        "branchId": str(complaint.branch_id) if complaint.branch_id else None,
        "subject": complaint.subject,
        "description": complaint.description,
        "status": complaint.status,
        "priority": complaint.priority,
        "channel": complaint.channel,
        "category": complaint.category,
        "reportedAt": complaint.reported_at.isoformat(),
        "closedAt": complaint.closed_at.isoformat() if complaint.closed_at else None,
        "closedBy": str(complaint.closed_by) if complaint.closed_by else None,
        "closureNotes": complaint.closure_notes,
        "createdAt": complaint.created_at.isoformat() if complaint.created_at else None,
        "createdBy": str(complaint.created_by) if complaint.created_by else None,
        "updatedAt": complaint.updated_at.isoformat() if complaint.updated_at else None,
        "updatedBy": str(complaint.updated_by) if complaint.updated_by else None,
    }


class ComplaintService:
    def __init__(self, repository: ComplaintRepository) -> None:
        self._repo = repository

    def create(
        self,
        payload: ComplaintCreateRequest,
        *,
        actor_user_id: uuid.UUID,
    ) -> ComplaintResponse:
        if not self._repo.customer_exists(payload.customer_id):
            raise ValidationAppError(
                "Customer not found",
                details={"customerId": str(payload.customer_id)},
            )
        if payload.branch_id is not None and not self._repo.branch_exists(payload.branch_id):
            raise ValidationAppError(
                "Branch not found",
                details={"branchId": str(payload.branch_id)},
            )

        now = datetime.now(UTC)
        reported_at = payload.reported_at or now
        if reported_at.tzinfo is None:
            reported_at = reported_at.replace(tzinfo=UTC)

        complaint = Complaint(
            complaint_number=_generate_complaint_number(),
            customer_id=payload.customer_id,
            branch_id=payload.branch_id,
            subject=payload.subject,
            description=payload.description,
            status=INITIAL_COMPLAINT_STATUS,
            priority=payload.priority,
            channel=payload.channel,
            category=payload.category,
            reported_at=reported_at,
            created_at=now,
            updated_at=now,
            created_by=actor_user_id,
            updated_by=actor_user_id,
        )
        self._repo.add(complaint)
        self._repo.add_audit_log(
            actor_user_id=actor_user_id,
            action="complaint.create",
            entity_id=complaint.id,
            new_value=_snapshot(complaint),
            occurred_at=now,
        )
        self._repo.add_timeline(
            complaint_id=complaint.id,
            actor_user_id=actor_user_id,
            event_type=TimelineEvent.CREATED,
            event_at=now,
            from_status=None,
            to_status=INITIAL_COMPLAINT_STATUS,
            summary="Complaint created",
            metadata={"complaintNumber": complaint.complaint_number},
        )
        self._repo.commit()
        self._repo.refresh(complaint)
        return _to_response(complaint)

    def get(self, complaint_id: uuid.UUID) -> ComplaintResponse:
        complaint = self._repo.get_by_id(complaint_id)
        if complaint is None:
            raise NotFoundError("Complaint not found")
        return _to_response(complaint)

    def list(
        self,
        *,
        page: int,
        page_size: int,
        status: str | None = None,
        priority: str | None = None,
        customer_id: uuid.UUID | None = None,
        branch_id: uuid.UUID | None = None,
    ) -> tuple[list[ComplaintResponse], int]:
        if page < 1:
            raise ValidationAppError("page must be >= 1", details={"page": page})
        if page_size < 1 or page_size > 100:
            raise ValidationAppError(
                "pageSize must be between 1 and 100",
                details={"pageSize": page_size},
            )

        items, total = self._repo.list_page(
            page=page,
            page_size=page_size,
            status=status,
            priority=priority,
            customer_id=customer_id,
            branch_id=branch_id,
        )
        return [_to_response(item) for item in items], total

    def update(
        self,
        complaint_id: uuid.UUID,
        payload: ComplaintUpdateRequest,
        *,
        actor_user_id: uuid.UUID,
    ) -> ComplaintResponse:
        complaint = self._repo.get_by_id(complaint_id)
        if complaint is None:
            raise NotFoundError("Complaint not found")

        changes = payload.model_dump(exclude_unset=True)
        if "branch_id" in changes and changes["branch_id"] is not None:
            if not self._repo.branch_exists(changes["branch_id"]):
                raise ValidationAppError(
                    "Branch not found",
                    details={"branchId": str(changes["branch_id"])},
                )

        old_value = _snapshot(complaint)
        old_priority = complaint.priority
        now = datetime.now(UTC)

        for field_name, value in changes.items():
            setattr(complaint, field_name, value)

        complaint.updated_at = now
        complaint.updated_by = actor_user_id

        self._repo.add_audit_log(
            actor_user_id=actor_user_id,
            action="complaint.update",
            entity_id=complaint.id,
            old_value=old_value,
            new_value=_snapshot(complaint),
            occurred_at=now,
        )

        # Priority change is a first-class timeline activity (TASK-008).
        if "priority" in changes and changes["priority"] != old_priority:
            self._repo.add_timeline(
                complaint_id=complaint.id,
                actor_user_id=actor_user_id,
                event_type=TimelineEvent.UPDATED,
                event_at=now,
                from_status=complaint.status,
                to_status=complaint.status,
                summary=f"Priority changed from {old_priority} to {complaint.priority}",
                metadata={
                    "changeType": "PRIORITY_CHANGED",
                    "fromPriority": old_priority,
                    "toPriority": complaint.priority,
                },
            )

        self._repo.commit()
        self._repo.refresh(complaint)
        return _to_response(complaint)

    def change_status(
        self,
        complaint_id: uuid.UUID,
        payload: ComplaintStatusChangeRequest,
        *,
        actor_user_id: uuid.UUID,
    ) -> ComplaintResponse:
        """Validated lifecycle transition — sole path for non-assign status changes."""
        complaint = self._repo.get_by_id(complaint_id)
        if complaint is None:
            raise NotFoundError("Complaint not found")

        try:
            current = ComplaintStatus(complaint.status)
        except ValueError as exc:
            raise ValidationAppError(
                "Complaint has an unsupported status",
                details={"status": complaint.status},
            ) from exc

        target = payload.status
        if current == target:
            raise ValidationAppError(
                "Invalid status transition.",
                details={
                    "fromStatus": current.value,
                    "toStatus": target.value,
                    "reason": "status unchanged",
                },
            )

        if not can_transition(current, target):
            raise ValidationAppError(
                "Invalid status transition.",
                details={
                    "fromStatus": current.value,
                    "toStatus": target.value,
                },
            )

        old_value = _snapshot(complaint)
        now = datetime.now(UTC)
        complaint.status = target
        complaint.updated_at = now
        complaint.updated_by = actor_user_id

        if target == ComplaintStatus.CLOSED:
            complaint.closed_at = now
            complaint.closed_by = actor_user_id
        elif target != ComplaintStatus.CLOSED:
            # Leaving RESOLVED/CLOSED (reopen) clears closure timestamp.
            if current in {ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED}:
                complaint.closed_at = None
                complaint.closed_by = None
                complaint.closure_notes = None

        if target == ComplaintStatus.RESOLVED:
            event_type: TimelineEvent = TimelineEvent.RESOLVED
        elif target == ComplaintStatus.CLOSED:
            event_type = TimelineEvent.CLOSED
        else:
            event_type = TimelineEvent.UPDATED

        summary = f"Status changed from {current.value} to {target.value}"
        self._repo.add_audit_log(
            actor_user_id=actor_user_id,
            action="complaint.status_change",
            entity_id=complaint.id,
            old_value=old_value,
            new_value=_snapshot(complaint),
            occurred_at=now,
        )
        self._repo.add_timeline(
            complaint_id=complaint.id,
            actor_user_id=actor_user_id,
            event_type=event_type,
            event_at=now,
            from_status=current.value,
            to_status=target.value,
            summary=summary,
            metadata={
                "changeType": "STATUS_CHANGED",
                "fromStatus": current.value,
                "toStatus": target.value,
                "reason": payload.reason,
            },
        )
        self._repo.commit()
        self._repo.refresh(complaint)
        return _to_response(complaint)

    def close(
        self,
        complaint_id: uuid.UUID,
        payload: CloseComplaintRequest,
        *,
        actor_user_id: uuid.UUID,
    ) -> CloseComplaintResult:
        """API-312 — Explicit Complaint Closure after Final Resolution (TASK-019)."""
        complaint = self._repo.get_by_id(complaint_id)
        if complaint is None:
            raise NotFoundError("Complaint not found")

        if complaint.status == ComplaintStatus.CLOSED or complaint.closed_at is not None:
            raise ValidationAppError(
                ALREADY_CLOSED_MESSAGE,
                details={"status": complaint.status},
            )

        if complaint.status != CLOSABLE_STATUS:
            raise ValidationAppError(
                NOT_IN_PROGRESS_FOR_CLOSE_MESSAGE,
                details={"status": complaint.status},
            )

        final_resolution = self._repo.get_final_resolution(complaint_id)
        if final_resolution is None:
            raise ValidationAppError(
                FINAL_RESOLUTION_REQUIRED_MESSAGE,
                details={"complaintId": str(complaint_id)},
            )

        escalation = self._repo.get_latest_escalation(complaint_id)
        if escalation is None:
            raise ValidationAppError(
                ESCALATION_REQUIRED_MESSAGE,
                details={"complaintId": str(complaint_id)},
            )

        closer = self._repo.get_user(actor_user_id)
        if closer is None:
            raise ValidationAppError(
                "Closer not found or inactive",
                details={"closedBy": str(actor_user_id)},
            )

        from_status = complaint.status
        escalation_status_before = escalation.status
        now = datetime.now(UTC)

        complaint.status = TARGET_CLOSED_STATUS
        complaint.closed_at = now
        complaint.closed_by = actor_user_id
        complaint.closure_notes = payload.notes
        complaint.updated_at = now
        complaint.updated_by = actor_user_id

        # Escalation remains as-is — do NOT close escalation.
        escalation.updated_at = now
        escalation.updated_by = actor_user_id

        self._repo.add_audit_log(
            actor_user_id=actor_user_id,
            action="complaint.close",
            entity_id=complaint.id,
            new_value={
                "complaintId": str(complaint.id),
                "status": TARGET_CLOSED_STATUS.value,
                "closedAt": now.isoformat(),
                "closedBy": str(actor_user_id),
                "closureNotes": payload.notes,
                "escalationId": str(escalation.id),
                "escalationStatus": escalation.status,
            },
            occurred_at=now,
        )
        self._repo.add_timeline(
            complaint_id=complaint.id,
            actor_user_id=actor_user_id,
            event_type=TimelineEvent.CLOSED,
            event_at=now,
            from_status=from_status,
            to_status=TARGET_CLOSED_STATUS.value,
            summary="Complaint closed",
            metadata={
                "changeType": "COMPLAINT_CLOSED",
                "complaintId": str(complaint.id),
                "escalationId": str(escalation.id),
                "closedBy": str(actor_user_id),
                "closedAt": now.isoformat(),
            },
        )

        assert complaint.status == ComplaintStatus.CLOSED
        assert escalation.status == escalation_status_before

        result = CloseComplaintResult(
            complaintId=complaint.id,
            status=TARGET_CLOSED_STATUS,
            closedAt=now,
            closedBy=actor_user_id,
        )
        self._repo.commit()
        return result
