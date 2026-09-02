"""Pengaduan Internal aggregate — Owner immutable, Handling Unit transferable, dual acceptance."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

from app.core.authorization.visibility import is_pusat_unit
from app.modules.internal_complaint.domain import errors as err
from app.modules.internal_complaint.domain.transitions import can_transition_status
from app.modules.internal_complaint.domain.value_objects import (
    RESOLUTION_SENTINEL,
    AcceptanceDecision,
    AcceptanceParty,
    CompletionRequestStatus,
    HistoryEventType,
    InternalComplaintNumber,
    InternalStatus,
    ResolutionProposalStatus,
    ResolveAction,
    TransferRequestStatus,
    WithdrawRequestStatus,
)

_CANONICAL_PUSAT_UNIT = "PUSAT"


def canonicalize_internal_handling_unit(unit_id: str | None) -> str:
    """Pengaduan Internal has one Pusat door: PUSAT (never PUSAT-CRO / HO-*)."""
    target = (unit_id or "").strip()
    if is_pusat_unit(target):
        return _CANONICAL_PUSAT_UNIT
    return target


def actor_matches_internal_handling(
    actor_unit_id: str | None,
    handling_unit_id: str,
    *,
    actor_is_admin: bool = False,
) -> bool:
    """Cabang: exact handling unit. Pusat: any Pusat login (or Admin) may act."""
    if is_pusat_unit(handling_unit_id):
        return actor_is_admin or is_pusat_unit(actor_unit_id)
    return _unit_ids_equal(actor_unit_id, handling_unit_id)


def is_branch_pusat_transfer(source_unit_id: str, target_unit_id: str) -> bool:
    """True only for Cabang ↔ Pusat (XOR). Forbids Cabang↔Cabang and Pusat↔Pusat."""
    source_is_pusat = is_pusat_unit(source_unit_id)
    target_is_pusat = is_pusat_unit(target_unit_id)
    return source_is_pusat != target_is_pusat


def actor_transfer_source(
    actor_unit_id: str | None, *, actor_is_admin: bool = False
) -> str:
    """Cabang actor → cabang source; Admin / Pusat → PUSAT.

    Missing membership for a non-admin is treated as cabang so the actor
    can only send to Pusat (never pick another branch).
    """
    if actor_is_admin or is_pusat_unit(actor_unit_id):
        return "PUSAT"
    return (actor_unit_id or "").strip() or "BRANCH"


def assert_actor_may_transfer_to(
    *,
    actor_unit_id: str | None,
    actor_is_admin: bool,
    destination_unit_id: str,
) -> None:
    actor_source = actor_transfer_source(
        actor_unit_id, actor_is_admin=actor_is_admin
    )
    if is_branch_pusat_transfer(actor_source, destination_unit_id):
        return
    raise err.conflict(
        "TRANSFER_DIRECTION_NOT_ALLOWED",
        "Cabang hanya dapat memindahkan ke Pusat; Pusat hanya ke cabang.",
        details={
            "actorUnitId": actor_unit_id,
            "destinationUnitId": destination_unit_id,
        },
    )


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _unit_ids_equal(left: str | None, right: str | None) -> bool:
    a = (left or "").strip().upper()
    b = (right or "").strip().upper()
    return bool(a) and bool(b) and a == b


def _actor_ids_equal(left: str | None, right: str | None) -> bool:
    a = (left or "").strip()
    b = (right or "").strip()
    return bool(a) and bool(b) and a == b


@dataclass
class ResolutionRecord:
    resolution_id: str
    resolution_code: str
    summary: str
    status: ResolutionProposalStatus
    comment: str
    detail: str | None = None
    proposed_by: str | None = None
    proposed_at: datetime | None = None
    decided_by: str | None = None
    decided_at: datetime | None = None
    rejection_reason: str | None = None


@dataclass(frozen=True, slots=True)
class AcceptanceRecord:
    acceptance_id: str
    party: AcceptanceParty
    decision: AcceptanceDecision
    actor_id: str
    actor_unit_id: str | None
    decided_at: datetime
    note: str | None = None


@dataclass(frozen=True, slots=True)
class HistoryEvent:
    event_id: str
    event_type: HistoryEventType
    actor_id: str
    actor_unit_id: str | None
    occurred_at: datetime
    note: str | None = None
    source_unit_id: str | None = None
    target_unit_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class InternalComplaintAggregate:
    complaint_id: UUID
    complaint_number: InternalComplaintNumber
    status: InternalStatus
    subject: str
    description: str
    category: str
    priority: str
    created_by: str
    created_at: datetime
    # Owner = creator unit; immutable after create.
    owner_unit_id: str
    # Current handling unit; mutated only by transfer (ASSIGNED).
    handling_unit_id: str
    subcategory: str | None = None
    chronology: str | None = None
    impact: str | None = None
    related_complaint_id: str | None = None
    related_complaint_number: str | None = None
    closed_by: str | None = None
    closed_at: datetime | None = None
    updated_at: datetime | None = None
    resolution: ResolutionRecord | None = None
    resolution_history: list[ResolutionRecord] = field(default_factory=list)
    handling_unit_acceptance: AcceptanceRecord | None = None
    owner_acceptance: AcceptanceRecord | None = None
    acceptance_history: list[AcceptanceRecord] = field(default_factory=list)
    history: list[HistoryEvent] = field(default_factory=list)
    supervisor_approved_after_resolved: bool = False
    # Agent-family transfer request gate (Cabang XOR Pusat) — Agent create
    # never transfers directly; Supervisor/Manager/Admin must decide first.
    transfer_request_status: TransferRequestStatus | None = None
    transfer_request_destination_unit_id: str | None = None
    transfer_request_reason: str | None = None
    transfer_requested_by: str | None = None
    transfer_requested_at: datetime | None = None
    transfer_decided_by: str | None = None
    transfer_decided_at: datetime | None = None
    transfer_decision_reason: str | None = None
    withdraw_request_status: WithdrawRequestStatus | None = None
    withdraw_request_reason: str | None = None
    withdraw_requested_by: str | None = None
    withdraw_requested_at: datetime | None = None
    withdraw_decided_by: str | None = None
    withdraw_decided_at: datetime | None = None
    withdraw_decision_reason: str | None = None
    withdrawn_by: str | None = None
    withdrawn_at: datetime | None = None
    withdraw_reason: str | None = None
    completion_request_status: CompletionRequestStatus | None = None
    completion_return_reason: str | None = None
    completion_returned_by: str | None = None
    completion_returned_at: datetime | None = None
    pusat_handled_at: datetime | None = None

    def _append_history(
        self,
        *,
        event_type: HistoryEventType,
        actor_id: str,
        actor_unit_id: str | None,
        note: str | None = None,
        source_unit_id: str | None = None,
        target_unit_id: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> None:
        occurred = _utcnow()
        if self.history:
            last = _as_utc(self.history[-1].occurred_at)
            if occurred <= last:
                occurred = last + timedelta(milliseconds=1)
        self.history.append(
            HistoryEvent(
                event_id=str(uuid4()),
                event_type=event_type,
                actor_id=actor_id,
                actor_unit_id=actor_unit_id,
                occurred_at=occurred,
                note=(note or "").strip() or None,
                source_unit_id=source_unit_id,
                target_unit_id=target_unit_id,
                payload=dict(payload or {}),
            )
        )

    def _mark_pusat_handled(self) -> None:
        """Sticky — first Pusat action (receive / return / approve withdraw)."""
        if self.pusat_handled_at is None:
            self.pusat_handled_at = _utcnow()

    @classmethod
    def create(
        cls,
        *,
        complaint_number: InternalComplaintNumber,
        subject: str,
        description: str,
        category: str,
        priority: str,
        created_by: str,
        owner_unit_id: str,
        subcategory: str | None = None,
        chronology: str | None = None,
        impact: str | None = None,
        related_complaint_id: str | None = None,
        related_complaint_number: str | None = None,
        actor_unit_id: str | None = None,
    ) -> InternalComplaintAggregate:
        owner = (owner_unit_id or "").strip()
        if not owner:
            raise err.validation(
                "ownerUnitId is required (derived from creator unit)",
                details={"field": "ownerUnitId"},
            )
        now = _utcnow()
        related_id = (related_complaint_id or "").strip() or None
        related_number = (related_complaint_number or "").strip() or None
        if related_id and not related_number:
            raise err.validation(
                "relatedComplaintNumber snapshot is required when relatedComplaintId is set",
                details={"field": "relatedComplaintNumber"},
            )
        if related_number and not related_id:
            raise err.validation(
                "relatedComplaintId is required when relatedComplaintNumber is set",
                details={"field": "relatedComplaintId"},
            )
        agg = cls(
            complaint_id=uuid4(),
            complaint_number=complaint_number,
            status=InternalStatus.CREATED,
            subject=subject.strip(),
            description=description.strip(),
            category=category.strip(),
            priority=priority.strip(),
            created_by=created_by,
            created_at=now,
            owner_unit_id=owner,
            handling_unit_id=owner,
            subcategory=(subcategory.strip() if subcategory else None),
            chronology=(chronology.strip() if chronology else None),
            impact=(impact.strip() if impact else None),
            related_complaint_id=related_id,
            related_complaint_number=related_number,
            updated_at=now,
        )
        agg._append_history(
            event_type=HistoryEventType.CREATED,
            actor_id=created_by,
            actor_unit_id=actor_unit_id or owner,
            note="Pengaduan internal dibuat",
            source_unit_id=owner,
            target_unit_id=owner,
        )
        return agg

    def transfer(
        self,
        *,
        destination_unit_id: str,
        actor_id: str,
        actor_unit_id: str | None = None,
        actor_is_admin: bool = False,
        reason: str | None = None,
        enforce_actor_direction: bool = True,
    ) -> None:
        """Transfer changes Handling Unit only — Owner is never mutated."""
        if self.status in (
            InternalStatus.CLOSED,
            InternalStatus.RESOLVED,
            InternalStatus.WITHDRAWN,
        ):
            raise err.invalid_state(
                "Cannot transfer a RESOLVED/CLOSED/WITHDRAWN complaint.",
                details={"status": self.status.value},
            )
        target = canonicalize_internal_handling_unit(destination_unit_id)
        if not target:
            raise err.validation(
                "destinationUnitId is required for transfer",
                details={"field": "destinationUnitId"},
            )
        if target == self.handling_unit_id:
            raise err.conflict(
                "SAME_HANDLING_UNIT",
                "destinationUnitId must differ from current handling unit.",
            )
        source = self.handling_unit_id
        if not is_branch_pusat_transfer(source, target):
            raise err.conflict(
                "TRANSFER_DIRECTION_NOT_ALLOWED",
                "Transfer hanya Cabang ↔ Pusat (tidak Cabang ↔ Cabang).",
                details={
                    "sourceUnitId": source,
                    "destinationUnitId": target,
                },
            )
        if enforce_actor_direction:
            assert_actor_may_transfer_to(
                actor_unit_id=actor_unit_id,
                actor_is_admin=actor_is_admin,
                destination_unit_id=target,
            )
        self.handling_unit_id = target
        self.status = InternalStatus.ASSIGNED
        if is_pusat_unit(target):
            self.completion_request_status = None
            self.completion_return_reason = None
            self.completion_returned_by = None
            self.completion_returned_at = None
        self.updated_at = _utcnow()
        self._append_history(
            event_type=HistoryEventType.TRANSFER,
            actor_id=actor_id,
            actor_unit_id=actor_unit_id,
            note=reason,
            source_unit_id=source,
            target_unit_id=target,
        )

    def request_transfer(
        self,
        *,
        destination_unit_id: str,
        reason: str,
        actor_id: str,
        actor_unit_id: str | None = None,
        actor_is_admin: bool = False,
    ) -> None:
        """Agent-family gate: ask to send Handling to the opposite unit.

        Only valid while the complaint is still local (CREATED, never
        transferred) and no request is already pending. Does not move
        Handling Unit — that only happens on APPROVE via ``transfer()``.
        """
        if self.status != InternalStatus.CREATED:
            raise err.invalid_state(
                "Transfer request requires status CREATED.",
                details={"status": self.status.value},
            )
        if self.handling_unit_id != self.owner_unit_id:
            raise err.invalid_state(
                "Complaint already transferred; request no longer applies."
            )
        if self.transfer_request_status == TransferRequestStatus.PENDING:
            raise err.conflict(
                "TRANSFER_REQUEST_PENDING",
                "A transfer request is already pending decision.",
            )
        target = canonicalize_internal_handling_unit(destination_unit_id)
        if not target:
            raise err.validation(
                "destinationUnitId is required",
                details={"field": "destinationUnitId"},
            )
        reason_text = (reason or "").strip()
        if not reason_text:
            raise err.validation(
                "reason is required for a transfer request",
                details={"field": "reason"},
            )
        if not is_branch_pusat_transfer(self.owner_unit_id, target):
            raise err.conflict(
                "TRANSFER_DIRECTION_NOT_ALLOWED",
                "Transfer hanya Cabang ↔ Pusat (tidak Cabang ↔ Cabang).",
                details={
                    "sourceUnitId": self.owner_unit_id,
                    "destinationUnitId": target,
                },
            )
        assert_actor_may_transfer_to(
            actor_unit_id=actor_unit_id,
            actor_is_admin=actor_is_admin,
            destination_unit_id=target,
        )
        now = _utcnow()
        self.transfer_request_status = TransferRequestStatus.PENDING
        self.transfer_request_destination_unit_id = target
        self.transfer_request_reason = reason_text
        self.transfer_requested_by = actor_id
        self.transfer_requested_at = now
        self.transfer_decided_by = None
        self.transfer_decided_at = None
        self.transfer_decision_reason = None
        self.updated_at = now
        self._append_history(
            event_type=HistoryEventType.TRANSFER_REQUESTED,
            actor_id=actor_id,
            actor_unit_id=actor_unit_id,
            note=reason_text,
            source_unit_id=self.owner_unit_id,
            target_unit_id=target,
        )

    def decide_transfer_request(
        self,
        *,
        decision: TransferRequestStatus,
        actor_id: str,
        actor_unit_id: str | None = None,
        actor_is_admin: bool = False,
        reason: str | None = None,
    ) -> None:
        """Supervisor/Manager/Admin decides a pending Agent transfer request.

        APPROVE performs the transfer immediately (reuses ``transfer()`` so
        the XOR direction check and ASSIGNED status change stay identical to
        the Supervisor/Manager direct-transfer path). REJECT leaves the
        complaint local at CREATED — the Agent may request again.
        """
        if self.transfer_request_status != TransferRequestStatus.PENDING:
            raise err.conflict(
                "NO_PENDING_TRANSFER_REQUEST",
                "No pending transfer request to decide.",
            )
        now = _utcnow()
        if decision == TransferRequestStatus.APPROVED:
            target = self.transfer_request_destination_unit_id or ""
            original_reason = self.transfer_request_reason
            self.transfer_request_status = TransferRequestStatus.APPROVED
            self.transfer_decided_by = actor_id
            self.transfer_decided_at = now
            self.transfer_decision_reason = (reason or "").strip() or None
            self._append_history(
                event_type=HistoryEventType.TRANSFER_REQUEST_APPROVED,
                actor_id=actor_id,
                actor_unit_id=actor_unit_id,
                note=self.transfer_decision_reason,
            )
            self.transfer(
                destination_unit_id=target,
                actor_id=actor_id,
                actor_unit_id=actor_unit_id,
                actor_is_admin=actor_is_admin,
                reason=original_reason,
                enforce_actor_direction=False,
            )
            return
        if decision == TransferRequestStatus.REJECTED:
            reason_text = (reason or "").strip()
            if not reason_text:
                raise err.validation(
                    "reason is required when rejecting a transfer request",
                    details={"field": "reason"},
                )
            self.transfer_request_status = TransferRequestStatus.REJECTED
            self.transfer_decided_by = actor_id
            self.transfer_decided_at = now
            self.transfer_decision_reason = reason_text
            self.updated_at = now
            self._append_history(
                event_type=HistoryEventType.TRANSFER_REQUEST_REJECTED,
                actor_id=actor_id,
                actor_unit_id=actor_unit_id,
                note=reason_text,
            )
            return
        raise err.validation("Unsupported transfer request decision")

    def start_handling(
        self,
        *,
        actor_id: str,
        actor_unit_id: str | None = None,
        note: str | None = None,
        emit_review: bool = True,
    ) -> None:
        """Receive / start review — CREATED or ASSIGNED → IN_PROGRESS.

        ``emit_review=False`` when receive is bundled into another action
        (auto-claim on PROPOSE) so history stays RECEIVED → RESOLUTION.
        """
        if self.status not in (InternalStatus.CREATED, InternalStatus.ASSIGNED):
            raise err.invalid_state(
                "Receive/handle requires CREATED or ASSIGNED.",
                details={"status": self.status.value},
            )
        if self.completion_request_status == CompletionRequestStatus.PENDING:
            raise err.invalid_state(
                "Complete documents and resend to Pusat before receive.",
                details={"completionRequestStatus": "PENDING"},
            )
        self.status = InternalStatus.IN_PROGRESS
        self.updated_at = _utcnow()
        if is_pusat_unit(self.handling_unit_id):
            self._mark_pusat_handled()
        self._append_history(
            event_type=HistoryEventType.RECEIVED,
            actor_id=actor_id,
            actor_unit_id=actor_unit_id,
            note=note or "Diterima untuk ditangani",
            source_unit_id=self.handling_unit_id,
            target_unit_id=self.handling_unit_id,
        )
        if emit_review:
            self._append_history(
                event_type=HistoryEventType.REVIEW,
                actor_id=actor_id,
                actor_unit_id=actor_unit_id,
                note="Peninjauan dimulai",
                source_unit_id=self.handling_unit_id,
                target_unit_id=self.handling_unit_id,
            )

    def _clear_pending_withdraw_request(self) -> None:
        if self.withdraw_request_status != WithdrawRequestStatus.PENDING:
            return
        self.withdraw_request_status = None
        self.withdraw_request_reason = None
        self.withdraw_requested_by = None
        self.withdraw_requested_at = None
        self.withdraw_decided_by = None
        self.withdraw_decided_at = None
        self.withdraw_decision_reason = None

    def return_for_completion(
        self,
        *,
        actor_id: str,
        reason: str,
        actor_unit_id: str | None = None,
    ) -> None:
        """Pusat returns Handling to the owner branch — documents incomplete.

        Not WITHDRAWN. Ticket stays alive at ASSIGNED on the owner unit.
        """
        if self.status not in (InternalStatus.ASSIGNED, InternalStatus.IN_PROGRESS):
            raise err.invalid_state(
                "Return for completion requires ASSIGNED or IN_PROGRESS.",
                details={"status": self.status.value},
            )
        if is_pusat_unit(self.owner_unit_id) or not is_pusat_unit(
            self.handling_unit_id
        ):
            raise err.invalid_state(
                "Return for completion is only for branch-owned tickets at Pusat."
            )
        if self.completion_request_status == CompletionRequestStatus.PENDING:
            raise err.conflict(
                "COMPLETION_REQUEST_PENDING",
                "Documents were already requested from the branch.",
            )
        reason_text = (reason or "").strip()
        if not reason_text:
            raise err.validation(
                "reason is required to return for completion",
                details={"field": "reason"},
            )
        now = _utcnow()
        source = self.handling_unit_id
        self._clear_pending_withdraw_request()
        self.handling_unit_id = self.owner_unit_id
        self.status = InternalStatus.ASSIGNED
        self.completion_request_status = CompletionRequestStatus.PENDING
        self.completion_return_reason = reason_text
        self.completion_returned_by = actor_id
        self.completion_returned_at = now
        self._mark_pusat_handled()
        self.updated_at = now
        self._append_history(
            event_type=HistoryEventType.RETURNED_FOR_COMPLETION,
            actor_id=actor_id,
            actor_unit_id=actor_unit_id,
            note=reason_text,
            source_unit_id=source,
            target_unit_id=self.owner_unit_id,
        )

    def resend_to_pusat(
        self,
        *,
        actor_id: str,
        actor_unit_id: str | None = None,
        note: str | None = None,
    ) -> None:
        """Branch resends to Pusat after completing documents."""
        if self.completion_request_status != CompletionRequestStatus.PENDING:
            raise err.conflict(
                "NO_PENDING_COMPLETION_REQUEST",
                "Ticket is not waiting for document completion.",
            )
        if self.status != InternalStatus.ASSIGNED:
            raise err.invalid_state(
                "Resend to Pusat requires status ASSIGNED.",
                details={"status": self.status.value},
            )
        if self.handling_unit_id != self.owner_unit_id or is_pusat_unit(
            self.owner_unit_id
        ):
            raise err.invalid_state(
                "Resend to Pusat requires Handling back at the owner branch."
            )
        note_text = (note or "").strip()
        if not note_text:
            raise err.validation(
                "note is required to resend to Pusat",
                details={"field": "note"},
            )
        now = _utcnow()
        source = self.handling_unit_id
        self.handling_unit_id = _CANONICAL_PUSAT_UNIT
        self.status = InternalStatus.ASSIGNED
        self.completion_request_status = None
        self.updated_at = now
        self._append_history(
            event_type=HistoryEventType.RESENT_TO_PUSAT,
            actor_id=actor_id,
            actor_unit_id=actor_unit_id,
            note=note_text,
            source_unit_id=source,
            target_unit_id=_CANONICAL_PUSAT_UNIT,
        )

    def withdraw(
        self,
        *,
        actor_id: str,
        reason: str,
        actor_unit_id: str | None = None,
    ) -> None:
        """Branch (or owner unit) cancels before Pusat receives — no Pusat notify."""
        if self.status not in (InternalStatus.CREATED, InternalStatus.ASSIGNED):
            raise err.invalid_state(
                "Direct withdraw is only allowed before receive.",
                details={"status": self.status.value},
            )
        reason_text = (reason or "").strip()
        if not reason_text:
            raise err.validation(
                "reason is required to withdraw",
                details={"field": "reason"},
            )
        now = _utcnow()
        self.status = InternalStatus.WITHDRAWN
        self.withdrawn_by = actor_id
        self.withdrawn_at = now
        self.withdraw_reason = reason_text
        self.updated_at = now
        self._append_history(
            event_type=HistoryEventType.WITHDRAWN,
            actor_id=actor_id,
            actor_unit_id=actor_unit_id,
            note=reason_text,
        )

    def request_withdraw(
        self,
        *,
        actor_id: str,
        reason: str,
        actor_unit_id: str | None = None,
    ) -> None:
        """After Pusat received: branch asks Pusat to withdraw (ticket stays IN_PROGRESS)."""
        if self.status != InternalStatus.IN_PROGRESS:
            raise err.invalid_state(
                "Withdraw request requires status IN_PROGRESS.",
                details={"status": self.status.value},
            )
        if is_pusat_unit(self.owner_unit_id) or not is_pusat_unit(self.handling_unit_id):
            raise err.invalid_state(
                "Withdraw request is only for branch-owned complaints received by Pusat."
            )
        if self.withdraw_request_status == WithdrawRequestStatus.PENDING:
            raise err.conflict(
                "WITHDRAW_REQUEST_PENDING",
                "A withdraw request is already pending decision.",
            )
        reason_text = (reason or "").strip()
        if not reason_text:
            raise err.validation(
                "reason is required for a withdraw request",
                details={"field": "reason"},
            )
        now = _utcnow()
        self.withdraw_request_status = WithdrawRequestStatus.PENDING
        self.withdraw_request_reason = reason_text
        self.withdraw_requested_by = actor_id
        self.withdraw_requested_at = now
        self.withdraw_decided_by = None
        self.withdraw_decided_at = None
        self.withdraw_decision_reason = None
        self.updated_at = now
        self._append_history(
            event_type=HistoryEventType.WITHDRAW_REQUESTED,
            actor_id=actor_id,
            actor_unit_id=actor_unit_id,
            note=reason_text,
        )

    def decide_withdraw_request(
        self,
        *,
        decision: WithdrawRequestStatus,
        actor_id: str,
        actor_unit_id: str | None = None,
        reason: str | None = None,
    ) -> None:
        if self.withdraw_request_status != WithdrawRequestStatus.PENDING:
            raise err.conflict(
                "NO_PENDING_WITHDRAW_REQUEST",
                "No pending withdraw request to decide.",
            )
        if self.status != InternalStatus.IN_PROGRESS:
            raise err.invalid_state(
                "Withdraw decision requires status IN_PROGRESS.",
                details={"status": self.status.value},
            )
        now = _utcnow()
        if decision == WithdrawRequestStatus.REJECTED:
            reason_text = (reason or "").strip()
            if not reason_text:
                raise err.validation(
                    "reason is required when rejecting a withdraw request",
                    details={"field": "reason"},
                )
            self.withdraw_request_status = WithdrawRequestStatus.REJECTED
            self.withdraw_decided_by = actor_id
            self.withdraw_decided_at = now
            self.withdraw_decision_reason = reason_text
            self.updated_at = now
            self._append_history(
                event_type=HistoryEventType.WITHDRAW_REQUEST_REJECTED,
                actor_id=actor_id,
                actor_unit_id=actor_unit_id,
                note=reason_text,
            )
            return
        if decision != WithdrawRequestStatus.APPROVED:
            raise err.validation("Unsupported withdraw request decision")
        reason_text = (
            (reason or "").strip()
            or (self.withdraw_request_reason or "").strip()
        )
        self.withdraw_request_status = WithdrawRequestStatus.APPROVED
        self.withdraw_decided_by = actor_id
        self.withdraw_decided_at = now
        self.withdraw_decision_reason = (reason or "").strip() or None
        self.status = InternalStatus.WITHDRAWN
        self.withdrawn_by = actor_id
        self.withdrawn_at = now
        self.withdraw_reason = reason_text
        self._mark_pusat_handled()
        self.updated_at = now
        self._append_history(
            event_type=HistoryEventType.WITHDRAW_REQUEST_APPROVED,
            actor_id=actor_id,
            actor_unit_id=actor_unit_id,
            note=reason_text,
        )
        self._append_history(
            event_type=HistoryEventType.WITHDRAWN,
            actor_id=actor_id,
            actor_unit_id=actor_unit_id,
            note=reason_text,
        )

    def transition_status(
        self,
        *,
        to_status: str,
        actor_id: str,
        destination_unit_id: str | None = None,
        reason: str | None = None,
        actor_unit_id: str | None = None,
        actor_is_admin: bool = False,
    ) -> None:
        raw = (to_status or "").strip().upper()
        if self.status == InternalStatus.CLOSED:
            raise err.invalid_state("Complaint is CLOSED; status cannot change.")
        try:
            target = InternalStatus(raw)
        except ValueError as exc:
            raise err.validation(
                "Invalid toStatus",
                details={"field": "toStatus", "value": to_status},
            ) from exc
        if target in (InternalStatus.RESOLVED, InternalStatus.CLOSED):
            raise err.conflict(
                "INVALID_TRANSITION",
                "RESOLVED/CLOSED must use Resolve/Acceptance/Close endpoints.",
            )
        if target == InternalStatus.ASSIGNED:
            self.transfer(
                destination_unit_id=destination_unit_id or "",
                actor_id=actor_id,
                actor_unit_id=actor_unit_id,
                actor_is_admin=actor_is_admin,
                reason=reason,
            )
            return
        if target == InternalStatus.IN_PROGRESS:
            self.start_handling(
                actor_id=actor_id, actor_unit_id=actor_unit_id, note=reason
            )
            return
        if not can_transition_status(self.status, target):
            raise err.conflict(
                "INVALID_TRANSITION",
                f"Transition {self.status.value} → {target.value} is not allowed.",
                details={"from": self.status.value, "to": target.value},
            )
        self.status = target
        self.updated_at = _utcnow()

    def _pending_resolution(self) -> ResolutionRecord | None:
        pending = self.resolution
        if pending and pending.status == ResolutionProposalStatus.PENDING_APPROVAL:
            return pending
        return None

    def _assert_propose_unit(
        self, *, actor_unit_id: str | None, actor_is_admin: bool
    ) -> None:
        if actor_is_admin:
            return
        if actor_matches_internal_handling(
            actor_unit_id,
            self.handling_unit_id,
            actor_is_admin=False,
        ):
            return
        raise err.conflict(
            "RESOLUTION_HANDLING_UNIT_REQUIRED",
            "Only the handling unit may propose a resolution.",
            details={
                "actorUnitId": actor_unit_id,
                "handlingUnitId": self.handling_unit_id,
            },
        )

    def _assert_owner_decision_unit(
        self, *, actor_unit_id: str | None, actor_is_admin: bool
    ) -> None:
        if actor_is_admin:
            return
        if not _unit_ids_equal(actor_unit_id, self.owner_unit_id):
            raise err.conflict(
                "RESOLUTION_OWNER_UNIT_REQUIRED",
                "Only the owner unit may accept or reject a resolution proposal.",
                details={
                    "actorUnitId": actor_unit_id,
                    "ownerUnitId": self.owner_unit_id,
                },
            )

    def _assert_not_self_proposal_decision(
        self, *, actor_id: str, pending: ResolutionRecord
    ) -> None:
        if _actor_ids_equal(pending.proposed_by, actor_id):
            raise err.conflict(
                "RESOLUTION_SELF_DECISION_NOT_ALLOWED",
                "The proposer cannot accept or reject their own proposal.",
                details={"proposedBy": pending.proposed_by, "actorId": actor_id},
            )

    def resolve(
        self,
        *,
        action: ResolveAction,
        actor_id: str,
        comment: str,
        resolution_code: str | None = None,
        summary: str | None = None,
        detail: str | None = None,
        rejection_reason: str | None = None,
        actor_unit_id: str | None = None,
        actor_is_admin: bool = False,
    ) -> None:
        comment_text = (comment or "").strip()
        now = _utcnow()
        if action == ResolveAction.PROPOSE:
            if not comment_text:
                raise err.conflict("COMMENT_REQUIRED", "Resolve requires comment.")
            self._assert_propose_unit(
                actor_unit_id=actor_unit_id, actor_is_admin=actor_is_admin
            )
            code = (resolution_code or "").strip() or RESOLUTION_SENTINEL
            summ = (summary or "").strip()
            if not summ:
                raise err.validation(
                    "summary is required for PROPOSE",
                    details={"fields": ["summary"]},
                )
            if self.status in (InternalStatus.CREATED, InternalStatus.ASSIGNED):
                self.start_handling(
                    actor_id=actor_id,
                    actor_unit_id=actor_unit_id,
                    note="Diterima saat usulan penyelesaian",
                    emit_review=False,
                )
            if self.status != InternalStatus.IN_PROGRESS:
                raise err.invalid_state(
                    "Resolve requires status IN_PROGRESS.",
                    details={"status": self.status.value},
                )
            record = ResolutionRecord(
                resolution_id=str(uuid4()),
                resolution_code=code,
                summary=summ,
                status=ResolutionProposalStatus.PENDING_APPROVAL,
                comment=comment_text,
                detail=detail,
                proposed_by=actor_id,
                proposed_at=now,
            )
            self.resolution_history.append(record)
            self.resolution = record
            self.supervisor_approved_after_resolved = False
            self._append_history(
                event_type=HistoryEventType.RESOLUTION,
                actor_id=actor_id,
                actor_unit_id=actor_unit_id,
                note=f"Penyelesaian diusulkan: {summ}",
                payload={"action": "PROPOSE", "resolutionCode": code},
            )
        elif action == ResolveAction.ACCEPT:
            if self.status != InternalStatus.IN_PROGRESS:
                raise err.invalid_state(
                    "Resolve requires status IN_PROGRESS.",
                    details={"status": self.status.value},
                )
            pending = self._pending_resolution()
            if pending is None:
                raise err.conflict(
                    "RESOLUTION_PROPOSAL_REQUIRED",
                    "Accept requires a pending resolution proposal.",
                )
            self._assert_owner_decision_unit(
                actor_unit_id=actor_unit_id, actor_is_admin=actor_is_admin
            )
            self._assert_not_self_proposal_decision(actor_id=actor_id, pending=pending)
            code = (resolution_code or "").strip() or pending.resolution_code
            summ = (summary or "").strip() or pending.summary
            detail = detail if detail is not None else pending.detail
            comment_text = comment_text or pending.comment
            if not comment_text:
                raise err.conflict("COMMENT_REQUIRED", "Resolve requires comment.")
            code = code or RESOLUTION_SENTINEL
            if not summ:
                raise err.validation(
                    "summary is required for ACCEPT",
                    details={"fields": ["summary"]},
                )
            record = ResolutionRecord(
                resolution_id=str(uuid4()),
                resolution_code=code,
                summary=summ,
                status=ResolutionProposalStatus.ACCEPTED,
                comment=comment_text,
                detail=detail,
                proposed_by=pending.proposed_by,
                proposed_at=pending.proposed_at,
                decided_by=actor_id,
                decided_at=now,
            )
            self.resolution_history.append(record)
            self.resolution = record
            self.status = InternalStatus.RESOLVED
            self.supervisor_approved_after_resolved = True
            # Proposing already records handling-unit agreement; stamp uses the proposer.
            acceptance = AcceptanceRecord(
                acceptance_id=str(uuid4()),
                party=AcceptanceParty.HANDLING_UNIT,
                decision=AcceptanceDecision.ACCEPT,
                actor_id=pending.proposed_by or actor_id,
                actor_unit_id=self.handling_unit_id,
                decided_at=now,
                note=None,
            )
            self.acceptance_history.append(acceptance)
            self.handling_unit_acceptance = acceptance
            self.owner_acceptance = None
            self._append_history(
                event_type=HistoryEventType.RESOLUTION,
                actor_id=actor_id,
                actor_unit_id=actor_unit_id,
                note=f"Penyelesaian disetujui: {summ}",
                payload={"action": "ACCEPT", "resolutionCode": code},
            )
            self._append_history(
                event_type=HistoryEventType.HANDLING_UNIT_ACCEPT,
                actor_id=pending.proposed_by or actor_id,
                actor_unit_id=self.handling_unit_id,
                note="Persetujuan unit penanganan tercatat otomatis saat penyelesaian diterima",
            )
        elif action == ResolveAction.REJECT:
            if self.status != InternalStatus.IN_PROGRESS:
                raise err.invalid_state(
                    "Resolve requires status IN_PROGRESS.",
                    details={"status": self.status.value},
                )
            pending = self._pending_resolution()
            if pending is None:
                raise err.conflict(
                    "RESOLUTION_PROPOSAL_REQUIRED",
                    "Reject requires a pending resolution proposal.",
                )
            self._assert_owner_decision_unit(
                actor_unit_id=actor_unit_id, actor_is_admin=actor_is_admin
            )
            self._assert_not_self_proposal_decision(actor_id=actor_id, pending=pending)
            rej = (rejection_reason or "").strip()
            if not rej:
                raise err.validation(
                    "rejectionReason is required when action=REJECT",
                    details={"field": "rejectionReason"},
                )
            comment_text = comment_text or rej
            record = ResolutionRecord(
                resolution_id=str(uuid4()),
                resolution_code=pending.resolution_code,
                summary=pending.summary,
                status=ResolutionProposalStatus.REJECTED,
                comment=comment_text,
                detail=pending.detail,
                proposed_by=pending.proposed_by,
                proposed_at=pending.proposed_at,
                decided_by=actor_id,
                decided_at=now,
                rejection_reason=rej,
            )
            self.resolution_history.append(record)
            self.resolution = record
            self._append_history(
                event_type=HistoryEventType.RESOLUTION,
                actor_id=actor_id,
                actor_unit_id=actor_unit_id,
                note=f"Usulan penyelesaian ditolak: {rej}",
                payload={"action": "REJECT"},
            )
        else:
            raise err.validation("Unsupported resolve action")
        self.updated_at = now

    def record_acceptance(
        self,
        *,
        party: AcceptanceParty,
        decision: AcceptanceDecision,
        actor_id: str,
        actor_unit_id: str | None = None,
        note: str | None = None,
    ) -> None:
        if self.status != InternalStatus.RESOLVED:
            raise err.invalid_state(
                "Acceptance requires status RESOLVED.",
                details={"status": self.status.value},
            )
        cleaned_note = (note or "").strip() or None
        if decision == AcceptanceDecision.REJECT and not cleaned_note:
            raise err.validation(
                "note is required when rejecting",
                details={"field": "note", "decision": decision.value},
            )
        now = _utcnow()
        record = AcceptanceRecord(
            acceptance_id=str(uuid4()),
            party=party,
            decision=decision,
            actor_id=actor_id,
            actor_unit_id=actor_unit_id,
            decided_at=now,
            note=cleaned_note,
        )
        self.acceptance_history.append(record)
        if party == AcceptanceParty.HANDLING_UNIT:
            self.handling_unit_acceptance = record
            event_type = (
                HistoryEventType.HANDLING_UNIT_ACCEPT
                if decision == AcceptanceDecision.ACCEPT
                else HistoryEventType.HANDLING_UNIT_REJECT
            )
        else:
            self.owner_acceptance = record
            event_type = (
                HistoryEventType.OWNER_ACCEPT
                if decision == AcceptanceDecision.ACCEPT
                else HistoryEventType.OWNER_REJECT
            )
        self._append_history(
            event_type=event_type,
            actor_id=actor_id,
            actor_unit_id=actor_unit_id,
            note=cleaned_note,
        )

        if decision == AcceptanceDecision.REJECT:
            self.status = InternalStatus.IN_PROGRESS
            self.handling_unit_acceptance = None
            self.owner_acceptance = None
            self.updated_at = now
            return

        if (
            self.handling_unit_acceptance is not None
            and self.handling_unit_acceptance.decision == AcceptanceDecision.ACCEPT
            and self.owner_acceptance is not None
            and self.owner_acceptance.decision == AcceptanceDecision.ACCEPT
        ):
            self.close(actor_id=actor_id, actor_unit_id=actor_unit_id)
            return

        self.updated_at = now

    def close(
        self, *, actor_id: str, actor_unit_id: str | None = None, note: str | None = None
    ) -> None:
        if self.status == InternalStatus.CLOSED:
            return
        if self.status != InternalStatus.RESOLVED:
            raise err.invalid_state("Close requires status RESOLVED.")
        if (
            self.resolution is None
            or self.resolution.status != ResolutionProposalStatus.ACCEPTED
        ):
            raise err.conflict(
                "CLOSE_CHECKLIST_NOT_MET",
                "Final Resolution Accepted is required before Close.",
            )
        if not self.supervisor_approved_after_resolved:
            raise err.conflict(
                "SUPERVISOR_APPROVAL_REQUIRED",
                "Supervisor Approval after RESOLVED is required.",
            )
        if (
            self.handling_unit_acceptance is None
            or self.handling_unit_acceptance.decision != AcceptanceDecision.ACCEPT
        ):
            raise err.conflict(
                "HANDLING_UNIT_ACCEPTANCE_REQUIRED",
                "Handling Unit must accept before Close.",
            )
        if (
            self.owner_acceptance is None
            or self.owner_acceptance.decision != AcceptanceDecision.ACCEPT
        ):
            raise err.conflict(
                "OWNER_ACCEPTANCE_REQUIRED",
                "Owner must accept before Close.",
            )
        now = _utcnow()
        self.status = InternalStatus.CLOSED
        self.closed_by = actor_id
        self.closed_at = now
        self.updated_at = now
        self._append_history(
            event_type=HistoryEventType.CLOSED,
            actor_id=actor_id,
            actor_unit_id=actor_unit_id,
            note=note or "Ditutup setelah persetujuan kedua unit",
        )

    def to_snapshot(self) -> dict[str, Any]:
        return {
            "complaintId": str(self.complaint_id),
            "complaintNumber": self.complaint_number.value,
            "status": self.status.value,
            "ownerUnitId": self.owner_unit_id,
            "handlingUnitId": self.handling_unit_id,
            "handlingUnitAcceptance": (
                self.handling_unit_acceptance.decision.value
                if self.handling_unit_acceptance
                else None
            ),
            "ownerAcceptance": (
                self.owner_acceptance.decision.value if self.owner_acceptance else None
            ),
        }
