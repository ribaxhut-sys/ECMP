"""HTTP request/response schemas aligned to OpenAPI cm-case-management.v1."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CaseResolutionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    resolution_id: str = Field(alias="resolutionId")
    resolution_code: str = Field(alias="resolutionCode")
    summary: str
    status: str
    comment: str
    detail: str | None = None
    customer_impact: str | None = Field(default=None, alias="customerImpact")
    attachment_ids: list[str] = Field(default_factory=list, alias="attachmentIds")
    proposed_by: str | None = Field(default=None, alias="proposedBy")
    proposed_at: datetime | None = Field(default=None, alias="proposedAt")
    decided_by: str | None = Field(default=None, alias="decidedBy")
    decided_at: datetime | None = Field(default=None, alias="decidedAt")
    rejection_reason: str | None = Field(default=None, alias="rejectionReason")


class CaseResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    case_id: str = Field(alias="caseId")
    case_number: str = Field(alias="caseNumber")
    complaint_id: str = Field(alias="complaintId")
    customer_id: str = Field(alias="customerId")
    status: str
    case_type: str = Field(alias="caseType")
    category: str | None = None
    subject: str
    description: str
    priority: str
    owning_unit_id: str | None = Field(default=None, alias="owningUnitId")
    assigned_user_id: str | None = Field(default=None, alias="assignedUserId")
    sla_policy_version_id: str | None = Field(default=None, alias="slaPolicyVersionId")
    sla_countdown_active: bool = Field(default=False, alias="slaCountdownActive")
    resolution: CaseResolutionResponse | None = None
    resolution_history: list[CaseResolutionResponse] = Field(
        default_factory=list, alias="resolutionHistory"
    )
    cancel_reason: str | None = Field(default=None, alias="cancelReason")
    closed_by: str | None = Field(default=None, alias="closedBy")
    closed_at: datetime | None = Field(default=None, alias="closedAt")
    created_at: datetime = Field(alias="createdAt")
    created_by: str = Field(alias="createdBy")
    updated_at: datetime | None = Field(default=None, alias="updatedAt")
    complaint_status_after_create: str | None = Field(
        default=None, alias="complaintStatusAfterCreate"
    )


class CreateCaseRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    complaint_id: str = Field(alias="complaintId")
    case_type: str = Field(alias="caseType")
    category: str | None = None
    subject: str
    description: str
    priority: str
    destination_unit_id: str | None = Field(default=None, alias="destinationUnitId")
    assigned_user_id: str | None = Field(default=None, alias="assignedUserId")
    sla_policy_version_id: str | None = Field(default=None, alias="slaPolicyVersionId")


class AddCaseRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    case_type: str = Field(alias="caseType")
    category: str | None = None
    subject: str
    description: str
    priority: str
    destination_unit_id: str | None = Field(default=None, alias="destinationUnitId")
    assigned_user_id: str | None = Field(default=None, alias="assignedUserId")
    sla_policy_version_id: str | None = Field(default=None, alias="slaPolicyVersionId")


class UpdateCaseStatusRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    to_status: str = Field(alias="toStatus")
    destination_unit_id: str | None = Field(default=None, alias="destinationUnitId")
    cancel_reason: str | None = Field(default=None, alias="cancelReason")
    reason: str | None = None
    assigned_user_id: str | None = Field(default=None, alias="assignedUserId")


class ResolveCaseRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    action: str
    comment: str
    resolution_code: str | None = Field(default=None, alias="resolutionCode")
    summary: str | None = None
    detail: str | None = None
    customer_impact: str | None = Field(default=None, alias="customerImpact")
    attachment_ids: list[str] = Field(default_factory=list, alias="attachmentIds")
    rejection_reason: str | None = Field(default=None, alias="rejectionReason")


class CloseCaseRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    note: str | None = None
