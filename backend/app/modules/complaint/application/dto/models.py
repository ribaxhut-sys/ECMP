"""Immutable Complaint DTOs — application read/write contracts (CAPABILITY-004…008).

Not HTTP schemas. Not persistence entities.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from typing import Mapping

from app.modules.complaint.domain.models import (
    AssigneeType,
    Assignment,
    Complaint,
    ComplaintPriority,
    ComplaintSLA,
    ComplaintStatus,
    Escalation,
    EscalationLevel,
    Resolution,
)


@dataclass(frozen=True, slots=True)
class ResolutionDto:
    """Immutable resolution snapshot."""

    summary: str
    resolved_by: str
    resolved_at: datetime

    @classmethod
    def from_domain(cls, resolution: Resolution) -> ResolutionDto:
        return cls(
            summary=resolution.summary,
            resolved_by=resolution.resolved_by,
            resolved_at=resolution.resolved_at,
        )

    def as_dict(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "summary": self.summary,
                "resolvedBy": self.resolved_by,
                "resolvedAt": self.resolved_at.isoformat(),
            }
        )


@dataclass(frozen=True, slots=True)
class AssignmentDto:
    """Immutable assignment snapshot for application consumers."""

    assignment_id: uuid.UUID
    complaint_id: uuid.UUID
    assignee_type: AssigneeType
    assignee_id: str
    assigned_at: datetime
    assigned_by: str
    released_at: datetime | None
    is_active: bool

    @classmethod
    def from_domain(cls, assignment: Assignment) -> AssignmentDto:
        return cls(
            assignment_id=assignment.assignment_id,
            complaint_id=assignment.complaint_id,
            assignee_type=assignment.assignee_type,
            assignee_id=assignment.assignee_id,
            assigned_at=assignment.assigned_at,
            assigned_by=assignment.assigned_by,
            released_at=assignment.released_at,
            is_active=assignment.is_active,
        )

    def as_dict(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "assignmentId": str(self.assignment_id),
                "complaintId": str(self.complaint_id),
                "assigneeType": self.assignee_type.value,
                "assigneeId": self.assignee_id,
                "assignedAt": self.assigned_at.isoformat(),
                "assignedBy": self.assigned_by,
                "releasedAt": (
                    None
                    if self.released_at is None
                    else self.released_at.isoformat()
                ),
                "isActive": self.is_active,
            }
        )


@dataclass(frozen=True, slots=True)
class EscalationDto:
    """Immutable escalation snapshot for application consumers."""

    escalation_id: uuid.UUID
    complaint_id: uuid.UUID
    level: EscalationLevel
    reason: str
    escalated_by: str
    escalated_at: datetime
    released_at: datetime | None
    is_current: bool

    @classmethod
    def from_domain(cls, escalation: Escalation) -> EscalationDto:
        return cls(
            escalation_id=escalation.escalation_id,
            complaint_id=escalation.complaint_id,
            level=escalation.level,
            reason=escalation.reason,
            escalated_by=escalation.escalated_by,
            escalated_at=escalation.escalated_at,
            released_at=escalation.released_at,
            is_current=escalation.is_current,
        )

    def as_dict(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "escalationId": str(self.escalation_id),
                "complaintId": str(self.complaint_id),
                "level": self.level.value,
                "reason": self.reason,
                "escalatedBy": self.escalated_by,
                "escalatedAt": self.escalated_at.isoformat(),
                "releasedAt": (
                    None
                    if self.released_at is None
                    else self.released_at.isoformat()
                ),
                "isCurrent": self.is_current,
            }
        )


@dataclass(frozen=True, slots=True)
class ComplaintSlaDto:
    """Immutable Complaint SLA snapshot for application consumers."""

    sla_id: uuid.UUID
    complaint_id: uuid.UUID
    policy_id: uuid.UUID
    policy_name: str
    target_minutes: int
    started_at: datetime
    due_at: datetime
    completed_at: datetime | None
    remaining_minutes: int
    is_active: bool
    is_breached: bool
    breached_at: datetime | None

    @classmethod
    def from_domain(
        cls,
        sla: ComplaintSLA,
        *,
        policy_name: str,
        target_minutes: int,
        current_time: datetime | None = None,
    ) -> ComplaintSlaDto:
        return cls(
            sla_id=sla.sla_id,
            complaint_id=sla.complaint_id,
            policy_id=sla.policy_id,
            policy_name=policy_name,
            target_minutes=target_minutes,
            started_at=sla.started_at,
            due_at=sla.due_at,
            completed_at=sla.completed_at,
            remaining_minutes=sla.remaining_minutes(current_time=current_time),
            is_active=sla.is_active,
            is_breached=sla.is_breached,
            breached_at=sla.breached_at,
        )

    def as_dict(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "slaId": str(self.sla_id),
                "complaintId": str(self.complaint_id),
                "policyId": str(self.policy_id),
                "policyName": self.policy_name,
                "targetMinutes": self.target_minutes,
                "startedAt": self.started_at.isoformat(),
                "dueAt": self.due_at.isoformat(),
                "completedAt": (
                    None
                    if self.completed_at is None
                    else self.completed_at.isoformat()
                ),
                "remainingMinutes": self.remaining_minutes,
                "isActive": self.is_active,
                "isBreached": self.is_breached,
                "breachedAt": (
                    None
                    if self.breached_at is None
                    else self.breached_at.isoformat()
                ),
            }
        )


@dataclass(frozen=True, slots=True)
class ComplaintDto:
    """Immutable complaint snapshot for application consumers."""

    complaint_id: uuid.UUID
    organization_id: uuid.UUID
    branch_id: uuid.UUID
    queue_ticket_id: uuid.UUID
    category: str
    title: str
    description: str
    priority: ComplaintPriority
    status: ComplaintStatus
    created_at: datetime
    updated_at: datetime
    resolution: ResolutionDto | None = None

    @classmethod
    def from_domain(cls, complaint: Complaint) -> ComplaintDto:
        return cls(
            complaint_id=complaint.complaint_id,
            organization_id=complaint.organization_id,
            branch_id=complaint.branch_id,
            queue_ticket_id=complaint.queue_ticket_id,
            category=complaint.category,
            title=complaint.title,
            description=complaint.description,
            priority=complaint.priority,
            status=complaint.status,
            created_at=complaint.created_at,
            updated_at=complaint.updated_at,
            resolution=(
                None
                if complaint.resolution is None
                else ResolutionDto.from_domain(complaint.resolution)
            ),
        )

    def as_dict(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "complaintId": str(self.complaint_id),
                "organizationId": str(self.organization_id),
                "branchId": str(self.branch_id),
                "queueTicketId": str(self.queue_ticket_id),
                "category": self.category,
                "title": self.title,
                "description": self.description,
                "priority": self.priority.value,
                "status": self.status.value,
                "createdAt": self.created_at.isoformat(),
                "updatedAt": self.updated_at.isoformat(),
                "resolution": (
                    None if self.resolution is None else dict(self.resolution.as_dict())
                ),
            }
        )


__all__ = [
    "AssignmentDto",
    "ComplaintDto",
    "ComplaintSlaDto",
    "EscalationDto",
    "ResolutionDto",
]
