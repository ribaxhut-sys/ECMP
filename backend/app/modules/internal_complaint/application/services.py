"""Application service for Pengaduan Internal."""

from __future__ import annotations

from app.core.authorization.principal import Principal
from app.core.authorization.visibility import DEFAULT_PUSAT_UNIT_CODES
from app.modules.internal_complaint.application.dto import (
    AcceptanceDTO,
    CloseCommand,
    CreateInternalComplaintCommand,
    DecideTransferRequestCommand,
    DecideWithdrawRequestCommand,
    HistoryEventDTO,
    InternalComplaintDTO,
    InternalComplaintSummaryDTO,
    RecordAcceptanceCommand,
    RequestTransferCommand,
    RequestWithdrawCommand,
    ResendToPusatCommand,
    ResolutionDTO,
    ResolveCommand,
    ReturnForCompletionCommand,
    StartHandlingCommand,
    TransferCommand,
    UpdateStatusCommand,
    WithdrawCommand,
)
from app.modules.internal_complaint.application.visibility import (
    resolve_internal_visibility,
)
from app.modules.internal_complaint.domain import errors as err
from app.modules.internal_complaint.domain.aggregate import (
    AcceptanceRecord,
    HistoryEvent,
    InternalComplaintAggregate,
    ResolutionRecord,
)
from app.modules.internal_complaint.domain.repositories import InternalComplaintRepository
from app.modules.internal_complaint.domain.value_objects import (
    AcceptanceDecision,
    AcceptanceParty,
    InternalComplaintNumber,
    ResolveAction,
    TransferRequestStatus,
    WithdrawRequestStatus,
)

# API decision string ("APPROVE"/"REJECT", matching the WP intake-escalation
# vocabulary) -> domain TransferRequestStatus. Kept out of the value object
# so the aggregate never has to know about the wire format.
_TRANSFER_DECISION_MAP: dict[str, TransferRequestStatus] = {
    "APPROVE": TransferRequestStatus.APPROVED,
    "REJECT": TransferRequestStatus.REJECTED,
}
_WITHDRAW_DECISION_MAP: dict[str, WithdrawRequestStatus] = {
    "APPROVE": WithdrawRequestStatus.APPROVED,
    "REJECT": WithdrawRequestStatus.REJECTED,
}


def _resolution_dto(r: ResolutionRecord) -> ResolutionDTO:
    return ResolutionDTO(
        resolution_id=r.resolution_id,
        resolution_code=r.resolution_code,
        summary=r.summary,
        status=r.status.value,
        comment=r.comment,
        detail=r.detail,
        proposed_by=r.proposed_by,
        proposed_at=r.proposed_at,
        decided_by=r.decided_by,
        decided_at=r.decided_at,
        rejection_reason=r.rejection_reason,
    )


def _acceptance_dto(a: AcceptanceRecord) -> AcceptanceDTO:
    return AcceptanceDTO(
        acceptance_id=a.acceptance_id,
        party=a.party.value,
        decision=a.decision.value,
        actor_id=a.actor_id,
        actor_unit_id=a.actor_unit_id,
        decided_at=a.decided_at,
        note=a.note,
    )


def _history_dto(e: HistoryEvent) -> HistoryEventDTO:
    return HistoryEventDTO(
        event_id=e.event_id,
        event_type=e.event_type.value,
        actor_id=e.actor_id,
        actor_unit_id=e.actor_unit_id,
        occurred_at=e.occurred_at,
        note=e.note,
        source_unit_id=e.source_unit_id,
        target_unit_id=e.target_unit_id,
    )


