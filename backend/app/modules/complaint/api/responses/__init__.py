"""Complaint HTTP response DTOs (CAPABILITY-004…008)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.complaint.application.dto import (
    AssignmentDto,
    ComplaintDto,
    ComplaintSlaDto,
    EscalationDto,
    ResolutionDto,
)
from app.modules.complaint.domain.models import (
    AssigneeType,
    ComplaintPriority,
    ComplaintStatus,
    EscalationLevel,
)


class ResolutionResponse(BaseModel):
    """Never Domain Entity. Never ORM."""

    model_config = ConfigDict(populate_by_name=True)

    summary: str
    resolved_by: str = Field(alias="resolvedBy")
    resolved_at: datetime = Field(alias="resolvedAt")

    @classmethod
    def from_dto(cls, dto: ResolutionDto) -> ResolutionResponse:
        return cls(
            summary=dto.summary,
            resolved_by=dto.resolved_by,
            resolved_at=dto.resolved_at,
        )


class AssignmentResponse(BaseModel):
    """Never Domain Entity. Never ORM."""

    model_config = ConfigDict(populate_by_name=True)

    assignment_id: uuid.UUID = Field(alias="assignmentId")
    complaint_id: uuid.UUID = Field(alias="complaintId")
    assignee_type: AssigneeType = Field(alias="assigneeType")
    assignee_id: str = Field(alias="assigneeId")
    assigned_at: datetime = Field(alias="assignedAt")
    assigned_by: str = Field(alias="assignedBy")
    released_at: datetime | None = Field(default=None, alias="releasedAt")
    is_active: bool = Field(alias="isActive")

    @classmethod
    def from_dto(cls, dto: AssignmentDto) -> AssignmentResponse:
        return cls(
            assignment_id=dto.assignment_id,
            complaint_id=dto.complaint_id,
            assignee_type=dto.assignee_type,
            assignee_id=dto.assignee_id,
            assigned_at=dto.assigned_at,
            assigned_by=dto.assigned_by,
            released_at=dto.released_at,
            is_active=dto.is_active,
        )


class EscalationResponse(BaseModel):
    """Never Domain Entity. Never ORM."""

    model_config = ConfigDict(populate_by_name=True)

    escalation_id: uuid.UUID = Field(alias="escalationId")
    level: EscalationLevel
    reason: str
    escalated_by: str = Field(alias="escalatedBy")
    escalated_at: datetime = Field(alias="escalatedAt")
    is_current: bool = Field(alias="isCurrent")

    @classmethod
    def from_dto(cls, dto: EscalationDto) -> EscalationResponse:
        return cls(
            escalation_id=dto.escalation_id,
            level=dto.level,
            reason=dto.reason,
            escalated_by=dto.escalated_by,
            escalated_at=dto.escalated_at,
            is_current=dto.is_current,
        )


class ComplaintSLAResponse(BaseModel):
    """Never Domain Entity. Never ORM. CAPABILITY-008 Complaint SLA."""

    model_config = ConfigDict(populate_by_name=True)

    sla_id: uuid.UUID = Field(alias="slaId")
    policy_id: uuid.UUID = Field(alias="policyId")
    policy_name: str = Field(alias="policyName")
    target_minutes: int = Field(alias="targetMinutes")
    started_at: datetime = Field(alias="startedAt")
    due_at: datetime = Field(alias="dueAt")
    completed_at: datetime | None = Field(default=None, alias="completedAt")
    remaining_minutes: int = Field(alias="remainingMinutes")
    is_active: bool = Field(alias="isActive")
    is_breached: bool = Field(alias="isBreached")
    breached_at: datetime | None = Field(default=None, alias="breachedAt")

    @classmethod
    def from_dto(cls, dto: ComplaintSlaDto) -> ComplaintSLAResponse:
        return cls(
            sla_id=dto.sla_id,
            policy_id=dto.policy_id,
            policy_name=dto.policy_name,
            target_minutes=dto.target_minutes,
            started_at=dto.started_at,
            due_at=dto.due_at,
            completed_at=dto.completed_at,
            remaining_minutes=dto.remaining_minutes,
            is_active=dto.is_active,
            is_breached=dto.is_breached,
            breached_at=dto.breached_at,
        )


class ComplaintResponse(BaseModel):
    """Never Domain Entity. Never ORM.

    CAPABILITY-005 processing fields: complaintId, status, priority, category,
    resolution, updatedAt (plus foundation fields for CRUD continuity).
    """

    model_config = ConfigDict(populate_by_name=True)

    complaint_id: uuid.UUID = Field(alias="complaintId")
    queue_ticket_id: uuid.UUID = Field(alias="queueTicketId")
    category: str
    title: str
    description: str
    priority: ComplaintPriority
    status: ComplaintStatus
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resolution: ResolutionResponse | None = None

    @classmethod
    def from_dto(cls, dto: ComplaintDto) -> ComplaintResponse:
        return cls(
            complaint_id=dto.complaint_id,
            queue_ticket_id=dto.queue_ticket_id,
            category=dto.category,
            title=dto.title,
            description=dto.description,
            priority=dto.priority,
            status=dto.status,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
            resolution=(
                None
                if dto.resolution is None
                else ResolutionResponse.from_dto(dto.resolution)
            ),
        )


__all__ = [
    "AssignmentResponse",
    "ComplaintResponse",
    "ComplaintSLAResponse",
    "EscalationResponse",
    "ResolutionResponse",
]
