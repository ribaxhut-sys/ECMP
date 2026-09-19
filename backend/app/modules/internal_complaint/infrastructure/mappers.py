"""ORM ↔ Aggregate mappers for Pengaduan Internal."""

from __future__ import annotations

from uuid import UUID

from app.modules.internal_complaint.domain.aggregate import (
    AcceptanceRecord,
    HistoryEvent,
    InternalComplaintAggregate,
    ResolutionRecord,
)
from app.modules.internal_complaint.domain.value_objects import (
    AcceptanceDecision,
    AcceptanceParty,
    CompletionRequestStatus,
    HistoryEventType,
    InternalComplaintNumber,
    InternalStatus,
    ResolutionProposalStatus,
    TransferRequestStatus,
    WithdrawRequestStatus,
)
from app.modules.internal_complaint.infrastructure.orm import (
    InternalComplaintAcceptanceORM,
    InternalComplaintEventORM,
    InternalComplaintORM,
    InternalComplaintResolutionORM,
)


def _current_acceptances(
    history: list[AcceptanceRecord],
    cycle_started_at,
) -> tuple[AcceptanceRecord | None, AcceptanceRecord | None]:
    """Latest ACCEPT per party after the current resolution cycle start.

    A REJECT clears pointers in-memory; ignore stale ACCEPT from prior cycles.
    """
    handling: AcceptanceRecord | None = None
    owner: AcceptanceRecord | None = None
    for record in history:
        if cycle_started_at and record.decided_at < cycle_started_at:
            continue
        if record.decision != AcceptanceDecision.ACCEPT:
            continue
        if record.party == AcceptanceParty.HANDLING_UNIT:
            handling = record
        elif record.party == AcceptanceParty.OWNER:
            owner = record
    return handling, owner


def resolution_from_orm(row: InternalComplaintResolutionORM) -> ResolutionRecord:
    return ResolutionRecord(
        resolution_id=str(row.id),
        resolution_code=row.resolution_code,
        summary=row.summary,
        status=ResolutionProposalStatus(row.status),
        comment=row.comment,
        detail=row.detail,
        proposed_by=row.proposed_by,
        proposed_at=row.proposed_at,
        decided_by=row.decided_by,
        decided_at=row.decided_at,
        rejection_reason=row.rejection_reason,
    )


def resolution_to_orm(
    complaint_id: UUID, record: ResolutionRecord
) -> InternalComplaintResolutionORM:
    stamped = record.decided_at or record.proposed_at
    return InternalComplaintResolutionORM(
        id=UUID(record.resolution_id),
        complaint_id=complaint_id,
        resolution_code=record.resolution_code,
        summary=record.summary,
        detail=record.detail,
        status=record.status.value,
        comment=record.comment,
        proposed_by=record.proposed_by,
        proposed_at=record.proposed_at,
        decided_by=record.decided_by,
        decided_at=record.decided_at,
        rejection_reason=record.rejection_reason,
        created_at=stamped,
    )


def acceptance_from_orm(row: InternalComplaintAcceptanceORM) -> AcceptanceRecord:
    return AcceptanceRecord(
        acceptance_id=str(row.id),
        party=AcceptanceParty(row.party),
        decision=AcceptanceDecision(row.decision),
        actor_id=row.actor_id,
        actor_unit_id=row.actor_unit_id,
        decided_at=row.decided_at,
        note=row.note,
    )


def acceptance_to_orm(
    complaint_id: UUID, record: AcceptanceRecord
) -> InternalComplaintAcceptanceORM:
    return InternalComplaintAcceptanceORM(
        id=UUID(record.acceptance_id),
        complaint_id=complaint_id,
        party=record.party.value,
        decision=record.decision.value,
        actor_id=record.actor_id,
        actor_unit_id=record.actor_unit_id,
        note=record.note,
        decided_at=record.decided_at,
    )


def event_from_orm(row: InternalComplaintEventORM) -> HistoryEvent:
    return HistoryEvent(
        event_id=str(row.id),
        event_type=HistoryEventType(row.event_type),
        actor_id=row.actor_id,
        actor_unit_id=row.actor_unit_id,
        occurred_at=row.occurred_at,
        note=row.note,
        source_unit_id=row.source_unit_id,
        target_unit_id=row.target_unit_id,
        payload=dict(row.payload or {}),
    )


def event_to_orm(complaint_id: UUID, record: HistoryEvent) -> InternalComplaintEventORM:
    return InternalComplaintEventORM(
        id=UUID(record.event_id),
        complaint_id=complaint_id,
        event_type=record.event_type.value,
        actor_id=record.actor_id,
        actor_unit_id=record.actor_unit_id,
        source_unit_id=record.source_unit_id,
        target_unit_id=record.target_unit_id,
        note=record.note,
        payload=dict(record.payload or {}),
        occurred_at=record.occurred_at,
    )


