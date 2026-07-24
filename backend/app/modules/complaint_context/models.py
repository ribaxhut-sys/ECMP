"""Complaint Context read-model value objects (TASK-044).

Immutable snapshots assembled from existing aggregates. Not persisted.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Mapping

from app.modules.routing import ComplaintRoute


@dataclass(frozen=True, slots=True)
class ComplaintSnapshot:
    """Minimal immutable view of the Complaint aggregate header."""

    id: uuid.UUID
    complaint_number: str
    subject: str
    description: str
    channel: str | None
    category: str | None
    reported_at: datetime
    customer_id: uuid.UUID | None
    branch_id: uuid.UUID | None


@dataclass(frozen=True, slots=True)
class SourceRef:
    """Polymorphic complaint origin (DEC-018)."""

    source_type: str
    source_id: uuid.UUID


@dataclass(frozen=True, slots=True)
class TargetRef:
    """Polymorphic complaint destination (DEC-018)."""

    target_type: str
    target_id: uuid.UUID | None


@dataclass(frozen=True, slots=True)
class AssignmentSnapshot:
    """Current assignment row snapshot (None when unassigned)."""

    id: uuid.UUID
    assignee_id: uuid.UUID
    assignee_name: str | None
    assigned_by: uuid.UUID | None
    assigned_at: datetime
    is_current: bool
    notes: str | None


@dataclass(frozen=True, slots=True)
class AssigneeRef:
    """Current assignee identity projected from the current assignment."""

    user_id: uuid.UUID
    full_name: str | None


@dataclass(frozen=True, slots=True)
class SlaSnapshot:
    """Current SLA record snapshot (None when no SLA row exists)."""

    id: uuid.UUID
    overall_status: str
    overall_due_at: datetime | None
    assignment_status: str
    assignment_due_at: datetime | None
    resolution_status: str
    resolution_due_at: datetime | None
    appointment_status: str
    appointment_due_at: datetime | None
    escalation_status: str
    escalation_due_at: datetime | None


@dataclass(frozen=True, slots=True)
class ComplaintContext:
    """Immutable operational read model for one Complaint.

    Assembled on demand from Complaint + Assignment + SLA + Routing.
    No table, no cache — consumers must rebuild/refresh when data changes.
    """

    complaint: ComplaintSnapshot
    current_assignment: AssignmentSnapshot | None
    current_status: str
    current_sla: SlaSnapshot | None
    priority: str
    source: SourceRef
    target: TargetRef
    routing: ComplaintRoute
    current_assignee: AssigneeRef | None
    created_at: datetime
    updated_at: datetime

    def as_dict(self) -> Mapping[str, object]:
        """Diagnostic serialization (not an API contract)."""
        route = self.routing
        assignment = self.current_assignment
        sla = self.current_sla
        assignee = self.current_assignee
        return {
            "complaintId": str(self.complaint.id),
            "complaintNumber": self.complaint.complaint_number,
            "currentStatus": self.current_status,
            "priority": self.priority,
            "sourceType": self.source.source_type,
            "sourceId": str(self.source.source_id),
            "targetType": self.target.target_type,
            "targetId": (
                str(self.target.target_id) if self.target.target_id else None
            ),
            "routing": {
                "receiverType": route.receiver_type.value,
                "receiverId": (
                    str(route.receiver_id) if route.receiver_id else None
                ),
                "assignmentContext": dict(route.assignment_context),
                "routingReason": route.routing_reason,
            },
            "currentAssignmentId": (
                str(assignment.id) if assignment is not None else None
            ),
            "currentAssigneeId": (
                str(assignee.user_id) if assignee is not None else None
            ),
            "currentAssigneeName": (
                assignee.full_name if assignee is not None else None
            ),
            "slaOverallStatus": (
                sla.overall_status if sla is not None else None
            ),
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
        }
