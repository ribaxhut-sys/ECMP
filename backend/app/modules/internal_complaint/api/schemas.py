"""HTTP schemas for Pengaduan Internal API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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


class ResolutionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    resolution_id: str = Field(alias="resolutionId")
    resolution_code: str = Field(alias="resolutionCode")
    summary: str
    status: str
    comment: str
    detail: str | None = None
    proposed_by: str | None = Field(default=None, alias="proposedBy")
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
    closed_at: datetime | None = Field(default=None, alias="closedAt")
    created_at: datetime = Field(alias="createdAt")
    created_by: str = Field(alias="createdBy")
    created_by_name: str | None = Field(default=None, alias="createdByName")
    updated_at: datetime | None = Field(default=None, alias="updatedAt")


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
    # Owner always derived from principal. handlingUnitId may optionally set
    # initial Handling Unit (Cabang ↔ Pusat only) under complaints:create —
    # Agents can escalate on create without complaints:assign.
    owner_unit_id: str | None = Field(default=None, alias="ownerUnitId")
    handling_unit_id: str | None = Field(default=None, alias="handlingUnitId")


class TransferRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    destination_unit_id: str = Field(alias="destinationUnitId")
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
