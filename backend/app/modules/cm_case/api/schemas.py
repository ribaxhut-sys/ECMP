"""HTTP request/response schemas aligned to OpenAPI cm-case-management.v1."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CaseSummaryResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    case_id: str = Field(alias="caseId")
    case_number: str = Field(alias="caseNumber")
    complaint_id: str = Field(alias="complaintId")
    complaint_number: str | None = Field(default=None, alias="complaintNumber")
    status: str
    case_type: str | None = Field(default=None, alias="caseType")
    category: str | None = None
    priority: str | None = None
    subject: str | None = None
    # Current handling unit — mutated on transfer.
    owning_unit_id: str | None = Field(default=None, alias="owningUnitId")
    # F4 owner — unit that created the parent Complaint; immutable.
    owner_unit_id: str | None = Field(default=None, alias="ownerUnitId")
    customer_id: str | None = Field(default=None, alias="customerId")
    created_at: datetime | None = Field(default=None, alias="createdAt")
    created_by: str | None = Field(default=None, alias="createdBy")
    handling_claimed_by: str | None = Field(default=None, alias="handlingClaimedBy")
    handling_claimed_by_name: str | None = Field(
        default=None, alias="handlingClaimedByName"
    )
    escalated_to_pusat: bool = Field(default=False, alias="escalatedToPusat")
    owning_unit: str = Field(default="BRANCH", alias="owningUnit")
    escalation_reason: str | None = Field(default=None, alias="escalationReason")
    is_read: bool | None = Field(default=None, alias="isRead")
    unread_reason: str | None = Field(default=None, alias="unreadReason")


class WorkBadgeCountsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    unread_cases: int = Field(alias="unreadCases")
    pusat_queue: int = Field(alias="pusatQueue")


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


class CaseAcceptanceResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    acceptance_id: str = Field(alias="acceptanceId")
    party: str
    decision: str
    actor_id: str = Field(alias="actorId")
    actor_unit_id: str | None = Field(default=None, alias="actorUnitId")
    decided_at: datetime = Field(alias="decidedAt")
    note: str | None = None


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
    # Current handling unit — mutated on transfer (F4 handling unit rule).
    owning_unit_id: str | None = Field(default=None, alias="owningUnitId")
    # F4 owner — unit that created the parent Complaint; never changes.
    owner_unit_id: str | None = Field(default=None, alias="ownerUnitId")
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
    handling_claimed_by: str | None = Field(default=None, alias="handlingClaimedBy")
    handling_claimed_by_name: str | None = Field(
        default=None, alias="handlingClaimedByName"
    )
    updated_at: datetime | None = Field(default=None, alias="updatedAt")
    complaint_status_after_create: str | None = Field(
        default=None, alias="complaintStatusAfterCreate"
    )
    # F4 closure rule — current-state pointers, separate from the history list.
    handling_unit_acceptance: CaseAcceptanceResponse | None = Field(
        default=None, alias="handlingUnitAcceptance"
    )
    owner_acceptance: CaseAcceptanceResponse | None = Field(
        default=None, alias="ownerAcceptance"
    )
    acceptance_history: list[CaseAcceptanceResponse] = Field(
        default_factory=list, alias="acceptanceHistory"
    )
    escalated_to_pusat: bool = Field(default=False, alias="escalatedToPusat")
    owning_unit: str = Field(default="BRANCH", alias="owningUnit")
    escalation_reason: str | None = Field(default=None, alias="escalationReason")
    escalated_at: datetime | None = Field(default=None, alias="escalatedAt")


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
    note: str | None = None
    intake_action: str | None = Field(default=None, alias="intakeAction")


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
    handling_claimed_by: str | None = Field(default=None, alias="handlingClaimedBy")


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


class EscalateToPusatRequest(BaseModel):
    """DEC-029 / API-520 lab — reason min 20 after trim (domain)."""

    model_config = ConfigDict(populate_by_name=True)

    reason: str


class CancelEscalationToPusatRequest(BaseModel):
    """Mode A lab — branch cancels API-520; reason min 20 after trim (domain)."""

    model_config = ConfigDict(populate_by_name=True)

    reason: str


class ReturnEscalationRequest(BaseModel):
    """API-521 lab — Pusat returns Case; note min 10 after trim (F4-OQ-01)."""

    model_config = ConfigDict(populate_by_name=True)

    return_note: str = Field(alias="returnNote")


class CaseHistoryEntry(BaseModel):
    """API-537 — chronological Case Timeline row (this Case + parent HQ path)."""

    model_config = ConfigDict(populate_by_name=True)

    entry_id: str = Field(alias="entryId")
    event_code: str = Field(alias="eventCode")
    event_type: str = Field(alias="eventType")
    occurred_at: datetime = Field(alias="occurredAt")
    actor_id: str | None = Field(default=None, alias="actorId")
    actor_name: str | None = Field(default=None, alias="actorName")
    actor_unit_id: str | None = Field(default=None, alias="actorUnitId")
    note: str | None = None
    priority: str | None = None
    case_number: str | None = Field(default=None, alias="caseNumber")
    case_status: str | None = Field(default=None, alias="caseStatus")
    arrival_date: str | None = Field(
        default=None,
        alias="arrivalDate",
        description=(
            "HQ taxpayer-visit calendar date (YYYY-MM-DD) when eventCode is "
            "HQ_ARRIVAL_SCHEDULED; not occurredAt"
        ),
    )
    arrival_time: str | None = Field(
        default=None,
        alias="arrivalTime",
        description="HQ taxpayer-visit clock time (HH:MM, 24h Asia/Jakarta)",
    )


class RecordAcceptanceRequest(BaseModel):
    """F4 closure rule — Handling Unit / Owner accept or reject a resolution."""

    model_config = ConfigDict(populate_by_name=True)

    party: str
    decision: str
    note: str | None = None
