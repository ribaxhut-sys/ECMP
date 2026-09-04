"""HTTP schemas for Pengaduan Internal API."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class InternalComplaintSummaryResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    complaint_id: str = Field(alias="complaintId")
    complaint_number: str = Field(alias="complaintNumber")
    status: str
    subject: str
    category: str | None = None
    priority: str | None = None
    owner_unit_id: str = Field(alias="ownerUnitId")
    handling_unit_id: str = Field(alias="handlingUnitId")
    created_at: datetime = Field(alias="createdAt")
    created_by: str = Field(alias="createdBy")
    created_by_name: str | None = Field(default=None, alias="createdByName")
    related_complaint_id: str | None = Field(
        default=None, alias="relatedComplaintId"
    )
    related_complaint_number: str | None = Field(
        default=None, alias="relatedComplaintNumber"
    )
    transfer_request_status: str | None = Field(
        default=None, alias="transferRequestStatus"
    )
    withdraw_request_status: str | None = Field(
        default=None, alias="withdrawRequestStatus"
    )
    completion_request_status: str | None = Field(
        default=None, alias="completionRequestStatus"
    )
    resolution_status: str | None = Field(
        default=None, alias="resolutionStatus"
    )


class ResolutionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    resolution_id: str = Field(alias="resolutionId")
    resolution_code: str = Field(alias="resolutionCode")
    summary: str
    status: str
    comment: str
    detail: str | None = None
    proposed_by: str | None = Field(default=None, alias="proposedBy")
    proposed_by_name: str | None = Field(default=None, alias="proposedByName")
    proposed_at: datetime | None = Field(default=None, alias="proposedAt")
    decided_by: str | None = Field(default=None, alias="decidedBy")
    decided_at: datetime | None = Field(default=None, alias="decidedAt")
    rejection_reason: str | None = Field(default=None, alias="rejectionReason")


class AcceptanceResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    acceptance_id: str = Field(alias="acceptanceId")
    party: str
    decision: str
    actor_id: str = Field(alias="actorId")
    actor_unit_id: str | None = Field(default=None, alias="actorUnitId")
    decided_at: datetime = Field(alias="decidedAt")
    note: str | None = None


class HistoryEventResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    event_id: str = Field(alias="eventId")
    event_type: str = Field(alias="eventType")
    actor_id: str = Field(alias="actorId")
    actor_name: str | None = Field(default=None, alias="actorName")
    actor_unit_id: str | None = Field(default=None, alias="actorUnitId")
    occurred_at: datetime = Field(alias="occurredAt")
    note: str | None = None
    source_unit_id: str | None = Field(default=None, alias="sourceUnitId")
    target_unit_id: str | None = Field(default=None, alias="targetUnitId")


class InternalComplaintResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    complaint_id: str = Field(alias="complaintId")
    complaint_number: str = Field(alias="complaintNumber")
    status: str
    subject: str
    description: str
    category: str
    subcategory: str | None = None
    priority: str
    chronology: str | None = None
    impact: str | None = None
    related_complaint_id: str | None = Field(
        default=None, alias="relatedComplaintId"
    )
    related_complaint_number: str | None = Field(
        default=None, alias="relatedComplaintNumber"
    )
    owner_unit_id: str = Field(alias="ownerUnitId")
    handling_unit_id: str = Field(alias="handlingUnitId")
    resolution: ResolutionResponse | None = None
    resolution_history: list[ResolutionResponse] = Field(
        default_factory=list, alias="resolutionHistory"
    )
    handling_unit_acceptance: AcceptanceResponse | None = Field(
        default=None, alias="handlingUnitAcceptance"
    )
    owner_acceptance: AcceptanceResponse | None = Field(
        default=None, alias="ownerAcceptance"
    )
    acceptance_history: list[AcceptanceResponse] = Field(
        default_factory=list, alias="acceptanceHistory"
    )
    history: list[HistoryEventResponse] = Field(default_factory=list)
    closed_by: str | None = Field(default=None, alias="closedBy")
    closed_by_name: str | None = Field(default=None, alias="closedByName")
    closed_at: datetime | None = Field(default=None, alias="closedAt")
    created_at: datetime = Field(alias="createdAt")
    created_by: str = Field(alias="createdBy")
    created_by_name: str | None = Field(default=None, alias="createdByName")
    updated_at: datetime | None = Field(default=None, alias="updatedAt")
    transfer_request_status: str | None = Field(
        default=None, alias="transferRequestStatus"
    )
    transfer_request_destination_unit_id: str | None = Field(
        default=None, alias="transferRequestDestinationUnitId"
    )
    transfer_request_reason: str | None = Field(
        default=None, alias="transferRequestReason"
    )
    transfer_requested_by: str | None = Field(
        default=None, alias="transferRequestedBy"
    )
    transfer_requested_by_name: str | None = Field(
        default=None, alias="transferRequestedByName"
    )
    transfer_requested_at: datetime | None = Field(
        default=None, alias="transferRequestedAt"
    )
    transfer_decided_by: str | None = Field(default=None, alias="transferDecidedBy")
    transfer_decided_by_name: str | None = Field(
        default=None, alias="transferDecidedByName"
    )
    transfer_decided_at: datetime | None = Field(
        default=None, alias="transferDecidedAt"
    )
    transfer_decision_reason: str | None = Field(
        default=None, alias="transferDecisionReason"
    )
    withdraw_request_status: str | None = Field(
        default=None, alias="withdrawRequestStatus"
    )
    withdraw_request_reason: str | None = Field(
        default=None, alias="withdrawRequestReason"
    )
    withdraw_requested_by: str | None = Field(
        default=None, alias="withdrawRequestedBy"
    )
    withdraw_requested_by_name: str | None = Field(
        default=None, alias="withdrawRequestedByName"
    )
    withdraw_requested_at: datetime | None = Field(
        default=None, alias="withdrawRequestedAt"
    )
    withdraw_decided_by: str | None = Field(
        default=None, alias="withdrawDecidedBy"
    )
    withdraw_decided_by_name: str | None = Field(
        default=None, alias="withdrawDecidedByName"
    )
    withdraw_decided_at: datetime | None = Field(
        default=None, alias="withdrawDecidedAt"
    )
    withdraw_decision_reason: str | None = Field(
        default=None, alias="withdrawDecisionReason"
    )
    withdrawn_by: str | None = Field(default=None, alias="withdrawnBy")
    withdrawn_by_name: str | None = Field(default=None, alias="withdrawnByName")
    withdrawn_at: datetime | None = Field(default=None, alias="withdrawnAt")
    withdraw_reason: str | None = Field(default=None, alias="withdrawReason")
    completion_request_status: str | None = Field(
        default=None, alias="completionRequestStatus"
    )
    completion_return_reason: str | None = Field(
        default=None, alias="completionReturnReason"
    )
    completion_returned_by: str | None = Field(
        default=None, alias="completionReturnedBy"
    )
    completion_returned_by_name: str | None = Field(
        default=None, alias="completionReturnedByName"
    )
    completion_returned_at: datetime | None = Field(
        default=None, alias="completionReturnedAt"
    )


class CreateInternalComplaintRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    subject: str
    description: str
    category: str
    priority: str = "MEDIUM"
    # Legacy free-text; ignored on new creates (use relatedComplaintId).
    subcategory: str | None = None
    chronology: str | None = None
    impact: str | None = None
    related_complaint_id: str | None = Field(
        default=None, alias="relatedComplaintId"
    )
    # Client-supplied relatedComplaintNumber is ignored — server snapshots from DB.
    related_complaint_number: str | None = Field(
        default=None, alias="relatedComplaintNumber"
    )
    # Owner always derived from principal. Cabang create always sends Handling
    # to Pusat (ASSIGNED). Pusat create: complaints:assign → direct transfer;
    # Agent-family + handlingUnitId → pending transfer request (requestReason
    # required).
    owner_unit_id: str | None = Field(default=None, alias="ownerUnitId")
    handling_unit_id: str | None = Field(default=None, alias="handlingUnitId")
    request_reason: str | None = Field(default=None, alias="requestReason")


class TransferRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    destination_unit_id: str = Field(alias="destinationUnitId")
    reason: str | None = None


class RequestTransferRequest(BaseModel):
    """Submit (or re-submit after REJECTED) an Agent transfer request."""

    model_config = ConfigDict(populate_by_name=True)

    destination_unit_id: str = Field(alias="destinationUnitId")
    reason: str = Field(min_length=1)


class DecideTransferRequestRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    decision: Literal["APPROVE", "REJECT"]
    reason: str | None = None


class StartHandlingRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    note: str | None = None


class UpdateStatusRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    to_status: str = Field(alias="toStatus")
    destination_unit_id: str | None = Field(default=None, alias="destinationUnitId")
    reason: str | None = None


class ResolveRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    action: str
    comment: str
    resolution_code: str | None = Field(default=None, alias="resolutionCode")
    summary: str | None = None
    detail: str | None = None
    rejection_reason: str | None = Field(default=None, alias="rejectionReason")


class RecordAcceptanceRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    party: str
    decision: str
    note: str | None = None


class CloseRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    note: str | None = None


class WithdrawRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    reason: str = Field(min_length=1)


class ReturnForCompletionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    reason: str = Field(min_length=1)


class ResendToPusatRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    note: str = Field(min_length=1)

    @field_validator("note")
    @classmethod
    def note_not_blank(cls, value: str) -> str:
        cleaned = (value or "").strip()
        if not cleaned:
            raise ValueError("note is required")
        return cleaned


class DecideWithdrawRequestRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    decision: Literal["APPROVE", "REJECT"]
    reason: str | None = None


class CountBucketResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    key: str
    count: int


class InternalComplaintReportSummaryResponse(BaseModel):
    """API-554 — report breakdown counted server-side, not in the browser."""

    model_config = ConfigDict(populate_by_name=True)

    total_items: int = Field(alias="totalItems")
    by_status: list[CountBucketResponse] = Field(alias="byStatus")
    by_priority: list[CountBucketResponse] = Field(alias="byPriority")
    by_handling_unit: list[CountBucketResponse] = Field(alias="byHandlingUnit")
