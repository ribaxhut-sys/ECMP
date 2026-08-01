"""SLA API contracts (camelCase)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.core.user_messages import m

SlaStatusLiteral = Literal["PENDING", "ON_TIME", "BREACHED", "COMPLETED"]


class SlaRecordResponse(BaseModel):
    """API-314 SLA record (immutable deadline snapshot; statuses PENDING)."""

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    complaint_id: uuid.UUID = Field(alias="complaintId")
    assignment_due_at: datetime | None = Field(default=None, alias="assignmentDueAt")
    resolution_due_at: datetime | None = Field(default=None, alias="resolutionDueAt")
    appointment_due_at: datetime | None = Field(default=None, alias="appointmentDueAt")
    escalation_due_at: datetime | None = Field(default=None, alias="escalationDueAt")
    overall_due_at: datetime | None = Field(default=None, alias="overallDueAt")
    assignment_status: SlaStatusLiteral = Field(alias="assignmentStatus")
    resolution_status: SlaStatusLiteral = Field(alias="resolutionStatus")
    appointment_status: SlaStatusLiteral = Field(alias="appointmentStatus")
    escalation_status: SlaStatusLiteral = Field(alias="escalationStatus")
    overall_status: SlaStatusLiteral = Field(alias="overallStatus")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class SlaPolicyCreateRequest(BaseModel):
    """API-316 create SLA policy (targets only; no deadline calculation)."""

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    assignment_target_minutes: int = Field(alias="assignmentTargetMinutes", ge=1)
    appointment_target_minutes: int = Field(alias="appointmentTargetMinutes", ge=1)
    resolution_target_minutes: int = Field(alias="resolutionTargetMinutes", ge=1)
    escalation_target_minutes: int = Field(alias="escalationTargetMinutes", ge=1)
    overall_target_minutes: int = Field(alias="overallTargetMinutes", ge=1)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError(m("validation.name_required"))
        return cleaned

    @field_validator("description")
    @classmethod
    def strip_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class SlaPolicyResponse(BaseModel):
    """API-315 / API-316 / API-317 SLA policy payload."""

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None = None
    assignment_target_minutes: int = Field(alias="assignmentTargetMinutes")
    appointment_target_minutes: int = Field(alias="appointmentTargetMinutes")
    resolution_target_minutes: int = Field(alias="resolutionTargetMinutes")
    escalation_target_minutes: int = Field(alias="escalationTargetMinutes")
    overall_target_minutes: int = Field(alias="overallTargetMinutes")
    is_active: bool = Field(alias="isActive")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
