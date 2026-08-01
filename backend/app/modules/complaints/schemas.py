"""Complaint API contracts (camelCase, aligned with OpenAPI)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.enums import ComplaintSourceType, ComplaintStatus, ComplaintTargetType
from app.core.user_messages import m

Priority = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


class ComplaintCreateRequest(BaseModel):
    """Create complaint — supports legacy and multi-source/target payloads.

    Legacy (backward compatible): ``customerId`` (+ optional ``branchId``)
    implies ``sourceType=CUSTOMER``, ``targetType=BRANCH``.

    Generalized: provide ``sourceType``, ``sourceId``, ``targetType``,
    ``targetId`` (all required together).
    """

    model_config = ConfigDict(populate_by_name=True)

    customer_id: uuid.UUID | None = Field(default=None, alias="customerId")
    branch_id: uuid.UUID | None = Field(default=None, alias="branchId")
    source_type: ComplaintSourceType | None = Field(default=None, alias="sourceType")
    source_id: uuid.UUID | None = Field(default=None, alias="sourceId")
    target_type: ComplaintTargetType | None = Field(default=None, alias="targetType")
    target_id: uuid.UUID | None = Field(default=None, alias="targetId")
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
            raise ValueError(m("validation.must_not_blank"))
        return cleaned

    @model_validator(mode="after")
    def resolve_source_target(self) -> ComplaintCreateRequest:
        generalized_fields = (
            self.source_type,
            self.source_id,
            self.target_type,
            self.target_id,
        )
        any_generalized = any(v is not None for v in generalized_fields)
        all_generalized = all(v is not None for v in generalized_fields)

        if any_generalized and not all_generalized:
            missing: list[str] = []
            if self.source_type is None:
                missing.append("sourceType")
            if self.source_id is None:
                missing.append("sourceId")
            if self.target_type is None:
                missing.append("targetType")
            if self.target_id is None:
                missing.append("targetId")
            raise ValueError(
                m("complaint.route_fields_all_required")
                + f" (hilang: {', '.join(missing)})"
            )

        if all_generalized:
            # Sync legacy columns from polymorphic fields.
            if self.source_type == ComplaintSourceType.CUSTOMER:
                object.__setattr__(
                    self,
                    "customer_id",
                    self.source_id if self.customer_id is None else self.customer_id,
                )
                if self.customer_id != self.source_id:
                    raise ValueError(
                        m("complaint.customer_source_mismatch")
                    )
            if self.target_type == ComplaintTargetType.BRANCH:
                object.__setattr__(
                    self,
                    "branch_id",
                    self.target_id if self.branch_id is None else self.branch_id,
                )
                if self.branch_id != self.target_id:
                    raise ValueError(
                        m("complaint.branch_target_mismatch")
                    )
            elif self.target_type == ComplaintTargetType.HEAD_OFFICE:
                # HO target — branch context is not derived.
                pass
            return self

        # Legacy payload: customer → branch (exact prior behavior).
        if self.customer_id is None:
            raise ValueError(m("complaint.customer_required_when_route_omitted"))
        object.__setattr__(self, "source_type", ComplaintSourceType.CUSTOMER)
        object.__setattr__(self, "source_id", self.customer_id)
        object.__setattr__(self, "target_type", ComplaintTargetType.BRANCH)
        object.__setattr__(self, "target_id", self.branch_id)
        return self


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
            raise ValueError(m("validation.must_not_blank"))
        return cleaned

    @model_validator(mode="after")
    def at_least_one_field(self) -> ComplaintUpdateRequest:
        provided = self.model_dump(exclude_unset=True)
        if not provided:
            raise ValueError(m("validation.at_least_one_field"))
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
    customer_id: uuid.UUID | None = Field(default=None, alias="customerId")
    branch_id: uuid.UUID | None = Field(default=None, alias="branchId")
    source_type: ComplaintSourceType = Field(alias="sourceType")
    source_id: uuid.UUID = Field(alias="sourceId")
    target_type: ComplaintTargetType = Field(alias="targetType")
    target_id: uuid.UUID | None = Field(default=None, alias="targetId")
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
            raise ValueError(m("validation.must_not_blank"))
        return cleaned


class CloseComplaintResult(BaseModel):
    """API-312 close response."""

    model_config = ConfigDict(populate_by_name=True)

    complaint_id: uuid.UUID = Field(alias="complaintId")
    status: ComplaintStatus
    closed_at: datetime = Field(alias="closedAt")
    closed_by: uuid.UUID = Field(alias="closedBy")
