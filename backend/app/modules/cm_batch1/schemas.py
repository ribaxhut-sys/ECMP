"""Pydantic contracts for CM Batch 1 (API-500…506) — camelCase."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class CustomerSearchRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_number: str | None = Field(default=None, alias="customerNumber")
    identity_number: str | None = Field(default=None, alias="identityNumber")
    reference_number: str | None = Field(default=None, alias="referenceNumber")


class CustomerCandidate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: str = Field(alias="customerId")
    display_name: str = Field(alias="displayName")
    masked_identity: str | None = Field(default=None, alias="maskedIdentity")


class CustomerSearchResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    verification_status: Literal[
        "verified",
        "not_found",
        "ambiguous",
        "degraded",
        "blocked",
    ] = Field(alias="verificationStatus")
    customer_id: str | None = Field(default=None, alias="customerId")
    as_of: datetime = Field(alias="asOf")
    candidates: list[CustomerCandidate] = Field(default_factory=list)
    enumeration_outcome: Literal["allowed", "delayed", "blocked", "alerted"] = Field(
        alias="enumerationOutcome"
    )
    brief_profile: dict[str, Any] | None = Field(default=None, alias="briefProfile")


class ConfirmCustomerRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: str = Field(alias="customerId")


class ConfirmCustomerResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: str = Field(alias="customerId")
    locked: bool = True
    as_of: datetime = Field(alias="asOf")


class Customer360Batch1Response(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: str = Field(alias="customerId")
    profile: dict[str, Any]
    active_complaints: list[dict[str, Any]] = Field(alias="activeComplaints")
    complaint_count: int = Field(alias="complaintCount")
    as_of: datetime = Field(alias="asOf")


class CreateComplaintBatch1Request(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: str = Field(alias="customerId")
    category: str
    channel: str
    subject: str
    description: str
    priority: str | None = "MEDIUM"
    recording_unit_id: str | None = Field(default=None, alias="recordingUnitId")
    duplicate_override_justification: str | None = Field(
        default=None, alias="duplicateOverrideJustification"
    )
    staging_token: str | None = Field(default=None, alias="stagingToken")


class ComplaintBatch1Response(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    complaint_id: str = Field(alias="complaintId")
    complaint_number: str = Field(alias="complaintNumber")
    status: Literal["REGISTERED"] = "REGISTERED"
    customer_id: str = Field(alias="customerId")
    case_created: Literal[False] = Field(default=False, alias="caseCreated")
    replayed: bool = False
    category: str | None = None
    channel: str | None = None
    subject: str | None = None
    priority: str | None = None
    created_at: datetime | None = Field(default=None, alias="createdAt")
    duplicate_check_result: str | None = Field(
        default=None, alias="duplicateCheckResult"
    )


class DuplicateCheckRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: str = Field(alias="customerId")
    category: str | None = None
    subject: str | None = None
    channel: str | None = None


class DuplicateCheckResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    warning: bool = False
    candidates: list[dict[str, Any]] = Field(default_factory=list)
    degraded: bool = False
    later_review_work_item_id: str | None = Field(
        default=None, alias="laterReviewWorkItemId"
    )


class DuplicateDecisionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    decision: Literal["link_existing", "override", "recommend_only", "blocked"]
    surviving_complaint_id: str | None = Field(
        default=None, alias="survivingComplaintId"
    )
    justification: str | None = None
    staging_token: str | None = Field(default=None, alias="stagingToken")
    customer_id: str | None = Field(default=None, alias="customerId")


class DuplicateDecisionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    decision_id: str = Field(alias="decisionId")
    decision: str
    customer_id: str = Field(alias="customerId")
    surviving_complaint_id: str | None = Field(
        default=None, alias="survivingComplaintId"
    )
    warning: bool = False
    hard_block: bool = Field(default=False, alias="hardBlock")
    case_created: Literal[False] = Field(default=False, alias="caseCreated")
    policy_version: str = Field(alias="policyVersion")
    created_at: datetime = Field(alias="createdAt")


class Batch1AttachmentResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    attachment_id: str = Field(alias="attachmentId")
    platform_attachment_id: str = Field(alias="platformAttachmentId")
    status: Literal["STAGED", "ACTIVE", "TRANSFERRED", "VOID", "SUPERSEDED"]
    classification: str
    staging_token: str | None = Field(default=None, alias="stagingToken")
    complaint_id: str | None = Field(default=None, alias="complaintId")
    original_name: str = Field(alias="originalName")
    mime_type: str = Field(alias="mimeType")
    size_bytes: int = Field(alias="sizeBytes")
    checksum_sha256: str = Field(alias="checksumSha256")
    supersedes_id: str | None = Field(default=None, alias="supersedesId")
    void_reason: str | None = Field(default=None, alias="voidReason")
    created_at: datetime = Field(alias="createdAt")


class TransferAttachmentsRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    staging_token: str = Field(alias="stagingToken")
    surviving_complaint_id: str = Field(alias="survivingComplaintId")


class TransferAttachmentsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    staging_token: str = Field(alias="stagingToken")
    surviving_complaint_id: str = Field(alias="survivingComplaintId")
    transferred_count: int = Field(alias="transferredCount")
    attachments: list[Batch1AttachmentResponse] = Field(default_factory=list)
    discarded: Literal[False] = False


class VoidAttachmentRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    reason: str


class LaterReviewWorkItemResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    work_item_id: str = Field(alias="workItemId")
    customer_id: str = Field(alias="customerId")
    complaint_id: str | None = Field(default=None, alias="complaintId")
    reason: str
    status: str
    created_at: datetime = Field(alias="createdAt")
    age_hours: float = Field(alias="ageHours")


class AgingComplaintItemResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    complaint_id: str = Field(alias="complaintId")
    complaint_number: str = Field(alias="complaintNumber")
    customer_id: str = Field(alias="customerId")
    status: str
    subject: str | None = None
    priority: str | None = None
    created_at: datetime = Field(alias="createdAt")
    age_hours: float = Field(alias="ageHours")
    case_created: Literal[False] = Field(default=False, alias="caseCreated")


class SupervisorQueueResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    later_review_items: list[LaterReviewWorkItemResponse] = Field(
        alias="laterReviewItems"
    )
    aging_complaints: list[AgingComplaintItemResponse] = Field(
        alias="agingComplaints"
    )
    aging_threshold_hours: int = Field(alias="agingThresholdHours")
    as_of: datetime = Field(alias="asOf")
