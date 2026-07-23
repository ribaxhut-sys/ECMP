"""Escalation API contracts (camelCase)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.enums import ComplaintStatus, EscalationReasonCode
from app.modules.appointments.schemas import AppointmentSummary

EscalationReasonCodeLiteral = Literal[
    "SPECIALIST_REQUIRED",
    "COMPLEX_CASE",
    "POLICY_EXCEPTION",
    "CUSTOMER_REQUEST",
    "OTHER",
]


class EscalateComplaintRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    reason: str = Field(min_length=1, max_length=2000)
    escalated_to_user_id: uuid.UUID | None = Field(
        default=None, alias="escalatedToUserId"
    )
    escalated_to_role_id: uuid.UUID | None = Field(
        default=None, alias="escalatedToRoleId"
    )
    escalated_from_user_id: uuid.UUID | None = Field(
        default=None, alias="escalatedFromUserId"
    )

    @field_validator("reason")
    @classmethod
    def strip_reason(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned

    @model_validator(mode="after")
    def require_target(self) -> EscalateComplaintRequest:
        if self.escalated_to_user_id is None and self.escalated_to_role_id is None:
            raise ValueError(
                "escalatedToUserId or escalatedToRoleId is required"
            )
        return self


class EscalationRequestCreate(BaseModel):
    """API-301 — Branch → HO Escalation Request body."""

    model_config = ConfigDict(populate_by_name=True)

    reason_code: EscalationReasonCodeLiteral = Field(alias="reasonCode")
    reason_description: str = Field(
        alias="reasonDescription", min_length=1, max_length=2000
    )
    diagnosis: str = Field(min_length=1, max_length=5000)
    notes: str | None = Field(default=None, max_length=5000)

    @field_validator("reason_description", "diagnosis")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned

    @field_validator("notes")
    @classmethod
    def strip_optional_notes(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @field_validator("reason_code")
    @classmethod
    def validate_reason_code(
        cls, value: EscalationReasonCodeLiteral
    ) -> EscalationReasonCodeLiteral:
        # Ensure value is one of the approved codes (Literal already checks).
        _ = EscalationReasonCode(value)
        return value


class EscalationResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    complaint_id: uuid.UUID = Field(alias="complaintId")
    escalated_from_user_id: uuid.UUID | None = Field(
        default=None, alias="escalatedFromUserId"
    )
    escalated_to_user_id: uuid.UUID | None = Field(
        default=None, alias="escalatedToUserId"
    )
    escalated_to_role_id: uuid.UUID | None = Field(
        default=None, alias="escalatedToRoleId"
    )
    reason: str
    level: int
    status: str
    escalated_at: datetime = Field(alias="escalatedAt")
    resolved_at: datetime | None = Field(default=None, alias="resolvedAt")
    reason_code: str | None = Field(default=None, alias="reasonCode")
    reason_description: str | None = Field(default=None, alias="reasonDescription")
    diagnosis: str | None = None
    notes: str | None = None
    requested_by: uuid.UUID | None = Field(default=None, alias="requestedBy")
    requested_by_name: str | None = Field(default=None, alias="requestedByName")
    requested_at: datetime | None = Field(default=None, alias="requestedAt")
    reviewed_by: uuid.UUID | None = Field(default=None, alias="reviewedBy")
    reviewed_by_name: str | None = Field(default=None, alias="reviewedByName")
    reviewed_at: datetime | None = Field(default=None, alias="reviewedAt")
    review_notes: str | None = Field(default=None, alias="reviewNotes")
    active_appointment: AppointmentSummary | None = Field(
        default=None, alias="activeAppointment"
    )


class EscalationReviewRequest(BaseModel):
    """API-303 / API-304 review body."""

    model_config = ConfigDict(populate_by_name=True)

    review_notes: str = Field(alias="reviewNotes", min_length=1, max_length=5000)

    @field_validator("review_notes")
    @classmethod
    def strip_review_notes(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned


class EscalationReviewResult(BaseModel):
    """API-303 / API-304 slim review response."""

    model_config = ConfigDict(populate_by_name=True)

    id: uuid.UUID
    status: str
    reviewed_by: uuid.UUID = Field(alias="reviewedBy")
    reviewed_at: datetime = Field(alias="reviewedAt")


class EscalationRequestResult(BaseModel):
    """API-301 slim create response."""

    model_config = ConfigDict(populate_by_name=True)

    id: uuid.UUID
    complaint_id: uuid.UUID = Field(alias="complaintId")
    status: str
    requested_by: uuid.UUID = Field(alias="requestedBy")
    requested_at: datetime = Field(alias="requestedAt")


class EscalateComplaintResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    escalation: EscalationResponse
    complaint_id: uuid.UUID = Field(alias="complaintId")
    status: ComplaintStatus
