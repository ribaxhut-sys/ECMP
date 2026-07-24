"""Assignment application service (no FastAPI imports)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.core.enums import ComplaintStatus, TimelineEvent
from app.core.errors import InvalidStateError, NotFoundError, ValidationAppError
from app.models import ComplaintAssignment
from app.modules.assignments.repository import AssignmentRepository
from app.modules.assignments.schemas import (
    AssignComplaintRequest,
    AssignComplaintResult,
    AssignmentResponse,
)

ASSIGNABLE_STATUSES = frozenset(
    {ComplaintStatus.NEW, ComplaintStatus.ASSIGNED}
)
TARGET_STATUS = ComplaintStatus.ASSIGNED


def _to_response(assignment: ComplaintAssignment) -> AssignmentResponse:
    reason = None
    notes = assignment.notes
    # Convention: reassignment reason stored as notes; expose both for API clarity.
    if notes and notes.startswith("REASSIGN:"):
        reason = notes.removeprefix("REASSIGN:").strip() or None
    assignee = assignment.__dict__.get("assignee")
    assignee_name = getattr(assignee, "full_name", None) if assignee is not None else None
    return AssignmentResponse(
        id=assignment.id,
        complaintId=assignment.complaint_id,
        assigneeId=assignment.assignee_id,
        assigneeName=assignee_name,
        assignedBy=assignment.assigned_by,
        assignedAt=assignment.assigned_at,
        unassignedAt=assignment.unassigned_at,
        isCurrent=assignment.is_current,
        notes=None if reason else notes,
        reason=reason,
    )


def _compose_notes(*, reason: str | None, notes: str | None, reassigned: bool) -> str | None:
    if reassigned and reason:
        prefix = f"REASSIGN: {reason}"
        if notes:
            return f"{prefix} | {notes}"
        return prefix
    return notes


class AssignmentService:
    def __init__(self, repository: AssignmentRepository) -> None:
        self._repo = repository

    def assign(
        self,
        complaint_id: uuid.UUID,
        payload: AssignComplaintRequest,
        *,
        actor_user_id: uuid.UUID,
    ) -> AssignComplaintResult:
        complaint = self._repo.get_complaint(complaint_id)
        if complaint is None:
            raise NotFoundError("Complaint not found")

        if complaint.status not in ASSIGNABLE_STATUSES:
            raise InvalidStateError(
                "Complaint cannot be assigned in its current status",
                details={"status": complaint.status},
            )

        if not self._repo.user_exists(payload.assignee_id):
            raise ValidationAppError(
                "Assignee not found or inactive",
                details={"assigneeId": str(payload.assignee_id)},
            )

        current = self._repo.get_current_assignment(complaint_id)
        reassigned = (
            current is not None or complaint.status == ComplaintStatus.ASSIGNED
        )

        if reassigned:
            reason = (payload.reason or "").strip() if payload.reason else ""
            if not reason:
                raise ValidationAppError(
                    "reason is required for reassignment",
                    details={"reason": "mandatory when reassigning"},
                )

        now = datetime.now(UTC)
        from_status = complaint.status

        if current is not None:
            # Preserve history — close current row, never delete.
            self._repo.close_assignment(
                current,
                unassigned_at=now,
                actor_user_id=actor_user_id,
            )

        assignment = ComplaintAssignment(
            complaint_id=complaint.id,
            assignee_id=payload.assignee_id,
            assigned_by=actor_user_id,
            assigned_at=now,
            unassigned_at=None,
            is_current=True,
            notes=_compose_notes(
                reason=payload.reason,
                notes=payload.notes,
                reassigned=reassigned,
            ),
            created_at=now,
            updated_at=now,
            created_by=actor_user_id,
            updated_by=actor_user_id,
        )
        self._repo.add_assignment(assignment)

        complaint.status = TARGET_STATUS
        complaint.updated_at = now
        complaint.updated_by = actor_user_id

        event_type = (
            TimelineEvent.REASSIGNED if reassigned else TimelineEvent.ASSIGNED
        )
        assignee_name = self._repo.get_user_full_name(payload.assignee_id) or str(
            payload.assignee_id
        )
        summary = (
            f"Reassigned to {assignee_name}"
            if reassigned
            else f"Assigned to {assignee_name}"
        )
        self._repo.add_timeline(
            complaint_id=complaint.id,
            actor_user_id=actor_user_id,
            event_type=event_type,
            event_at=now,
            from_status=from_status,
            to_status=TARGET_STATUS,
            summary=summary,
            metadata={
                "assigneeId": str(payload.assignee_id),
                "assigneeName": assignee_name,
                "assignedBy": str(actor_user_id),
                "reassigned": reassigned,
                "reason": payload.reason,
                "changeType": "STATUS_CHANGED" if from_status != TARGET_STATUS else None,
            },
        )

        # TASK-024 — evaluate assignment (and other) SLA statuses.
        from app.modules.sla.hooks import evaluate_sla_for_complaint

        evaluate_sla_for_complaint(self._repo.session, complaint.id, now=now)

        self._repo.commit()
        self._repo.refresh(assignment)
        self._repo.refresh(complaint)

        return AssignComplaintResult(
            assignment=_to_response(assignment),
            complaintId=complaint.id,
            status=ComplaintStatus(complaint.status),
            reassigned=reassigned,
        )

    def list_assignments(self, complaint_id: uuid.UUID) -> list[AssignmentResponse]:
        complaint = self._repo.get_complaint(complaint_id)
        if complaint is None:
            raise NotFoundError("Complaint not found")
        rows = self._repo.list_assignments(complaint_id)
        return [_to_response(row) for row in rows]
