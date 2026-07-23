"""Escalation API contracts (camelCase)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.enums import ComplaintStatus


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


class EscalateComplaintResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    escalation: EscalationResponse
    complaint_id: uuid.UUID = Field(alias="complaintId")
    status: ComplaintStatus
