"""Complaint Context Foundation (TASK-044).

Assembles an immutable operational read model for one Complaint from
existing data. Does not persist, cache, or mutate aggregates.
"""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.enums import ComplaintSourceType, ComplaintTargetType
from app.core.errors import NotFoundError, ValidationAppError
from app.models import Complaint, ComplaintAssignment, SlaRecord
from app.modules.assignments.repository import AssignmentRepository
from app.modules.complaint_context.models import (
    AssigneeRef,
    AssignmentSnapshot,
    ComplaintContext,
    ComplaintSnapshot,
    SlaSnapshot,
    SourceRef,
    TargetRef,
)
from app.modules.complaints.repository import ComplaintRepository
from app.modules.routing import ComplaintRoute, ComplaintRoutingService
from app.modules.sla.repository import SlaRepository


def _complaint_snapshot(complaint: Complaint) -> ComplaintSnapshot:
    return ComplaintSnapshot(
        id=complaint.id,
        complaint_number=complaint.complaint_number,
        subject=complaint.subject,
        description=complaint.description,
        channel=complaint.channel,
        category=complaint.category,
        reported_at=complaint.reported_at,
        customer_id=complaint.customer_id,
        branch_id=complaint.branch_id,
    )


def _assignment_snapshot(
    assignment: ComplaintAssignment,
) -> AssignmentSnapshot:
    assignee = assignment.__dict__.get("assignee")
    assignee_name = (
        getattr(assignee, "full_name", None) if assignee is not None else None
    )
    return AssignmentSnapshot(
        id=assignment.id,
        assignee_id=assignment.assignee_id,
        assignee_name=assignee_name,
        assigned_by=assignment.assigned_by,
        assigned_at=assignment.assigned_at,
        is_current=assignment.is_current,
        notes=assignment.notes,
    )


def _assignee_ref(assignment: ComplaintAssignment) -> AssigneeRef:
    assignee = assignment.__dict__.get("assignee")
    full_name = (
        getattr(assignee, "full_name", None) if assignee is not None else None
    )
    return AssigneeRef(user_id=assignment.assignee_id, full_name=full_name)


def _sla_snapshot(row: SlaRecord) -> SlaSnapshot:
    return SlaSnapshot(
        id=row.id,
        overall_status=row.overall_status,
        overall_due_at=row.overall_due_at,
        assignment_status=row.assignment_status,
        assignment_due_at=row.assignment_due_at,
        resolution_status=row.resolution_status,
        resolution_due_at=row.resolution_due_at,
        appointment_status=row.appointment_status,
        appointment_due_at=row.appointment_due_at,
        escalation_status=row.escalation_status,
        escalation_due_at=row.escalation_due_at,
    )


def _resolve_routing(
    complaint: Complaint,
    routing: ComplaintRoutingService,
) -> ComplaintRoute:
    """Derive current route from persisted source/target (read-only)."""
    try:
        source_type = ComplaintSourceType(complaint.source_type)
    except ValueError as exc:
        raise ValidationAppError(
            "Complaint has an unsupported sourceType",
            details={"sourceType": complaint.source_type},
        ) from exc
    try:
        target_type = ComplaintTargetType(complaint.target_type)
    except ValueError as exc:
        raise ValidationAppError(
            "Complaint has an unsupported targetType",
            details={"targetType": complaint.target_type},
        ) from exc

    return routing.resolve_route(
        source_type=source_type,
        source_id=complaint.source_id,
        target_type=target_type,
        target_id=complaint.target_id,
    )


class ComplaintContextService:
    """Build / refresh ComplaintContext from live operational data."""

    def __init__(
        self,
        session: Session,
        *,
        routing_service: ComplaintRoutingService | None = None,
        complaint_repository: ComplaintRepository | None = None,
        assignment_repository: AssignmentRepository | None = None,
        sla_repository: SlaRepository | None = None,
    ) -> None:
        self._session = session
        self._routing = routing_service or ComplaintRoutingService()
        self._complaints = complaint_repository or ComplaintRepository(session)
        self._assignments = assignment_repository or AssignmentRepository(
            session
        )
        self._sla = sla_repository or SlaRepository(session)

    def build_context(self, complaint_id: uuid.UUID) -> ComplaintContext:
        """Assemble an immutable operational context for ``complaint_id``."""
        complaint = self._complaints.get_by_id(complaint_id)
        if complaint is None:
            raise NotFoundError("Complaint not found")

        assignment = self._assignments.get_current_assignment(complaint_id)
        sla_row = self._sla.get_by_complaint_id(complaint_id)
        route = _resolve_routing(complaint, self._routing)

        return ComplaintContext(
            complaint=_complaint_snapshot(complaint),
            current_assignment=(
                _assignment_snapshot(assignment)
                if assignment is not None
                else None
            ),
            current_status=complaint.status,
            current_sla=_sla_snapshot(sla_row) if sla_row is not None else None,
            priority=complaint.priority,
            source=SourceRef(
                source_type=complaint.source_type,
                source_id=complaint.source_id,
            ),
            target=TargetRef(
                target_type=complaint.target_type,
                target_id=complaint.target_id,
            ),
            routing=route,
            current_assignee=(
                _assignee_ref(assignment) if assignment is not None else None
            ),
            created_at=complaint.created_at,
            updated_at=complaint.updated_at,
        )

    def refresh_context(self, complaint_id: uuid.UUID) -> ComplaintContext:
        """Re-assemble context from current data (no cache — alias of build)."""
        return self.build_context(complaint_id)