def to_dto(c: InternalComplaintAggregate) -> InternalComplaintDTO:
    return InternalComplaintDTO(
        complaint_id=str(c.complaint_id),
        complaint_number=c.complaint_number.value,
        status=c.status.value,
        subject=c.subject,
        description=c.description,
        category=c.category,
        priority=c.priority,
        owner_unit_id=c.owner_unit_id,
        handling_unit_id=c.handling_unit_id,
        created_by=c.created_by,
        created_at=c.created_at,
        subcategory=c.subcategory,
        chronology=c.chronology,
        impact=c.impact,
        related_complaint_id=c.related_complaint_id,
        related_complaint_number=c.related_complaint_number,
        closed_by=c.closed_by,
        closed_at=c.closed_at,
        updated_at=c.updated_at,
        resolution=_resolution_dto(c.resolution) if c.resolution else None,
        resolution_history=[_resolution_dto(r) for r in c.resolution_history],
        handling_unit_acceptance=(
            _acceptance_dto(c.handling_unit_acceptance)
            if c.handling_unit_acceptance
            else None
        ),
        owner_acceptance=(
            _acceptance_dto(c.owner_acceptance) if c.owner_acceptance else None
        ),
        acceptance_history=[_acceptance_dto(a) for a in c.acceptance_history],
        history=[_history_dto(e) for e in c.history],
        transfer_request_status=(
            c.transfer_request_status.value if c.transfer_request_status else None
        ),
        transfer_request_destination_unit_id=c.transfer_request_destination_unit_id,
        transfer_request_reason=c.transfer_request_reason,
        transfer_requested_by=c.transfer_requested_by,
        transfer_requested_at=c.transfer_requested_at,
        transfer_decided_by=c.transfer_decided_by,
        transfer_decided_at=c.transfer_decided_at,
        transfer_decision_reason=c.transfer_decision_reason,
        withdraw_request_status=(
            c.withdraw_request_status.value if c.withdraw_request_status else None
        ),
        withdraw_request_reason=c.withdraw_request_reason,
        withdraw_requested_by=c.withdraw_requested_by,
        withdraw_requested_at=c.withdraw_requested_at,
        withdraw_decided_by=c.withdraw_decided_by,
        withdraw_decided_at=c.withdraw_decided_at,
        withdraw_decision_reason=c.withdraw_decision_reason,
        withdrawn_by=c.withdrawn_by,
        withdrawn_at=c.withdrawn_at,
        withdraw_reason=c.withdraw_reason,
        completion_request_status=(
            c.completion_request_status.value if c.completion_request_status else None
        ),
        completion_return_reason=c.completion_return_reason,
        completion_returned_by=c.completion_returned_by,
        completion_returned_at=c.completion_returned_at,
        pusat_handled_at=c.pusat_handled_at,
    )


