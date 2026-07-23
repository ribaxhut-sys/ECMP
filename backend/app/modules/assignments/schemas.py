"""Assignment API contracts (camelCase)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.enums import ComplaintStatus


class AssignComplaintRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    assignee_id: uuid.UUID = Field(alias="assigneeId")
    reason: str | None = Field(default=None, max_length=2000)
    notes: str | None = Field(default=None, max_length=2000)

    @field_validator("reason", "notes")
    @classmethod
    def strip_optional(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class AssignmentResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    complaint_id: uuid.UUID = Field(alias="complaintId")
    assignee_id: uuid.UUID = Field(alias="assigneeId")
    assignee_name: str | None = Field(default=None, alias="assigneeName")
    assigned_by: uuid.UUID | None = Field(default=None, alias="assignedBy")
    assigned_at: datetime = Field(alias="assignedAt")
    unassigned_at: datetime | None = Field(default=None, alias="unassignedAt")
    is_current: bool = Field(alias="isCurrent")
    notes: str | None = None
    reason: str | None = None


class AssignComplaintResult(BaseModel):
    """Assign response payload: new assignment + updated complaint status."""

    model_config = ConfigDict(populate_by_name=True)

    assignment: AssignmentResponse
    complaint_id: uuid.UUID = Field(alias="complaintId")
    status: ComplaintStatus
    reassigned: bool
