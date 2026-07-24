"""Complaint HTTP request models (CAPABILITY-004…008)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.complaint.api.validators import strip_optional, strip_required
from app.modules.complaint.domain.models import (
    AssigneeType,
    ComplaintPriority,
    ComplaintStatus,
    EscalationLevel,
)


class CreateComplaintRequest(BaseModel):
    """POST /api/v1/complaints · POST /api/v1/tickets/{ticketId}/complaints"""

    model_config = ConfigDict(populate_by_name=True)

    organization_id: uuid.UUID = Field(alias="organizationId")
    branch_id: uuid.UUID = Field(alias="branchId")
    queue_ticket_id: uuid.UUID | None = Field(default=None, alias="queueTicketId")
    category: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=10000)
    priority: ComplaintPriority = ComplaintPriority.NORMAL

    @field_validator("category")
    @classmethod
    def _category(cls, value: str) -> str:
        return strip_required(value, "category")

    @field_validator("title")
    @classmethod
    def _title(cls, value: str) -> str:
        return strip_required(value, "title")

    @field_validator("description")
    @classmethod
    def _description(cls, value: str) -> str:
        return strip_required(value, "description")


class UpdateComplaintRequest(BaseModel):
    """PUT /api/v1/complaints/{id}"""

    model_config = ConfigDict(populate_by_name=True)

    category: str | None = Field(default=None, min_length=1, max_length=100)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=1, max_length=10000)
    priority: ComplaintPriority | None = None
    status: ComplaintStatus | None = None

    @field_validator("category")
    @classmethod
    def _category(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return strip_required(value, "category")

    @field_validator("title")
    @classmethod
    def _title(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return strip_required(value, "title")

    @field_validator("description")
    @classmethod
    def _description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return strip_required(value, "description")


class ResolveRequest(BaseModel):
    """POST /api/v1/complaints/{id}/resolve"""

    model_config = ConfigDict(populate_by_name=True)

    summary: str = Field(min_length=1, max_length=10000)
    resolved_by: str = Field(alias="resolvedBy", min_length=1, max_length=200)

    @field_validator("summary")
    @classmethod
    def _summary(cls, value: str) -> str:
        return strip_required(value, "summary")

    @field_validator("resolved_by")
    @classmethod
    def _resolved_by(cls, value: str) -> str:
        return strip_required(value, "resolved_by")


class CloseRequest(BaseModel):
    """POST /api/v1/complaints/{id}/close — body optional."""

    model_config = ConfigDict(populate_by_name=True)


class ReopenRequest(BaseModel):
    """POST /api/v1/complaints/{id}/reopen — reason optional."""

    model_config = ConfigDict(populate_by_name=True)

    reason: str | None = Field(default=None, max_length=2000)

    @field_validator("reason")
    @classmethod
    def _reason(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = strip_optional(value)
        return cleaned or None


class AssignRequest(BaseModel):
    """POST /api/v1/complaints/{id}/assign"""

    model_config = ConfigDict(populate_by_name=True)

    assignee_type: AssigneeType = Field(alias="assigneeType")
    assignee_id: str = Field(alias="assigneeId", min_length=1, max_length=200)
    assigned_by: str = Field(alias="assignedBy", min_length=1, max_length=200)

    @field_validator("assignee_id")
    @classmethod
    def _assignee_id(cls, value: str) -> str:
        return strip_required(value, "assignee_id")

    @field_validator("assigned_by")
    @classmethod
    def _assigned_by(cls, value: str) -> str:
        return strip_required(value, "assigned_by")


class ReassignRequest(BaseModel):
    """POST /api/v1/complaints/{id}/reassign"""

    model_config = ConfigDict(populate_by_name=True)

    assignee_type: AssigneeType = Field(alias="assigneeType")
    assignee_id: str = Field(alias="assigneeId", min_length=1, max_length=200)
    assigned_by: str = Field(alias="assignedBy", min_length=1, max_length=200)

    @field_validator("assignee_id")
    @classmethod
    def _assignee_id(cls, value: str) -> str:
        return strip_required(value, "assignee_id")

    @field_validator("assigned_by")
    @classmethod
    def _assigned_by(cls, value: str) -> str:
        return strip_required(value, "assigned_by")


class UnassignRequest(BaseModel):
    """POST /api/v1/complaints/{id}/unassign"""

    model_config = ConfigDict(populate_by_name=True)

    released_by: str = Field(alias="releasedBy", min_length=1, max_length=200)
    reason: str | None = Field(default=None, max_length=2000)

    @field_validator("released_by")
    @classmethod
    def _released_by(cls, value: str) -> str:
        return strip_required(value, "released_by")

    @field_validator("reason")
    @classmethod
    def _reason(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = strip_optional(value)
        return cleaned or None


class EscalateRequest(BaseModel):
    """POST /api/v1/complaints/{id}/escalate"""

    model_config = ConfigDict(populate_by_name=True)

    level: EscalationLevel
    reason: str = Field(min_length=1, max_length=10000)
    escalated_by: str = Field(alias="escalatedBy", min_length=1, max_length=200)

    @field_validator("reason")
    @classmethod
    def _reason(cls, value: str) -> str:
        return strip_required(value, "reason")

    @field_validator("escalated_by")
    @classmethod
    def _escalated_by(cls, value: str) -> str:
        return strip_required(value, "escalated_by")


class StartSLARequest(BaseModel):
    """POST /api/v1/complaints/{id}/sla/start"""

    model_config = ConfigDict(populate_by_name=True)

    policy_id: uuid.UUID | None = Field(default=None, alias="policyId")


class RecalculateRequest(BaseModel):
    """POST /api/v1/complaints/{id}/sla/recalculate"""

    model_config = ConfigDict(populate_by_name=True)

    current_time: datetime = Field(alias="currentTime")


__all__ = [
    "AssignRequest",
    "CloseRequest",
    "CreateComplaintRequest",
    "EscalateRequest",
    "ReassignRequest",
    "RecalculateRequest",
    "ReopenRequest",
    "ResolveRequest",
    "StartSLARequest",
    "UnassignRequest",
    "UpdateComplaintRequest",
]
