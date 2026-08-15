"""Application service — CAP-008 Mode A Case use cases (Epic 4).

No Notification / Assignment / SLA / Event engines. Audit + Complaint Timeline only.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

from app.core.authorization.principal import Principal
from app.modules.audit.repository import AuditRepository
from app.modules.audit.service import AuditService
from app.modules.cm_case.application.dto import (
    AcceptanceDTO,
    AddCaseCommand,
    CaseDTO,
    CaseSummaryDTO,
    CloseCaseCommand,
    CreateCaseCommand,
    RecordAcceptanceCommand,
    ResolutionDTO,
    ResolveCaseCommand,
    UpdateStatusCommand,
)
from app.modules.cm_case.application.visibility import (
    DEFAULT_PUSAT_UNIT_CODES,
    resolve_case_visibility,
)
from app.modules.cm_case.domain import errors as err
from app.modules.cm_case.domain.aggregate import (
    AcceptanceRecord,
    CaseAggregate,
    ResolutionRecord,
)
from app.modules.cm_case.domain.repositories import CaseRepository, ParentComplaintRef
from app.modules.cm_case.domain.value_objects import (
    MAX_CASES_PER_COMPLAINT,
    AcceptanceDecision,
    AcceptanceParty,
    CaseNumber,
    CaseStatus,
    ResolveAction,
)
from app.modules.timeline.domain.entity import TimelineEntry
from app.modules.timeline.domain.enums import ActorType, AggregateType
from app.modules.timeline.repository import TimelineRepository

HANDLE_CLAIM_REASON = "HANDLE_CLAIM"
HANDLE_REASSIGN_REASON = "HANDLE_REASSIGN"


def _normalize_actor_id(value: str | None) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""
    try:
        return str(UUID(raw))
    except ValueError:
        return raw.casefold()


def _actor_is_complaint_creator(parent: ParentComplaintRef, actor_id: str) -> bool:
    left = _normalize_actor_id(parent.created_by)
    right = _normalize_actor_id(actor_id)
    return bool(left) and left == right


def _ids_equal(left: str | None, right: str | None) -> bool:
    a = _normalize_actor_id(left)
    b = _normalize_actor_id(right)
    return bool(a) and a == b


def _assert_current_handler(case: CaseAggregate, actor_id: str) -> None:
    claimed = (case.handling_claimed_by or "").strip()
    if not claimed:
        raise err.conflict(
            "HANDLING_CLAIM_REQUIRED",
            "Claim handling before working this Case.",
        )
    if not _ids_equal(claimed, actor_id):
        raise err.conflict(
            "HANDLING_CLAIMER_ONLY",
            "Only the current handling officer can do this.",
            details={"handlingClaimedBy": claimed},
        )


class SideEffects(Protocol):
    def record_case_event(
        self,
        *,
        case: CaseAggregate,
        event_name: str,
        title: str,
        actor_id: str,
        actor_unit_id: str | None = None,
        before: dict | None = None,
        after: dict | None = None,
        note: str | None = None,
    ) -> None: ...


class NoOpSideEffects:
    def record_case_event(
        self,
        *,
        case: CaseAggregate,
        event_name: str,
        title: str,
        actor_id: str,
        actor_unit_id: str | None = None,
        before: dict | None = None,
        after: dict | None = None,
        note: str | None = None,
    ) -> None:
        _ = (case, event_name, title, actor_id, actor_unit_id, before, after, note)


class AuditTimelineSideEffects:
    """BR-016 / BR-017 via existing Audit + Timeline (Complaint stream). No Event Engine."""

    def __init__(
        self,
        session,
        *,
        audit: AuditService | None = None,
        timeline: TimelineRepository | None = None,
    ) -> None:
        self._audit = audit or AuditService(AuditRepository(session))
        self._timeline = timeline or TimelineRepository(session)

    def record_case_event(
        self,
        *,
        case: CaseAggregate,
        event_name: str,
        title: str,
        actor_id: str,
        actor_unit_id: str | None = None,
        before: dict | None = None,
        after: dict | None = None,
        note: str | None = None,
    ) -> None:
        actor_uuid: UUID | None = None
        try:
            actor_uuid = UUID(actor_id)
        except ValueError:
            actor_uuid = None

        self._audit.log(
            event_type=event_name,
            entity_type="Case",
            action="CREATE" if event_name == "CaseCreated" else "UPDATE",
            entity_id=case.case_id,
            actor_id=actor_uuid,
            old_values=before,
            new_values=after or case.to_snapshot(),
            metadata={
                "complaintId": case.complaint_id,
                "caseNumber": case.case_number.value,
                "domainEvent": event_name,
                # F4 history rule — "unit mana yang melakukan" alongside actor_id.
                "actorUnitId": actor_unit_id,
                "note": note,
            },
            commit=False,
        )

        try:
            complaint_uuid = UUID(case.complaint_id)
        except ValueError:
            return

        entry = TimelineEntry.create(
            aggregate_type=AggregateType.COMPLAINT.value,
            aggregate_id=complaint_uuid,
            event_type=event_name,
            title=title,
            description=f"Case {case.case_number.value} — {case.status.value}",
            actor_type=ActorType.USER.value,
            actor_id=actor_id,
            metadata={
                "caseId": str(case.case_id),
                "caseNumber": case.case_number.value,
                "caseStatus": case.status.value,
                "actorUnitId": actor_unit_id,
                "note": note,
            },
        )
        self._timeline.add(entry)


def _resolution_dto(r: ResolutionRecord) -> ResolutionDTO:
    return ResolutionDTO(
        resolution_id=r.resolution_id,
        resolution_code=r.resolution_code,
        summary=r.summary,
        status=r.status.value,
        comment=r.comment,
        detail=r.detail,
        customer_impact=r.customer_impact,
        attachment_ids=list(r.attachment_ids),
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


def to_case_dto(case: CaseAggregate) -> CaseDTO:
    return CaseDTO(
        case_id=str(case.case_id),
        case_number=case.case_number.value,
        complaint_id=case.complaint_id,
        customer_id=case.customer_id,
        status=case.status.value,
        case_type=case.case_type,
        subject=case.subject,
        description=case.description,
        priority=case.priority,
        created_at=case.created_at,
        created_by=case.created_by,
        handling_claimed_by=case.handling_claimed_by,
        category=case.category,
        owning_unit_id=case.owning_unit_id,
        owner_unit_id=case.owner_unit_id,
        assigned_user_id=None,
        sla_policy_version_id=case.sla_policy_version_id,
        sla_countdown_active=False,
        cancel_reason=case.cancel_reason.value if case.cancel_reason else None,
        closed_by=case.closed_by,
        closed_at=case.closed_at,
        updated_at=case.updated_at,
        resolution=_resolution_dto(case.resolution) if case.resolution else None,
        resolution_history=[_resolution_dto(r) for r in case.resolution_history],
        complaint_status_after_create=case.complaint_status_after_create,
        handling_unit_acceptance=(
            _acceptance_dto(case.handling_unit_acceptance)
            if case.handling_unit_acceptance
            else None
        ),
        owner_acceptance=(
            _acceptance_dto(case.owner_acceptance) if case.owner_acceptance else None
        ),
        acceptance_history=[_acceptance_dto(a) for a in case.acceptance_history],
    )


class CaseApplicationService:
    def __init__(
        self,
        repository: CaseRepository,
        *,
        side_effects: SideEffects | None = None,
    ) -> None:
        self._repo = repository
        self._effects = side_effects or NoOpSideEffects()

    def create_case(self, cmd: CreateCaseCommand) -> CaseDTO:
        return self._create_under_complaint(cmd)

    def add_case(self, cmd: AddCaseCommand) -> CaseDTO:
        return self._create_under_complaint(
            CreateCaseCommand(
                complaint_id=cmd.complaint_id,
                case_type=cmd.case_type,
                subject=cmd.subject,
                description=cmd.description,
                priority=cmd.priority,
                category=cmd.category,
                destination_unit_id=cmd.destination_unit_id,
                assigned_user_id=cmd.assigned_user_id,
                sla_policy_version_id=cmd.sla_policy_version_id,
                actor_id=cmd.actor_id,
                actor_unit_id=cmd.actor_unit_id,
            )
        )

    def _create_under_complaint(self, cmd: CreateCaseCommand) -> CaseDTO:
        if cmd.assigned_user_id:
            raise err.conflict(
                "ASSIGNED_USER_NOT_ALLOWED_MODE_A",
                "Assigned User is outside Mode A (BQ-006).",
            )
        for field_name, value in (
            ("caseType", cmd.case_type),
            ("subject", cmd.subject),
            ("description", cmd.description),
            ("priority", cmd.priority),
            ("complaintId", cmd.complaint_id),
        ):
            if not (value or "").strip():
                raise err.validation(
                    f"{field_name} is required",
                    details={"field": field_name},
                )

        parent = self._repo.get_parent_complaint(cmd.complaint_id)
        if parent is None:
            raise err.not_found("Parent Complaint does not exist.")
        if parent.status == "CLOSED":
            raise err.conflict(
                "COMPLAINT_CLOSED",
                "Create Case on CLOSED Complaint is rejected.",
            )
        if parent.case_count >= MAX_CASES_PER_COMPLAINT:
            raise err.conflict(
                "MAX_CASES_EXCEEDED",
                "Maximum 5 Cases per Complaint reached (BQ-003).",
            )

        year = datetime.now(UTC).year
        number = CaseNumber(self._repo.next_case_number(year))
        first_case = parent.case_count == 0 and parent.status == "REGISTERED"
        case = CaseAggregate.create(
            complaint_id=parent.complaint_id,
            customer_id=parent.customer_id,
            case_number=number,
            case_type=cmd.case_type,
            subject=cmd.subject,
            description=cmd.description,
            priority=cmd.priority,
            created_by=cmd.actor_id,
            category=cmd.category,
            destination_unit_id=cmd.destination_unit_id,
            # F4 owner rule — snapshot the parent Complaint's owning unit
            # once; never reassigned by any later transition on this Case.
            owner_unit_id=parent.owning_unit_id,
            sla_policy_version_id=cmd.sla_policy_version_id or "MODE-A-BIND-ONLY",
            complaint_became_in_progress=first_case,
        )
        self._repo.save(case)
        if first_case or parent.case_count == 0:
            self._repo.mark_complaint_in_progress(parent.complaint_id)
            if first_case:
                case.complaint_status_after_create = "IN_PROGRESS"
        self._effects.record_case_event(
            case=case,
            event_name="CaseCreated",
            title="Case Created",
            actor_id=cmd.actor_id,
            actor_unit_id=cmd.actor_unit_id,
            after=case.to_snapshot(),
        )
        self._record_handling_claim(
            case=case,
            parent=parent,
            actor_id=cmd.actor_id,
            actor_unit_id=cmd.actor_unit_id,
        )
        self._repo.commit()
        return to_case_dto(case)

    def _record_handling_claim(
        self,
        *,
        case: CaseAggregate,
        parent: ParentComplaintRef,
        actor_id: str,
        actor_unit_id: str | None,
    ) -> None:
        continued = _actor_is_complaint_creator(parent, actor_id)
        event_name = "HandlingContinued" if continued else "HandlingTakenOver"
        title = "Handling continued" if continued else "Handling taken over"
        case.claim_handling(actor_id)
        self._repo.save(case)
        self._effects.record_case_event(
            case=case,
            event_name=event_name,
            title=title,
            actor_id=actor_id,
            actor_unit_id=actor_unit_id,
            after=case.to_snapshot(),
        )

    def get_case(
        self, case_id: str, *, complaint_id_context: str | None = None
    ) -> CaseDTO:
        case = self._repo.get(case_id)
        if case is None:
            raise err.not_found("Case does not exist.")
        if complaint_id_context:
            ctx = complaint_id_context.strip()
            parent = self._repo.get_parent_complaint(ctx)
            if parent is None:
                if case.complaint_id != ctx:
                    raise err.conflict(
                        "CASE_COMPLAINT_MEMBERSHIP_MISMATCH",
                        "CaseId is not a member of the supplied Complaint context.",
                    )
            elif case.complaint_id != parent.complaint_id:
                raise err.conflict(
                    "CASE_COMPLAINT_MEMBERSHIP_MISMATCH",
                    "CaseId is not a member of the supplied Complaint context.",
                )
        return to_case_dto(case)

    def list_cases(
        self,
        principal: Principal,
        *,
        page: int = 1,
        page_size: int = 20,
        complaint_id: str | None = None,
        status: str | None = None,
    ) -> tuple[list[CaseSummaryDTO], int]:
        visibility = resolve_case_visibility(principal)
        rows, total = self._repo.list_summaries(
            visibility=visibility.value,
            actor_id=str(principal.user_id),
            org_unit_id=principal.org_unit_id,
            pusat_unit_codes=DEFAULT_PUSAT_UNIT_CODES,
            complaint_id=complaint_id,
            status=status,
            page=page,
            page_size=page_size,
        )
        numbers = self._repo.complaint_numbers_by_ids(
            [row.complaint_id for row in rows]
        )
        items = [
            CaseSummaryDTO(
                case_id=str(row.id),
                case_number=row.case_number,
                complaint_id=row.complaint_id,
                status=row.status,
                case_type=row.case_type,
                subject=row.subject,
                priority=row.priority,
                created_at=row.created_at,
                created_by=row.created_by,
                handling_claimed_by=row.handling_claimed_by,
                category=row.category,
                owning_unit_id=row.owning_unit_id,
                owner_unit_id=row.owner_unit_id,
                customer_id=row.customer_id,
                complaint_number=numbers.get(str(row.complaint_id)),
            )
            for row in rows
        ]
        return items, total

    def update_status(self, cmd: UpdateStatusCommand) -> CaseDTO:
        reason = (cmd.reason or "").strip().upper()
        # BR-005 E4 — double-claim race: lock the row before reading
        # ``handling_claimed_by`` so two concurrent claims/reassigns cannot
        # both observe the pre-claim state. Only one request wins; the other
        # sees the just-committed claimer once it acquires the lock.
        claims_handling = reason in (HANDLE_CLAIM_REASON, HANDLE_REASSIGN_REASON)
        case = self._require(cmd.case_id, for_update=claims_handling)
        if reason == HANDLE_REASSIGN_REASON:
            if not cmd.actor_can_reassign:
                raise err.conflict(
                    "HANDLING_REASSIGN_FORBIDDEN",
                    "Only Supervisor or Manager can reassign handling.",
                )
            if case.status in (CaseStatus.CLOSED, CaseStatus.CANCELLED):
                raise err.invalid_state("Case is terminal; handling cannot be reassigned.")
            target = (cmd.handling_claimed_by or "").strip()
            parent = self._repo.get_parent_complaint(case.complaint_id)
            if parent is None:
                raise err.not_found("Parent Complaint does not exist.")
            case.claim_handling(target)
            self._repo.save(case)
            self._effects.record_case_event(
                case=case,
                event_name="HandlingTakenOver",
                title="Handling reassigned",
                actor_id=cmd.actor_id,
                actor_unit_id=cmd.actor_unit_id,
                after=case.to_snapshot(),
                note=target,
            )
            self._repo.commit()
            return to_case_dto(case)
        if reason == HANDLE_CLAIM_REASON:
            if case.status in (CaseStatus.CLOSED, CaseStatus.CANCELLED):
                raise err.invalid_state("Case is terminal; handling cannot be claimed.")
            claimed = (case.handling_claimed_by or "").strip()
            if claimed and not _ids_equal(claimed, cmd.actor_id):
                raise err.conflict(
                    "HANDLING_ALREADY_CLAIMED",
                    "Another officer is already handling this Case.",
                    details={"handlingClaimedBy": claimed},
                )
            # Same officer reclaim is idempotent — do not append another
            # HandlingContinued / HandlingTakenOver to intake history.
            if claimed and _ids_equal(claimed, cmd.actor_id):
                return to_case_dto(case)
            parent = self._repo.get_parent_complaint(case.complaint_id)
            if parent is None:
                raise err.not_found("Parent Complaint does not exist.")
            self._record_handling_claim(
                case=case,
                parent=parent,
                actor_id=cmd.actor_id,
                actor_unit_id=cmd.actor_unit_id,
            )
            self._repo.commit()
            return to_case_dto(case)
        target = (cmd.to_status or "").strip().upper()
        if target == "IN_PROGRESS":
            _assert_current_handler(case, cmd.actor_id)
        before = case.to_snapshot()
        if cmd.to_status and cmd.to_status.strip().upper() == "CANCELLED":
            if not (cmd.reason or "").strip() and not cmd.cancel_reason:
                raise err.validation(
                    "reason or cancelReason is required for CANCELLED",
                    details={"fields": ["reason", "cancelReason"]},
                )
        case.transition_status(
            to_status=cmd.to_status,
            actor_id=cmd.actor_id,
            destination_unit_id=cmd.destination_unit_id,
            cancel_reason=cmd.cancel_reason,
            reason=cmd.reason,
            assigned_user_id=cmd.assigned_user_id,
        )
        self._repo.save(case)
        event = "CaseCancelled" if case.status.value == "CANCELLED" else "CaseStatusChanged"
        if case.status.value == "ASSIGNED":
            event = "CaseAssigned"
        elif case.status.value == "IN_PROGRESS":
            event = "CaseWorkStarted"
        self._effects.record_case_event(
            case=case,
            event_name=event,
            title="Case Status Updated",
            actor_id=cmd.actor_id,
            actor_unit_id=cmd.actor_unit_id,
            before=before,
            after=case.to_snapshot(),
            note=cmd.reason,
        )
        if case.status.value in {"CANCELLED", "CLOSED"}:
            self._repo.sync_complaint_status_from_cases(case.complaint_id)
        self._repo.commit()
        return to_case_dto(case)

    def resolve(self, cmd: ResolveCaseCommand) -> CaseDTO:
        case = self._require(cmd.case_id)
        try:
            action = ResolveAction(cmd.action.strip().upper())
        except ValueError as exc:
            raise err.validation(
                "Invalid resolve action",
                details={"field": "action", "value": cmd.action},
            ) from exc
        if action == ResolveAction.PROPOSE:
            _assert_current_handler(case, cmd.actor_id)
        before = case.to_snapshot()
        case.resolve(
            action=action,
            actor_id=cmd.actor_id,
            comment=cmd.comment,
            resolution_code=cmd.resolution_code,
            summary=cmd.summary,
            detail=cmd.detail,
            customer_impact=cmd.customer_impact,
            attachment_ids=list(cmd.attachment_ids or []),
            rejection_reason=cmd.rejection_reason,
            evidence_required=False,  # category evidence policy catalog: NOT SPECIFIED
            actor_unit_id=cmd.actor_unit_id,
        )
        self._repo.save(case)
        self._effects.record_case_event(
            case=case,
            event_name="CaseResolved" if case.status.value == "RESOLVED" else "ResolutionUpdated",
            title="Case Resolution",
            actor_id=cmd.actor_id,
            actor_unit_id=cmd.actor_unit_id,
            before=before,
            after=case.to_snapshot(),
            note=cmd.comment,
        )
        if case.status.value in {"CLOSED", "CANCELLED"}:
            self._repo.sync_complaint_status_from_cases(case.complaint_id)
        self._repo.commit()
        return to_case_dto(case)

    def record_acceptance(self, cmd: RecordAcceptanceCommand) -> CaseDTO:
        """F4 closure rule — Handling Unit / Owner accept or reject a resolution.

        When both parties have ACCEPT, the Case transitions to CLOSED as a
        consequence of the second acceptance (no separate approval step).
        ``close()`` remains for compatibility and still cannot bypass the
        dual-acceptance gate.
        """
        case = self._require(cmd.case_id)
        before = case.to_snapshot()
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
        case.record_acceptance(
            party=party,
            decision=decision,
            actor_id=cmd.actor_id,
            actor_unit_id=cmd.actor_unit_id,
            note=cmd.note,
        )
        self._repo.save(case)
        event_name = (
            "CaseHandlingUnitAccepted"
            if party == AcceptanceParty.HANDLING_UNIT
            and decision == AcceptanceDecision.ACCEPT
            else "CaseOwnerAccepted"
            if party == AcceptanceParty.OWNER and decision == AcceptanceDecision.ACCEPT
            else "CaseHandlingUnitRejected"
            if party == AcceptanceParty.HANDLING_UNIT
            else "CaseOwnerRejected"
        )
        after_acceptance = case.to_snapshot()
        self._effects.record_case_event(
            case=case,
            event_name=event_name,
            title="Case Closure Acceptance",
            actor_id=cmd.actor_id,
            actor_unit_id=cmd.actor_unit_id,
            before=before,
            after=after_acceptance,
            note=cmd.note,
        )
        if case.status.value == "CLOSED":
            self._effects.record_case_event(
                case=case,
                event_name="CaseClosed",
                title="Case Closed",
                actor_id=cmd.actor_id,
                actor_unit_id=cmd.actor_unit_id,
                before=after_acceptance,
                after=case.to_snapshot(),
                note=cmd.note,
            )
            self._repo.sync_complaint_status_from_cases(case.complaint_id)
        self._repo.commit()
        return to_case_dto(case)

    def close(self, cmd: CloseCaseCommand) -> CaseDTO:
        case = self._require(cmd.case_id)
        before = case.to_snapshot()
        case.close(actor_id=cmd.actor_id)
        self._repo.save(case)
        self._effects.record_case_event(
            case=case,
            event_name="CaseClosed",
            title="Case Closed",
            actor_id=cmd.actor_id,
            actor_unit_id=cmd.actor_unit_id,
            before=before,
            after=case.to_snapshot(),
            note=cmd.note,
        )
        # Mode A product rule (2026-08-12): when every Case under the parent is
        # terminal, close the Aggregate. Supersedes BQ-007 "never close parent".
        self._repo.sync_complaint_status_from_cases(case.complaint_id)
        self._repo.commit()
        return to_case_dto(case)

    def _require(self, case_id: str, *, for_update: bool = False) -> CaseAggregate:
        case = self._repo.get(case_id, for_update=for_update)
        if case is None:
            raise err.not_found("Case does not exist.")
        return case
