"""Complaint API contracts (camelCase, aligned with OpenAPI)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.enums import ComplaintStatus

Priority = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


class ComplaintCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: uuid.UUID = Field(alias="customerId")
    branch_id: uuid.UUID | None = Field(default=None, alias="branchId")
    subject: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=5000)
    priority: Priority
    channel: str | None = Field(default=None, max_length=32)
    category: str | None = Field(default=None, max_length=64)
    reported_at: datetime | None = Field(default=None, alias="reportedAt")

    @field_validator("subject", "description")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned


class ComplaintUpdateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    subject: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=1, max_length=5000)
    priority: Priority | None = None
    channel: str | None = Field(default=None, max_length=32)
    category: str | None = Field(default=None, max_length=64)
    branch_id: uuid.UUID | None = Field(default=None, alias="branchId")

    @field_validator("subject", "description")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned

    @model_validator(mode="after")
    def at_least_one_field(self) -> ComplaintUpdateRequest:
        provided = self.model_dump(exclude_unset=True)
        if not provided:
            raise ValueError("at least one field must be provided")
        return self


class ComplaintStatusChangeRequest(BaseModel):
    """PATCH /status body — only validated lifecycle transitions."""

    model_config = ConfigDict(populate_by_name=True)

    status: ComplaintStatus
    reason: str | None = Field(default=None, max_length=2000)

    @field_validator("reason")
    @classmethod
    def strip_reason(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class ComplaintResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    complaint_number: str = Field(alias="complaintNumber")
    customer_id: uuid.UUID = Field(alias="customerId")
    branch_id: uuid.UUID | None = Field(default=None, alias="branchId")
    subject: str
    description: str
    status: ComplaintStatus
    priority: Priority
    channel: str | None = None
    category: str | None = None
    reported_at: datetime = Field(alias="reportedAt")
    closed_at: datetime | None = Field(default=None, alias="closedAt")
    closed_by: uuid.UUID | None = Field(default=None, alias="closedBy")
    closure_notes: str | None = Field(default=None, alias="closureNotes")
    created_at: datetime = Field(alias="createdAt")
    created_by: uuid.UUID | None = Field(default=None, alias="createdBy")
    updated_at: datetime = Field(alias="updatedAt")


class CloseComplaintRequest(BaseModel):
    """API-312 request body — explicit Complaint Closure after Final Resolution."""

    model_config = ConfigDict(populate_by_name=True)

    notes: str = Field(min_length=1, max_length=5000)

    @field_validator("notes")
    @classmethod
    def strip_notes(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned


class CloseComplaintResult(BaseModel):
    """API-312 close response."""

    model_config = ConfigDict(populate_by_name=True)

    complaint_id: uuid.UUID = Field(alias="complaintId")
    status: ComplaintStatus
    closed_at: datetime = Field(alias="closedAt")
    closed_by: uuid.UUID = Field(alias="closedBy")