class InternalComplaintApplicationService:
    def __init__(self, repo: InternalComplaintRepository) -> None:
        self._repo = repo

    def create(self, cmd: CreateInternalComplaintCommand) -> InternalComplaintDTO:
        number = InternalComplaintNumber(self._repo.next_number(owner_unit_id=cmd.owner_unit_id))
        complaint = InternalComplaintAggregate.create(
            complaint_number=number,
            subject=cmd.subject,
            description=cmd.description,
            category=cmd.category,
            priority=cmd.priority,
            created_by=cmd.actor_id,
            owner_unit_id=cmd.owner_unit_id,
            subcategory=cmd.subcategory,
            chronology=cmd.chronology,
            impact=cmd.impact,
            related_complaint_id=cmd.related_complaint_id,
            related_complaint_number=cmd.related_complaint_number,
            actor_unit_id=cmd.actor_unit_id,
        )
        self._repo.save(complaint)
        self._repo.commit()
        return to_dto(complaint)

    def get(self, complaint_id: str) -> InternalComplaintDTO:
        return to_dto(self._require(complaint_id))

    def list_complaints(
        self,
        principal: Principal,
        *,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        org_unit_id: str | None = None,
        pending_transfer_request: bool | None = None,
        pending_withdraw_request: bool | None = None,
    ) -> tuple[list[InternalComplaintSummaryDTO], int]:
        visibility = resolve_internal_visibility(principal, org_unit_id=org_unit_id)
        rows, total = self._repo.list_summaries(
            visibility=visibility.value,
            actor_id=str(principal.user_id),
            org_unit_id=org_unit_id,
            pusat_unit_codes=DEFAULT_PUSAT_UNIT_CODES,
            status=status,
            page=page,
            page_size=page_size,
            pending_transfer_request=pending_transfer_request,
            pending_withdraw_request=pending_withdraw_request,
        )
        items = [
            InternalComplaintSummaryDTO(
                complaint_id=str(r.id),
                complaint_number=r.complaint_number,
                status=r.status,
                subject=r.subject,
                category=r.category,
                priority=r.priority,
                owner_unit_id=r.owner_unit_id,
                handling_unit_id=r.handling_unit_id,
                created_at=r.created_at,
                created_by=r.created_by,
                related_complaint_id=r.related_complaint_id,
                related_complaint_number=r.related_complaint_number,
                transfer_request_status=r.transfer_request_status,
                withdraw_request_status=r.withdraw_request_status,
                completion_request_status=r.completion_request_status,
            )
            for r in rows
        ]
        return items, total

    def count_pending_transfer_requests(
        self, principal: Principal, *, org_unit_id: str | None = None
    ) -> int:
        """Badge/queue count — same visibility rules as the list (DEC-024 pattern)."""
        _, total = self.list_complaints(
            principal,
            page=1,
            page_size=1,
            org_unit_id=org_unit_id,
            pending_transfer_request=True,
        )
        return total

    def count_pending_withdraw_requests(
        self, principal: Principal, *, org_unit_id: str | None = None
    ) -> int:
        _, total = self.list_complaints(
            principal,
            page=1,
            page_size=1,
            org_unit_id=org_unit_id,
            pending_withdraw_request=True,
        )
        return total

    def transfer(self, cmd: TransferCommand) -> InternalComplaintDTO:
        complaint = self._require(cmd.complaint_id)
        complaint.transfer(
            destination_unit_id=cmd.destination_unit_id,
            actor_id=cmd.actor_id,
            actor_unit_id=cmd.actor_unit_id,
            actor_is_admin=cmd.actor_is_admin,
            reason=cmd.reason,
        )
        self._repo.save(complaint)
        self._repo.commit()
        return to_dto(complaint)

    def request_transfer(self, cmd: RequestTransferCommand) -> InternalComplaintDTO:
        complaint = self._require(cmd.complaint_id)
        complaint.request_transfer(
            destination_unit_id=cmd.destination_unit_id,
            reason=cmd.reason,
            actor_id=cmd.actor_id,
            actor_unit_id=cmd.actor_unit_id,
            actor_is_admin=cmd.actor_is_admin,
        )
        self._repo.save(complaint)
        self._repo.commit()
        return to_dto(complaint)

    def decide_transfer_request(
        self, cmd: DecideTransferRequestCommand
    ) -> InternalComplaintDTO:
        complaint = self._require(cmd.complaint_id)
        key = (cmd.decision or "").strip().upper()
        decision = _TRANSFER_DECISION_MAP.get(key)
        if decision is None:
            raise err.validation(
                "Invalid transfer request decision",
                details={"field": "decision", "value": cmd.decision},
            )
        complaint.decide_transfer_request(
            decision=decision,
            actor_id=cmd.actor_id,
            actor_unit_id=cmd.actor_unit_id,
            actor_is_admin=cmd.actor_is_admin,
            reason=cmd.reason,
        )
        self._repo.save(complaint)
        self._repo.commit()
        return to_dto(complaint)

    def start_handling(self, cmd: StartHandlingCommand) -> InternalComplaintDTO:
        complaint = self._require(cmd.complaint_id)
        complaint.start_handling(
            actor_id=cmd.actor_id,
            actor_unit_id=cmd.actor_unit_id,
            note=cmd.note,
        )
        self._repo.save(complaint)
        self._repo.commit()
        return to_dto(complaint)

    def update_status(self, cmd: UpdateStatusCommand) -> InternalComplaintDTO:
        complaint = self._require(cmd.complaint_id)
        complaint.transition_status(
            to_status=cmd.to_status,
            actor_id=cmd.actor_id,
            destination_unit_id=cmd.destination_unit_id,
            reason=cmd.reason,
            actor_unit_id=cmd.actor_unit_id,
            actor_is_admin=cmd.actor_is_admin,
        )
        self._repo.save(complaint)
        self._repo.commit()
        return to_dto(complaint)

    def resolve(self, cmd: ResolveCommand) -> InternalComplaintDTO:
        complaint = self._require(cmd.complaint_id)
        try:
            action = ResolveAction(cmd.action.strip().upper())
        except ValueError as exc:
            raise err.validation(
                "Invalid resolve action",
                details={"field": "action", "value": cmd.action},
            ) from exc
        complaint.resolve(
            action=action,
            actor_id=cmd.actor_id,
            comment=cmd.comment,
            resolution_code=cmd.resolution_code,
            summary=cmd.summary,
            detail=cmd.detail,
            rejection_reason=cmd.rejection_reason,
            actor_unit_id=cmd.actor_unit_id,
            actor_is_admin=cmd.actor_is_admin,
        )
        self._repo.save(complaint)
        self._repo.commit()
        return to_dto(complaint)

    def record_acceptance(self, cmd: RecordAcceptanceCommand) -> InternalComplaintDTO:
        complaint = self._require(cmd.complaint_id)
        try:
            party = AcceptanceParty(cmd.party.strip().upper())
        except ValueError as exc:
            raise err.validation(
                "Invalid acceptance party",
                details={"field": "party", "value": cmd.party},
            ) from exc
        try:
            decision = AcceptanceDecision(cmd.decision.strip().upper())
        except ValueError as exc:
            raise err.validation(
                "Invalid acceptance decision",
                details={"field": "decision", "value": cmd.decision},
            ) from exc
        complaint.record_acceptance(
            party=party,
            decision=decision,
            actor_id=cmd.actor_id,
            actor_unit_id=cmd.actor_unit_id,
            note=cmd.note,
        )
        self._repo.save(complaint)
        self._repo.commit()
        return to_dto(complaint)

    def close(self, cmd: CloseCommand) -> InternalComplaintDTO:
        complaint = self._require(cmd.complaint_id)
        complaint.close(
            actor_id=cmd.actor_id,
            actor_unit_id=cmd.actor_unit_id,
            note=cmd.note,
        )
        self._repo.save(complaint)
        self._repo.commit()
        return to_dto(complaint)

    def withdraw(self, cmd: WithdrawCommand) -> InternalComplaintDTO:
        complaint = self._require(cmd.complaint_id)
        complaint.withdraw(
            actor_id=cmd.actor_id,
            reason=cmd.reason,
            actor_unit_id=cmd.actor_unit_id,
        )
        self._repo.save(complaint)
        self._repo.commit()
        return to_dto(complaint)

    def request_withdraw(self, cmd: RequestWithdrawCommand) -> InternalComplaintDTO:
        complaint = self._require(cmd.complaint_id)
        complaint.request_withdraw(
            actor_id=cmd.actor_id,
            reason=cmd.reason,
            actor_unit_id=cmd.actor_unit_id,
        )
        self._repo.save(complaint)
        self._repo.commit()
        return to_dto(complaint)

    def decide_withdraw_request(
        self, cmd: DecideWithdrawRequestCommand
    ) -> InternalComplaintDTO:
        complaint = self._require(cmd.complaint_id)
        key = (cmd.decision or "").strip().upper()
        decision = _WITHDRAW_DECISION_MAP.get(key)
        if decision is None:
            raise err.validation(
                "Invalid withdraw request decision",
                details={"field": "decision", "value": cmd.decision},
            )
        complaint.decide_withdraw_request(
            decision=decision,
            actor_id=cmd.actor_id,
            actor_unit_id=cmd.actor_unit_id,
            reason=cmd.reason,
        )
        self._repo.save(complaint)
        self._repo.commit()
        return to_dto(complaint)

    def return_for_completion(
        self, cmd: ReturnForCompletionCommand
    ) -> InternalComplaintDTO:
        complaint = self._require(cmd.complaint_id)
        complaint.return_for_completion(
            actor_id=cmd.actor_id,
            reason=cmd.reason,
            actor_unit_id=cmd.actor_unit_id,
        )
        self._repo.save(complaint)
        self._repo.commit()
        return to_dto(complaint)

    def resend_to_pusat(self, cmd: ResendToPusatCommand) -> InternalComplaintDTO:
        complaint = self._require(cmd.complaint_id)
        complaint.resend_to_pusat(
            actor_id=cmd.actor_id,
            actor_unit_id=cmd.actor_unit_id,
            note=cmd.note,
        )
        self._repo.save(complaint)
        self._repo.commit()
        return to_dto(complaint)

    def _require(self, complaint_id: str) -> InternalComplaintAggregate:
        complaint = self._repo.get(complaint_id)
        if complaint is None:
            raise err.not_found("Internal complaint does not exist.")
        return complaint
