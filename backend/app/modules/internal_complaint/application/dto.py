"""Application DTOs / commands for Pengaduan Internal."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ResolutionDTO:
    resolution_id: str
    resolution_code: str
    summary: str
    status: str
    comment: str
    detail: str | None = None
    proposed_by: str | None = None
    proposed_at: datetime | None = None
    decided_by: str | None = None
    decided_at: datetime | None = None
    rejection_reason: str | None = None


@dataclass
class AcceptanceDTO:
    acceptance_id: str
    party: str
    decision: str
    actor_id: str
    actor_unit_id: str | None
    decided_at: datetime
    note: str | None = None


@dataclass
class HistoryEventDTO:
    event_id: str
    event_type: str
    actor_id: str
    actor_unit_id: str | None
    occurred_at: datetime
    note: str | None = None
    source_unit_id: str | None = None
    target_unit_id: str | None = None


@dataclass
class InternalComplaintDTO:
    complaint_id: str
    complaint_number: str
    status: str
    subject: str
    description: str
    category: str
    priority: str
    owner_unit_id: str
    handling_unit_id: str
    created_by: str
    created_at: datetime
    subcategory: str | None = None
    chronology: str | None = None
    impact: str | None = None
    related_complaint_id: str | None = None
    related_complaint_number: str | None = None
    closed_by: str | None = None
    closed_at: datetime | None = None
    updated_at: datetime | None = None
    resolution: ResolutionDTO | None = None
    resolution_history: list[ResolutionDTO] = field(default_factory=list)
    handling_unit_acceptance: AcceptanceDTO | None = None
    owner_acceptance: AcceptanceDTO | None = None
    acceptance_history: list[AcceptanceDTO] = field(default_factory=list)
    history: list[HistoryEventDTO] = field(default_factory=list)
    transfer_request_status: str | None = None
    transfer_request_destination_unit_id: str | None = None
    transfer_request_reason: str | None = None
    transfer_requested_by: str | None = None
    transfer_requested_at: datetime | None = None
    transfer_decided_by: str | None = None
    transfer_decided_at: datetime | None = None
    transfer_decision_reason: str | None = None
    withdraw_request_status: str | None = None
    withdraw_request_reason: str | None = None
    withdraw_requested_by: str | None = None
    withdraw_requested_at: datetime | None = None
    withdraw_decided_by: str | None = None
    withdraw_decided_at: datetime | None = None
    withdraw_decision_reason: str | None = None
    withdrawn_by: str | None = None
    withdrawn_at: datetime | None = None
    withdraw_reason: str | None = None
    completion_request_status: str | None = None
    completion_return_reason: str | None = None
    completion_returned_by: str | None = None
    completion_returned_at: datetime | None = None
    pusat_handled_at: datetime | None = None


@dataclass
class InternalComplaintSummaryDTO:
    complaint_id: str
    complaint_number: str
    status: str
    subject: str
    category: str | None
    priority: str | None
    owner_unit_id: str
    handling_unit_id: str
    created_at: datetime
    created_by: str
    related_complaint_id: str | None = None
    related_complaint_number: str | None = None
    transfer_request_status: str | None = None
    withdraw_request_status: str | None = None
    completion_request_status: str | None = None


@dataclass
class CreateInternalComplaintCommand:
    subject: str
    description: str
    category: str
    priority: str
    actor_id: str
    owner_unit_id: str
    subcategory: str | None = None
    chronology: str | None = None
    impact: str | None = None
    actor_unit_id: str | None = None
    related_complaint_id: str | None = None
    related_complaint_number: str | None = None


@dataclass
class TransferCommand:
    complaint_id: str
    destination_unit_id: str
    actor_id: str
    reason: str | None = None
    actor_unit_id: str | None = None
    actor_is_admin: bool = False


@dataclass
class RequestTransferCommand:
    """Agent-family gate — request instead of direct transfer on create."""

    complaint_id: str
    destination_unit_id: str
    reason: str
    actor_id: str
    actor_unit_id: str | None = None
    actor_is_admin: bool = False


@dataclass
class DecideTransferRequestCommand:
    complaint_id: str
    decision: str  # "APPROVE" | "REJECT"
    actor_id: str
    reason: str | None = None
    actor_unit_id: str | None = None
    actor_is_admin: bool = False


@dataclass
class StartHandlingCommand:
    complaint_id: str
    actor_id: str
    note: str | None = None
    actor_unit_id: str | None = None


@dataclass
class UpdateStatusCommand:
    complaint_id: str
    to_status: str
    actor_id: str
    destination_unit_id: str | None = None
    reason: str | None = None
    actor_unit_id: str | None = None
    actor_is_admin: bool = False


@dataclass
class ResolveCommand:
    complaint_id: str
    action: str
    comment: str
    actor_id: str
    resolution_code: str | None = None
    summary: str | None = None
    detail: str | None = None
    rejection_reason: str | None = None
    actor_unit_id: str | None = None
    actor_is_admin: bool = False


@dataclass
class RecordAcceptanceCommand:
    complaint_id: str
    party: str
    decision: str
    actor_id: str
    note: str | None = None
    actor_unit_id: str | None = None


@dataclass
class CloseCommand:
    complaint_id: str
    actor_id: str
    note: str | None = None
    actor_unit_id: str | None = None


@dataclass
class WithdrawCommand:
    complaint_id: str
    actor_id: str
    reason: str
    actor_unit_id: str | None = None


@dataclass
class RequestWithdrawCommand:
    complaint_id: str
    actor_id: str
    reason: str
    actor_unit_id: str | None = None


@dataclass
class DecideWithdrawRequestCommand:
    complaint_id: str
    decision: str
    actor_id: str
    reason: str | None = None
    actor_unit_id: str | None = None


@dataclass
class ReturnForCompletionCommand:
    complaint_id: str
    actor_id: str
    reason: str
    actor_unit_id: str | None = None


@dataclass
class ResendToPusatCommand:
    complaint_id: str
    actor_id: str
    note: str
    actor_unit_id: str | None = None
