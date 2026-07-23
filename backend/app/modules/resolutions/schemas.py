"""Resolution API contracts (camelCase, aligned with OpenAPI)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.enums import ComplaintStatus, FinalResolutionStatus

ResolutionCategory = Literal[
    "SOLVED",
    "WORKAROUND",
    "DUPLICATE",
    "INVALID_REQUEST",
    "USER_ERROR",
    "THIRD_PARTY",
]


class ResolveComplaintRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    resolution_category: ResolutionCategory = Field(alias="resolutionCategory")
    root_cause: str = Field(alias="rootCause", min_length=1, max_length=500)
    resolution_notes: str = Field(alias="resolutionNotes", min_length=1, max_length=5000)
    resolved_by: uuid.UUID | None = Field(default=None, alias="resolvedBy")

    @field_validator("root_cause", "resolution_notes")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned


class ResolutionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    complaint_id: uuid.UUID = Field(alias="complaintId")
    resolution_category: ResolutionCategory = Field(alias="resolutionCategory")
    root_cause: str = Field(alias="rootCause")
    resolution_notes: str = Field(alias="resolutionNotes")
    resolved_by: uuid.UUID = Field(alias="resolvedBy")
    resolved_by_name: str | None = Field(default=None, alias="resolvedByName")
    resolved_at: datetime = Field(alias="resolvedAt")
    is_current: bool = Field(alias="isCurrent")


class ResolveComplaintResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    resolution: ResolutionResponse
    complaint_id: uuid.UUID = Field(alias="complaintId")
    status: ComplaintStatus


class FinalResolutionRequest(BaseModel):
    """API-310 request body."""

    model_config = ConfigDict(populate_by_name=True)

    summary: str = Field(min_length=1, max_length=5000)
    notes: str = Field(min_length=1, max_length=5000)
    follow_up_required: bool = Field(default=False, alias="followUpRequired")

    @field_validator("summary", "notes")
    @classmethod
    def strip_final_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned


class FinalResolutionResult(BaseModel):
    """API-310 submit response (complaint remains IN_PROGRESS)."""

    model_config = ConfigDict(populate_by_name=True)

    complaint_id: uuid.UUID = Field(alias="complaintId")
    status: FinalResolutionStatus
    submitted_at: datetime = Field(alias="submittedAt")
    submitted_by: uuid.UUID = Field(alias="submittedBy")


class FinalResolutionResponse(BaseModel):
    """GET final-resolution read model for Complaint Detail."""

    model_config = ConfigDict(populate_by_name=True)

    complaint_id: uuid.UUID = Field(alias="complaintId")
    status: FinalResolutionStatus
    summary: str
    notes: str
    follow_up_required: bool = Field(alias="followUpRequired")
    submitted_at: datetime = Field(alias="submittedAt")
    submitted_by: uuid.UUID = Field(alias="submittedBy")
    submitted_by_name: str | None = Field(default=None, alias="submittedByName")