def complaint_from_orm(
    row: InternalComplaintORM,
    resolutions: list[InternalComplaintResolutionORM] | None = None,
    acceptances: list[InternalComplaintAcceptanceORM] | None = None,
    events: list[InternalComplaintEventORM] | None = None,
) -> InternalComplaintAggregate:
    resolution_history = [resolution_from_orm(r) for r in (resolutions or [])]
    acceptance_history = [acceptance_from_orm(a) for a in (acceptances or [])]
    history = [event_from_orm(e) for e in (events or [])]
    current = resolution_history[-1] if resolution_history else None
    cycle_started_at = None
    if (
        current
        and current.status == ResolutionProposalStatus.ACCEPTED
        and current.decided_at
    ):
        cycle_started_at = current.decided_at
    handling_acceptance, owner_acceptance = _current_acceptances(
        acceptance_history, cycle_started_at
    )
    return InternalComplaintAggregate(
        complaint_id=row.id,
        complaint_number=InternalComplaintNumber(row.complaint_number),
        status=InternalStatus(row.status),
        subject=row.subject,
        description=row.description,
        category=row.category,
        priority=row.priority,
        created_by=row.created_by,
        created_at=row.created_at,
        owner_unit_id=row.owner_unit_id,
        handling_unit_id=row.handling_unit_id,
        subcategory=row.subcategory,
        chronology=row.chronology,
        impact=row.impact,
        related_complaint_id=row.related_complaint_id,
        related_complaint_number=row.related_complaint_number,
        closed_by=row.closed_by,
        closed_at=row.closed_at,
        updated_at=row.updated_at,
        resolution=current,
        resolution_history=resolution_history,
        handling_unit_acceptance=handling_acceptance,
        owner_acceptance=owner_acceptance,
        acceptance_history=acceptance_history,
        history=history,
        supervisor_approved_after_resolved=bool(
            row.supervisor_approved_after_resolved
        ),
        transfer_request_status=(
            TransferRequestStatus(row.transfer_request_status)
            if row.transfer_request_status
            else None
        ),
        transfer_request_destination_unit_id=row.transfer_request_destination_unit_id,
        transfer_request_reason=row.transfer_request_reason,
        transfer_requested_by=row.transfer_requested_by,
        transfer_requested_at=row.transfer_requested_at,
        transfer_decided_by=row.transfer_decided_by,
        transfer_decided_at=row.transfer_decided_at,
        transfer_decision_reason=row.transfer_decision_reason,
        withdraw_request_status=(
            WithdrawRequestStatus(row.withdraw_request_status)
            if row.withdraw_request_status
            else None
        ),
        withdraw_request_reason=row.withdraw_request_reason,
        withdraw_requested_by=row.withdraw_requested_by,
        withdraw_requested_at=row.withdraw_requested_at,
        withdraw_decided_by=row.withdraw_decided_by,
        withdraw_decided_at=row.withdraw_decided_at,
        withdraw_decision_reason=row.withdraw_decision_reason,
        withdrawn_by=row.withdrawn_by,
        withdrawn_at=row.withdrawn_at,
        withdraw_reason=row.withdraw_reason,
        completion_request_status=(
            CompletionRequestStatus(row.completion_request_status)
            if row.completion_request_status
            else None
        ),
        completion_return_reason=row.completion_return_reason,
        completion_returned_by=row.completion_returned_by,
        completion_returned_at=row.completion_returned_at,
        pusat_handled_at=row.pusat_handled_at,
    )


def apply_complaint_to_orm(
    complaint: InternalComplaintAggregate, row: InternalComplaintORM
) -> None:
    row.complaint_number = complaint.complaint_number.value
    row.status = complaint.status.value
    row.subject = complaint.subject
    row.description = complaint.description
    row.category = complaint.category
    row.subcategory = complaint.subcategory
    row.priority = complaint.priority
    row.chronology = complaint.chronology
    row.impact = complaint.impact
    row.related_complaint_id = complaint.related_complaint_id
    row.related_complaint_number = complaint.related_complaint_number
    # Owner immutable: set only when blank (first insert).
    if not row.owner_unit_id:
        row.owner_unit_id = complaint.owner_unit_id
    row.handling_unit_id = complaint.handling_unit_id
    row.supervisor_approved_after_resolved = (
        complaint.supervisor_approved_after_resolved
    )
    row.closed_by = complaint.closed_by
    row.closed_at = complaint.closed_at
    row.created_by = complaint.created_by
    row.created_at = complaint.created_at
    row.updated_at = complaint.updated_at or complaint.created_at
    row.transfer_request_status = (
        complaint.transfer_request_status.value
        if complaint.transfer_request_status
        else None
    )
    row.transfer_request_destination_unit_id = (
        complaint.transfer_request_destination_unit_id
    )
    row.transfer_request_reason = complaint.transfer_request_reason
    row.transfer_requested_by = complaint.transfer_requested_by
    row.transfer_requested_at = complaint.transfer_requested_at
    row.transfer_decided_by = complaint.transfer_decided_by
    row.transfer_decided_at = complaint.transfer_decided_at
    row.transfer_decision_reason = complaint.transfer_decision_reason
    row.withdraw_request_status = (
        complaint.withdraw_request_status.value
        if complaint.withdraw_request_status
        else None
    )
    row.withdraw_request_reason = complaint.withdraw_request_reason
    row.withdraw_requested_by = complaint.withdraw_requested_by
    row.withdraw_requested_at = complaint.withdraw_requested_at
    row.withdraw_decided_by = complaint.withdraw_decided_by
    row.withdraw_decided_at = complaint.withdraw_decided_at
    row.withdraw_decision_reason = complaint.withdraw_decision_reason
    row.withdrawn_by = complaint.withdrawn_by
    row.withdrawn_at = complaint.withdrawn_at
    row.withdraw_reason = complaint.withdraw_reason
    row.completion_request_status = (
        complaint.completion_request_status.value
        if complaint.completion_request_status
        else None
    )
    row.completion_return_reason = complaint.completion_return_reason
    row.completion_returned_by = complaint.completion_returned_by
    row.completion_returned_at = complaint.completion_returned_at
    row.pusat_handled_at = complaint.pusat_handled_at
