"""CM Batch 1 application service — FR-001 / FR-002 / FR-003."""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from datetime import UTC, date, datetime, timedelta
from typing import Any, Protocol
from zoneinfo import ZoneInfo

from app.core.authorization.principal import Principal
from app.core.authorization.visibility import (
    DEFAULT_PUSAT_UNIT_CODES,
    is_pusat_unit,
    resolve_row_visibility,
)
from app.core.config import Settings, get_settings
from app.core.errors import (
    InvalidStateError,
    NotFoundError,
    RateLimitedError,
    ValidationAppError,
)
from app.core.user_messages import m
from app.integrations.customer import (
    CustomerLookupStatus,
    CustomerProvider,
    MinimalCustomer,
    build_customer_provider,
    mask_identity,
)
from app.integrations.directory import NullUserDirectory, UserDirectory
from app.modules.cm_batch1 import event_factory as events
from app.modules.cm_batch1.customer_search_key import validate_customer_search_key
from app.modules.cm_batch1.duplicate_config import (
    DEFAULT_DUPLICATE_CONFIG,
    DuplicateConfig,
)
from app.modules.cm_batch1.duplicate_engine import evaluate_candidates
from app.modules.cm_batch1.entities import (
    ComplaintAggregate,
    DuplicateDecisionRecord,
    LaterReviewWorkItem,
)
from app.modules.cm_batch1.enumeration import EnumerationGuard
from app.modules.cm_batch1.intake_narrative import (
    append_cancellation_note,
    append_hq_acceptance_note,
    append_hq_arrival_note,
    append_hq_completion_note,
    append_hq_return_note,
    append_re_escalation_reason,
    append_rejection_note,
    append_supervisor_note,
    has_escalation_reason,
    has_intake_note,
    parse_intake_description,
)
from app.modules.cm_batch1.predicates import is_closed
from app.modules.cm_batch1.schemas import (
    AgingComplaintItemResponse,
    ComplaintBatch1Response,
    ComplaintSlaView,
    ConfirmCustomerResponse,
    CreateComplaintBatch1Request,
    Customer360Batch1Response,
    CustomerCandidate,
    CustomerSearchRequest,
    CustomerSearchResponse,
    DuplicateCheckRequest,
    DuplicateCheckResponse,
    DuplicateDecisionRequest,
    DuplicateDecisionResponse,
    HqAcceptAndScheduleRequest,
    HqAcceptRequest,
    HqCompleteRequest,
    HqReturnRequest,
    HqScheduleArrivalRequest,
    IntakeEscalationDecisionRequest,
    IntakeEscalationRequestBody,
    LaterReviewWorkItemResponse,
    SupervisorQueueResponse,
    UserWorkStatsResponse,
)
from app.modules.cm_batch1.side_effects import (
    NoOpSideEffectRecorder,
    SideEffectRecorder,
)
from app.modules.cm_batch1.sla import resolve_complaint_sla
from app.modules.cm_batch1.store import STORE, Batch1Store


def _candidate_from_minimal(customer: MinimalCustomer) -> CustomerCandidate:
    """Operator-facing candidate: full customer number, mask kept for compatibility."""
    phone = (customer.phone or customer.reference_number or "").strip() or None
    return CustomerCandidate(
        customerId=customer.customer_id,
        displayName=customer.display_name,
        customerNumber=customer.customer_number,
        maskedIdentity=mask_identity(customer.identity_number),
        phone=phone,
    )


class CmBatch1StoreProtocol(Protocol):
    def confirm(self, principal_key: str, customer_id: str) -> None: ...

    def get_confirmed(self, principal_key: str) -> str | None: ...

    def get_idempotent(self, request_id: str) -> ComplaintAggregate | None: ...

    def get_by_channel_message(self, message_id: str) -> ComplaintAggregate | None: ...

    def resolve_create_keys(
        self,
        request_id: str,
        channel_message_id: str | None,
    ) -> ComplaintAggregate | None: ...

    def ensure_request_alias(self, request_id: str, complaint_id: str) -> None: ...

    def ensure_channel_alias(
        self, channel_message_id: str, complaint_id: str
    ) -> None: ...

    def get(self, complaint_id: str) -> ComplaintAggregate | None: ...

    def list_active_for_customer(self, customer_id: str) -> list[ComplaintAggregate]: ...

    def count_for_customer(self, customer_id: str) -> int: ...

    def list_for_customer(
        self, customer_id: str, *, limit: int = 50
    ) -> list[ComplaintAggregate]: ...

    def create(
        self,
        *,
        customer_id: str,
        category: str,
        channel: str,
        subject: str,
        description: str,
        priority: str,
        created_by: str | None,
        request_id: str,
        channel_message_id: str | None,
        status: str = "REGISTERED",
        intake_disposition: str | None = None,
        owning_unit_id: str | None = None,
        proposed_arrival_date: date | None = None,
        proposed_arrival_time: str | None = None,
        proposed_by: str | None = None,
    ) -> tuple[ComplaintAggregate, bool]: ...

    def commit(self) -> None: ...

    def find_duplicate_candidates(
        self,
        *,
        customer_id: str,
        since: datetime,
        limit: int,
    ) -> list[ComplaintAggregate]: ...

    def save_duplicate_decision(
        self,
        *,
        customer_id: str,
        decision: str,
        surviving_complaint_id: str | None,
        source_complaint_id: str | None,
        justification: str | None,
        staging_token: str | None,
        warning: bool,
        hard_block: bool,
        policy_version: str,
        candidate_snapshot: str | None,
        actor_id: str | None,
        later_review_work_item_id: str | None,
    ) -> DuplicateDecisionRecord: ...

    def get_duplicate_history(
        self, *, customer_id: str, limit: int = 50
    ) -> list[DuplicateDecisionRecord]: ...

    def create_later_review_work_item(
        self,
        *,
        customer_id: str,
        reason: str,
        complaint_id: str | None = None,
    ) -> str: ...

    def list_later_review_items(
        self, *, status: str | None = "OPEN", limit: int = 100
    ) -> list[LaterReviewWorkItem]: ...

    def list_aging_without_case(
        self, *, older_than: datetime, limit: int = 100
    ) -> list[ComplaintAggregate]: ...

    def list_complaints(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        keyword: str | None = None,
        priority: str | None = None,
        category: str | None = None,
        status: str | None = None,
        intake_disposition: str | None = None,
        created_by: str | None = None,
        decided_by: str | None = None,
        visibility: str | None = None,
        actor_id: str | None = None,
        org_unit_id: str | None = None,
        pusat_unit_codes: frozenset[str] | None = None,
    ) -> tuple[list[ComplaintAggregate], int]: ...

    def work_stats_for_user(self, user_key: str) -> dict[str, int]: ...

    def update_intake_disposition(
        self,
        complaint_id: str,
        *,
        intake_disposition: str,
        description: str | None = None,
        priority: str | None = None,
        decided_by: str | None = None,
        clear_proposed: bool = False,
    ) -> ComplaintAggregate | None: ...

    def propose_arrival(
        self,
        complaint_id: str,
        *,
        proposed_date: date,
        proposed_time: str,
        proposed_by: str | None,
    ) -> ComplaintAggregate | None: ...

    def clear_proposed_arrival(self, complaint_id: str) -> ComplaintAggregate | None: ...

    def accept_at_hq(
        self,
        complaint_id: str,
        *,
        hq_accepted_at: datetime,
        description: str | None = None,
        intake_disposition: str | None = None,
    ) -> ComplaintAggregate | None: ...

    def schedule_hq_arrival(
        self,
        complaint_id: str,
        *,
        arrival_date: date,
        arrival_time: str,
        description: str | None = None,
        intake_disposition: str | None = None,
        destination_unit_id: str | None = None,
        destination_set_by: str | None = None,
    ) -> ComplaintAggregate | None: ...

    def accept_and_schedule_at_hq(
        self,
        complaint_id: str,
        *,
        hq_accepted_at: datetime,
        arrival_date: date,
        arrival_time: str,
        description: str,
        intake_disposition: str = "HQ_SCHEDULED",
        destination_unit_id: str | None = None,
        destination_set_by: str | None = None,
    ) -> ComplaintAggregate | None: ...

    def complete_at_hq(
        self,
        complaint_id: str,
        *,
        description: str,
        intake_disposition: str = "HQ_CLOSED",
        closed_by: str | None = None,
    ) -> ComplaintAggregate | None: ...


DEFAULT_AGING_THRESHOLD_HOURS = 24
DEFAULT_SUPERVISOR_QUEUE_LIMIT = 100


def _is_hhmm(value: str) -> bool:
    parts = value.split(":")
    if len(parts) != 2:
        return False
    try:
        hour = int(parts[0])
        minute = int(parts[1])
    except ValueError:
        return False
    return 0 <= hour <= 23 and 0 <= minute <= 59


_OPERATOR_TZ = ZoneInfo("Asia/Jakarta")


def _operator_today() -> date:
    """Calendar 'today' for advisory slot validation — lab operators are WIB.

    Do not use ``datetime.now(UTC).date()``: between 00:00–07:00 WIB the UTC
    date is still yesterday, so a local-yesterday proposal would incorrectly
    pass a UTC past-check.
    """
    return datetime.now(_OPERATOR_TZ).date()


def _validate_proposed_arrival(
    proposed_date: date | None, proposed_time: str | None
) -> None:
    """Branch-proposed slot is advisory only — format + not-in-the-past only.

    Grid alignment / working-day / holiday checks live in the HQ schedule
    availability endpoint (UI-side guidance); the escalation write path does
    not depend on that module.
    """
    if proposed_date is None and proposed_time is None:
        return
    if proposed_date is None or not (proposed_time or "").strip():
        raise ValidationAppError(
            "proposedArrivalDate and proposedArrivalTime must be provided together",
            details={"field": "proposedArrivalDate"},
        )
    if not _is_hhmm(proposed_time):
        raise ValidationAppError(
            "proposedArrivalTime must be HH:MM",
            details={"field": "proposedArrivalTime"},
        )
    if proposed_date < _operator_today():
        raise ValidationAppError(
            "proposedArrivalDate cannot be in the past",
            details={"field": "proposedArrivalDate"},
        )


def _validate_hq_destination_unit(value: str | None, *, required: bool) -> str | None:
    """Destination must be a Pusat unit — CRO, Sekretariat or a Suban.

    Existence/active checks belong to the org directory (router boundary via
    ``OrgUnitResolver.resolve_active_unit_code``); this is the domain rule.
    """
    cleaned = (value or "").strip()
    if not cleaned:
        if required:
            raise ValidationAppError(
                "destinationUnitId is required",
                details={"field": "destinationUnitId"},
            )
        return None
    if not is_pusat_unit(cleaned):
        raise ValidationAppError(
            "destinationUnitId must be a Pusat unit",
            details={"field": "destinationUnitId", "value": cleaned},
        )
    return cleaned


def _arrival_history_body(
    *,
    row: ComplaintAggregate,
    arrival_date: date,
    arrival_time: str,
    destination_unit_id: str | None,
    note: str | None,
) -> str:
    """One history entry: when, where, why it moved off the branch proposal.

    Pusat informs the taxpayer itself, so the branch only ever reads this —
    and the branch still gets asked "why 13:00, we proposed 09:00?". The
    proposal is cleared on decision, so if the shift is not written down here
    it is gone.
    """
    lines = [f"{arrival_date.isoformat()} {arrival_time}"]
    if destination_unit_id:
        lines.append(f"Unit tujuan: {destination_unit_id}")
    proposed_date = row.proposed_arrival_date
    proposed_time = (row.proposed_arrival_time or "").strip()
    shifted = proposed_date is not None and (
        proposed_date != arrival_date or proposed_time != arrival_time
    )
    if shifted:
        lines.append(
            f"Usulan cabang {proposed_date.isoformat()} {proposed_time} "
            f"digeser Pusat ke {arrival_date.isoformat()} {arrival_time}."
        )
    if note:
        lines.append(note)
    return "\n".join(lines)


def _aggregate_status(raw: str | None) -> str:
    """DEC-025 §3.3 — expose REGISTERED | IN_PROGRESS | CLOSED as stored."""
    status = (raw or "REGISTERED").strip().upper()
    if status in {"REGISTERED", "IN_PROGRESS", "CLOSED"}:
        return status
    return "REGISTERED"


_INTAKE_DECISION_NOTE_MIN = 20


def _require_open_complaint(row: ComplaintAggregate, action: str) -> None:
    """Case may already exist (IN_PROGRESS); only CLOSED blocks HQ routing."""
    if is_closed(row.status):
        raise InvalidStateError(
            f"{action} requires an open complaint",
            details={"status": row.status},
        )


def _supervisor_note_from_intake(reason: str | None) -> str:
    text = (reason or "").strip()
    if len(text) >= _INTAKE_DECISION_NOTE_MIN:
        return text
    suffix = "Disetujui Supervisor ke Pusat pada intake."
    combined = f"{text} {suffix}".strip() if text else suffix
    return combined


class CmBatch1Service:
    def __init__(
        self,
        *,
        customer_provider: CustomerProvider | None = None,
        user_directory: UserDirectory | None = None,
        guard: EnumerationGuard | None = None,
        store: CmBatch1StoreProtocol | Batch1Store | None = None,
        strict_master: bool = True,
        duplicate_config: DuplicateConfig | None = None,
        scope_allows_candidate: Callable[[ComplaintAggregate], bool] | None = None,
        side_effects: SideEffectRecorder | None = None,
        settings: Settings | None = None,
        # Deprecated alias — prefer customer_provider
        master: CustomerProvider | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._customers: CustomerProvider = (
            customer_provider
            or master
            or build_customer_provider("stub")
        )
        self._directory: UserDirectory = user_directory or NullUserDirectory()
        self._guard = guard or EnumerationGuard()
        self._store: CmBatch1StoreProtocol = store or STORE
        self.strict_master = strict_master
        self._dup_config = duplicate_config or DEFAULT_DUPLICATE_CONFIG
        self._scope_allows_candidate = scope_allows_candidate or (
            lambda _complaint: True
        )
        self._side_effects: SideEffectRecorder = (
            side_effects or NoOpSideEffectRecorder()
        )

    @staticmethod
    def _as_of() -> datetime:
        return datetime.now(UTC)

    def search_customer(
        self,
        body: CustomerSearchRequest,
        *,
        principal_key: str,
    ) -> CustomerSearchResponse:
        keys = [
            ("customerNumber", body.customer_number),
            ("identityNumber", body.identity_number),
            ("referenceNumber", body.reference_number),
        ]
        provided = [(name, value) for name, value in keys if value and value.strip()]
        if len(provided) != 1:
            raise ValidationAppError(
                m("customer.exactly_one_key_type"),
                details={"provided": [n for n, _ in provided]},
            )

        outcome, delay = self._guard.check(principal_key)
        if outcome in {"blocked", "alerted"}:
            raise RateLimitedError(
                m("customer.search_blocked_enumeration"),
                details={"enumerationOutcome": outcome, "retryAfterSeconds": delay},
            )
        if outcome == "delayed" and delay > 0:
            time.sleep(min(delay, 0.05))

        key_name, key_value = provided[0]
        assert key_value is not None
        key_check = validate_customer_search_key(key_value)
        if not key_check.ok:
            raise ValidationAppError(
                m(key_check.error_code or "customer.search_key_empty"),
                details={
                    "keyType": key_name,
                    "kind": key_check.kind,
                    "digitCount": key_check.digit_count,
                },
            )
        if key_name == "customerNumber":
            lookup = self._customers.find_by_customer_number(key_value)
        elif key_name == "identityNumber":
            lookup = self._customers.find_by_national_id(key_value)
        else:
            lookup = self._customers.find_by_reference_number(key_value)

        as_of = self._as_of()

        if lookup.status == CustomerLookupStatus.UNAVAILABLE:
            if self.strict_master:
                raise ValidationAppError(
                    m("customer.master_unavailable_strict"),
                    details={"verificationStatus": "degraded"},
                )
            return CustomerSearchResponse(
                verificationStatus="degraded",
                customerId=None,
                asOf=as_of,
                candidates=[],
                enumerationOutcome=outcome if outcome != "delayed" else "delayed",
            )

        if lookup.status == CustomerLookupStatus.NOT_FOUND:
            self._guard.record_failure(principal_key)
            return CustomerSearchResponse(
                verificationStatus="not_found",
                customerId=None,
                asOf=as_of,
                candidates=[],
                enumerationOutcome=outcome if outcome != "delayed" else "delayed",
            )

        if lookup.status == CustomerLookupStatus.AMBIGUOUS:
            self._guard.record_success(principal_key)
            return CustomerSearchResponse(
                verificationStatus="ambiguous",
                customerId=None,
                asOf=as_of,
                candidates=[
                    _candidate_from_minimal(m) for m in lookup.candidates
                ],
                enumerationOutcome="allowed",
            )

        hit = lookup.customer
        assert hit is not None
        self._guard.record_success(principal_key)
        return CustomerSearchResponse(
            verificationStatus="verified",
            customerId=hit.customer_id,
            asOf=as_of,
            candidates=[_candidate_from_minimal(hit)],
            enumerationOutcome="allowed",
            briefProfile={
                "customerId": hit.customer_id,
                "displayName": hit.display_name,
                "status": hit.status,
                "customerNumber": hit.customer_number,
                "asOf": as_of.isoformat(),
            },
        )

    def confirm_customer(
        self, customer_id: str, *, principal_key: str
    ) -> ConfirmCustomerResponse:
        lookup = self._customers.get_minimal_customer(customer_id)
        if lookup.status == CustomerLookupStatus.UNAVAILABLE:
            raise NotFoundError(m("customer.not_in_master"))
        if lookup.status != CustomerLookupStatus.FOUND or lookup.customer is None:
            raise NotFoundError(m("customer.not_in_master"))
        self._store.confirm(principal_key, customer_id)
        self._store.commit()
        return ConfirmCustomerResponse(
            customerId=customer_id,
            locked=True,
            asOf=self._as_of(),
        )

    def customer_360_minimum(self, customer_id: str) -> Customer360Batch1Response:
        lookup = self._customers.get_minimal_customer(customer_id)
        if lookup.status != CustomerLookupStatus.FOUND or lookup.customer is None:
            raise NotFoundError(m("customer.not_found"))
        row = lookup.customer
        active = self._store.list_active_for_customer(customer_id)
        history = self._store.list_for_customer(customer_id, limit=50)
        total = self._store.count_for_customer(customer_id)
        as_of = self._as_of()

        def _brief(c: ComplaintAggregate) -> dict[str, Any]:
            return {
                "complaintId": c.complaint_id,
                "complaintNumber": c.complaint_number,
                "status": c.status,
                "subject": c.subject,
                "category": c.category,
                "channel": c.channel,
                "createdAt": c.created_at.isoformat() if c.created_at else None,
            }

        return Customer360Batch1Response(
            customerId=customer_id,
            profile={
                "customerId": row.customer_id,
                "displayName": row.display_name,
                "customerNumber": row.customer_number,
                "phone": row.phone or row.reference_number,
                "email": row.email,
            },
            activeComplaints=[_brief(c) for c in active],
            complaintHistory=[_brief(c) for c in history],
            complaintCount=total,
            asOf=as_of,
        )

    def reject_master_write_back(self) -> None:
        raise ValidationAppError(
            m("customer.master_writeback_forbidden"),
            details={"operation": "write"},
        )

    def check_duplicates(
        self,
        body: DuplicateCheckRequest,
        *,
        actor_id: str | None = None,
        emit_side_effects: bool = True,
    ) -> DuplicateCheckResponse:
        if not body.customer_id or not body.customer_id.strip():
            raise ValidationAppError(m("complaint.customer_id_required"))

        customer_id = body.customer_id.strip()
        cfg = self._dup_config
        since = datetime.now(UTC) - timedelta(days=cfg.time_window_days)

        try:
            raw = self._store.find_duplicate_candidates(
                customer_id=customer_id,
                since=since,
                limit=max(cfg.candidate_limit * 3, cfg.candidate_limit),
            )
        except Exception:
            work_item_id = self._store.create_later_review_work_item(
                customer_id=customer_id,
                reason="duplicate_check_degraded",
                complaint_id=None,
            )
            if emit_side_effects:
                self._side_effects.record_many(
                    events.duplicate_check_degraded(
                        customer_id=customer_id,
                        work_item_id=work_item_id,
                        actor_id=actor_id,
                        reason="duplicate_check_degraded",
                    )
                )
            self._store.commit()
            return DuplicateCheckResponse(
                warning=False,
                candidates=[],
                degraded=True,
                laterReviewWorkItemId=work_item_id,
            )

        visible = [c for c in raw if self._scope_allows_candidate(c)]
        if raw and not visible:
            return DuplicateCheckResponse(
                warning=False,
                candidates=[],
                degraded=False,
                laterReviewWorkItemId=None,
            )

        scored = evaluate_candidates(
            intake_category=body.category,
            intake_subject=body.subject,
            intake_channel=body.channel,
            candidates=visible,
            config=cfg,
        )
        response = DuplicateCheckResponse(
            warning=len(scored) > 0,
            candidates=[c.as_dict() for c in scored],
            degraded=False,
            laterReviewWorkItemId=None,
        )
        if emit_side_effects and response.warning:
            primary = scored[0].complaint.complaint_id if scored else None
            self._side_effects.record(
                events.duplicate_warned(
                    customer_id=customer_id,
                    candidate_count=len(scored),
                    actor_id=actor_id,
                    aggregate_id=primary,
                )
            )
            self._store.commit()
        return response

    def record_duplicate_decision(
        self,
        body: DuplicateDecisionRequest,
        *,
        actor_id: str | None = None,
    ) -> DuplicateDecisionResponse:
        cfg = self._dup_config
        decision = body.decision
        allowed = {"link_existing", "override", "recommend_only", "blocked"}
        if decision not in allowed:
            raise ValidationAppError(
                m("duplicate.invalid_decision"),
                details={"allowed": sorted(allowed)},
            )

        customer_id = (body.customer_id or "").strip() if body.customer_id else ""
        surviving = (
            body.surviving_complaint_id.strip()
            if body.surviving_complaint_id
            else None
        )
        justification = body.justification
        hard_block = False
        warning = True

        if decision == "link_existing":
            if not surviving:
                raise ValidationAppError(
                    m("duplicate.surviving_id_required_link"),
                    details={"decision": decision},
                )
            existing = self._store.get(surviving)
            if existing is None:
                raise NotFoundError(m("duplicate.surviving_complaint_not_found"))
            customer_id = customer_id or existing.customer_id

        elif decision == "override":
            if not customer_id:
                raise ValidationAppError(
                    m("complaint.customer_id_required_override"),
                    details={"decision": decision},
                )
            justification = (body.justification or "").strip()
            if len(justification) < cfg.minimum_justification_length:
                raise ValidationAppError(
                    m("duplicate.override_justification_reason_required"),
                    details={
                        "minimumLength": cfg.minimum_justification_length,
                        "decision": decision,
                    },
                )

        elif decision == "blocked":
            if not customer_id and surviving:
                existing = self._store.get(surviving)
                if existing is not None:
                    customer_id = existing.customer_id
            if not customer_id:
                raise ValidationAppError(
                    m("complaint.customer_id_required_blocked"),
                    details={"decision": decision},
                )
            hard_block = True

        else:
            if surviving:
                existing = self._store.get(surviving)
                if existing is None:
                    raise NotFoundError(m("duplicate.surviving_complaint_not_found"))
                customer_id = customer_id or existing.customer_id
            if not customer_id:
                raise ValidationAppError(
                    m("complaint.customer_id_required_recommend_only"),
                    details={"decision": decision},
                )

        snapshot = (
            json.dumps({"survivingComplaintId": surviving}) if surviving else None
        )
        rec = self._store.save_duplicate_decision(
            customer_id=customer_id,
            decision=decision,
            surviving_complaint_id=surviving,
            source_complaint_id=None,
            justification=justification,
            staging_token=body.staging_token,
            warning=warning,
            hard_block=hard_block,
            policy_version=cfg.policy_version,
            candidate_snapshot=snapshot,
            actor_id=actor_id,
            later_review_work_item_id=None,
        )
        self._side_effects.record_many(
            events.duplicate_decision_events(
                decision=decision,
                customer_id=customer_id,
                surviving_complaint_id=surviving,
                actor_id=actor_id,
                decision_id=rec.decision_id,
                justification_present=bool((justification or "").strip()),
            )
        )
        self._store.commit()
        return DuplicateDecisionResponse(
            decisionId=rec.decision_id,
            decision=rec.decision,
            customerId=rec.customer_id,
            survivingComplaintId=rec.surviving_complaint_id,
            warning=rec.warning,
            hardBlock=rec.hard_block,
            caseCreated=False,
            policyVersion=rec.policy_version,
            createdAt=rec.created_at,
        )

    def get_duplicate_history(
        self, *, customer_id: str, limit: int = 50
    ) -> list[DuplicateDecisionRecord]:
        return self._store.get_duplicate_history(
            customer_id=customer_id, limit=limit
        )

    def enqueue_later_review(
        self,
        *,
        customer_id: str,
        reason: str,
        complaint_id: str | None = None,
    ) -> str:
        work_item_id = self._store.create_later_review_work_item(
            customer_id=customer_id,
            reason=reason,
            complaint_id=complaint_id,
        )
        self._store.commit()
        return work_item_id

    def get_supervisor_queue(
        self,
        *,
        work_item_status: str = "OPEN",
        aging_hours: int = DEFAULT_AGING_THRESHOLD_HOURS,
        limit: int = DEFAULT_SUPERVISOR_QUEUE_LIMIT,
    ) -> SupervisorQueueResponse:
        """Read-only later-review + no-Case aging visibility (API-513)."""
        status = (work_item_status or "OPEN").strip().upper() or "OPEN"
        if status not in {"OPEN", "ALL", "CLOSED"}:
            raise ValidationAppError(
                m("config.work_item_status_values"),
                details={"workItemStatus": work_item_status},
            )
        hours = max(1, min(int(aging_hours), 8760))
        cap = max(1, min(int(limit), 500))
        now = datetime.now(UTC)
        older_than = now - timedelta(hours=hours)

        later_rows = self._store.list_later_review_items(
            status=status, limit=cap
        )
        aging_rows = self._store.list_aging_without_case(
            older_than=older_than, limit=cap
        )

        def _age_hours(created_at: datetime) -> float:
            created = created_at if created_at.tzinfo else created_at.replace(tzinfo=UTC)
            return round(max(0.0, (now - created).total_seconds() / 3600.0), 2)

        return SupervisorQueueResponse(
            laterReviewItems=[
                LaterReviewWorkItemResponse(
                    workItemId=item.work_item_id,
                    customerId=item.customer_id,
                    complaintId=item.complaint_id,
                    reason=item.reason,
                    status=item.status,
                    createdAt=item.created_at,
                    ageHours=_age_hours(item.created_at),
                )
                for item in later_rows
            ],
            agingComplaints=[
                AgingComplaintItemResponse(
                    complaintId=row.complaint_id,
                    complaintNumber=row.complaint_number,
                    customerId=row.customer_id,
                    status=row.status,
                    subject=row.subject,
                    priority=row.priority,
                    createdAt=row.created_at,
                    ageHours=_age_hours(row.created_at),
                    caseCreated=False,
                )
                for row in aging_rows
            ],
            agingThresholdHours=hours,
            asOf=now,
        )

    def _enforce_duplicate_on_create(
        self, body: CreateComplaintBatch1Request
    ) -> str:
        cfg = self._dup_config
        if not cfg.enforce_on_create:
            return "skipped"

        check = self.check_duplicates(
            DuplicateCheckRequest(
                customerId=body.customer_id,
                category=body.category,
                subject=body.subject,
                channel=body.channel,
            ),
            emit_side_effects=False,
        )
        if check.degraded:
            return "degraded"
        if not check.warning:
            return "none"

        if any(c.get("hardBlock") for c in check.candidates):
            raise ValidationAppError(
                m("duplicate.hard_block_create"),
                details={
                    "duplicateCheckResult": "blocked",
                    "candidates": check.candidates,
                },
            )

        justification = (body.duplicate_override_justification or "").strip()
        if len(justification) < cfg.minimum_justification_length:
            raise ValidationAppError(
                m("duplicate.override_justification_required"),
                details={
                    "duplicateCheckResult": "warned",
                    "minimumLength": cfg.minimum_justification_length,
                    "candidates": check.candidates,
                },
            )
        return "overridden"

    def peek_idempotent(self, request_id: str) -> str | None:
        """Return existing complaint_id for an idempotency key (no writes)."""
        cleaned = (request_id or "").strip()
        if not cleaned:
            return None
        existing = self._store.get_idempotent(cleaned)
        return existing.complaint_id if existing is not None else None

    def peek_by_channel_message(self, message_id: str) -> str | None:
        """Return existing complaint_id for a channel message id (no writes)."""
        cleaned = (message_id or "").strip()
        if not cleaned:
            return None
        existing = self._store.get_by_channel_message(cleaned)
        return existing.complaint_id if existing is not None else None

    def create_complaint(
        self,
        body: CreateComplaintBatch1Request,
        *,
        request_id: str,
        channel_message_id: str | None,
        actor_id: str | None,
        principal_key: str | None = None,
        authorize_replay: Callable[[str], None] | None = None,
        owning_unit_id: str | None = None,
        auto_approve_escalation: bool = False,
    ) -> ComplaintBatch1Response:
        if not request_id or not request_id.strip():
            raise ValidationAppError(m("common.idempotency_key_required"))

        cleaned_request_id = request_id.strip()
        cleaned_channel = (
            channel_message_id.strip() if channel_message_id else None
        )

        # Deterministic replay read (repository owns key reconciliation).
        existing = self._store.resolve_create_keys(
            cleaned_request_id, cleaned_channel
        )
        if existing is not None:
            return self._complete_replay(
                existing,
                request_id=cleaned_request_id,
                channel_message_id=cleaned_channel,
                actor_id=actor_id,
                authorize_replay=authorize_replay,
            )

        if not body.customer_id.strip():
            raise ValidationAppError(m("complaint.customer_id_required"))

        # TD-CM-001 / EX-D / FR-002 AC1 — confirm lock required before new create.
        lock_principal = (principal_key or actor_id or "").strip()
        if not lock_principal:
            raise ValidationAppError(
                m("complaint.principal_key_required_confirm_lock"),
                details={"field": "principalKey"},
            )
        locked_customer_id = self._store.get_confirmed(lock_principal)
        customer_id = body.customer_id.strip()
        if locked_customer_id is None or locked_customer_id != customer_id:
            raise ValidationAppError(
                m("customer.id_must_be_confirmed"),
                details={
                    "customerId": customer_id,
                    "lockedCustomerId": locked_customer_id,
                    "principalKey": lock_principal,
                },
            )

        existence = self._customers.exists(body.customer_id)
        if existence.status == CustomerLookupStatus.UNAVAILABLE and self.strict_master:
            raise ValidationAppError(
                m("customer.master_unavailable_create_rejected")
            )
        if (
            existence.status == CustomerLookupStatus.NOT_FOUND
            and self.strict_master
        ):
            raise ValidationAppError(
                m("complaint.customer_id_verified_master"),
                details={"customerId": body.customer_id},
            )

        for field_name, value in (
            ("category", body.category),
            ("channel", body.channel),
            ("subject", body.subject),
            ("description", body.description),
        ):
            if not value or not str(value).strip():
                raise ValidationAppError(
                    f"{field_name} is required",
                    details={"field": field_name},
                )

        intake_disposition = (body.intake_disposition or "").strip().upper() or None
        initial_status = "REGISTERED"
        desc = body.description.strip()
        if intake_disposition == "BRANCH_CLOSED":
            # Thin BR-009 lab path: branch walk-away close without Case (BQ-011).
            if not has_intake_note(desc):
                raise ValidationAppError(
                    "intake note required for BRANCH_CLOSED",
                    details={
                        "field": "description",
                        "intakeDisposition": "BRANCH_CLOSED",
                        "requiredSection": "Catatan",
                    },
                )
            initial_status = "CLOSED"
        elif intake_disposition == "ESCALATE_PENDING_APPROVAL":
            if not has_escalation_reason(desc):
                raise ValidationAppError(
                    "escalation reason required for ESCALATE_PENDING_APPROVAL",
                    details={
                        "field": "description",
                        "intakeDisposition": "ESCALATE_PENDING_APPROVAL",
                        "requiredSection": "Alasan eskalasi",
                    },
                )
            initial_status = "REGISTERED"
        elif intake_disposition is not None:
            raise ValidationAppError(
                "unsupported intakeDisposition",
                details={"intakeDisposition": body.intake_disposition},
            )
        else:
            # Plain register (Daftarkan) — Catatan wajib agar cabang tahu
            # apa yang sudah diinfokan ke wajib pajak.
            if not has_intake_note(desc):
                raise ValidationAppError(
                    "intake note required for register",
                    details={
                        "field": "description",
                        "requiredSection": "Catatan",
                    },
                )

        if body.proposed_arrival_date is not None or body.proposed_arrival_time:
            if intake_disposition != "ESCALATE_PENDING_APPROVAL":
                raise ValidationAppError(
                    "proposedArrivalDate only allowed when escalating",
                    details={
                        "field": "proposedArrivalDate",
                        "intakeDisposition": body.intake_disposition,
                    },
                )
            _validate_proposed_arrival(
                body.proposed_arrival_date, body.proposed_arrival_time
            )

        dup_result = self._enforce_duplicate_on_create(body)

        unit = (owning_unit_id or body.recording_unit_id or "").strip() or None
        chosen_priority = (body.priority or "").strip() or None
        row, created = self._store.create(
            customer_id=customer_id,
            category=body.category.strip(),
            channel=body.channel.strip(),
            subject=body.subject.strip(),
            description=body.description.strip(),
            priority=chosen_priority or "MEDIUM",
            created_by=actor_id,
            request_id=cleaned_request_id,
            channel_message_id=cleaned_channel,
            status=initial_status,
            intake_disposition=intake_disposition,
            owning_unit_id=unit,
            proposed_arrival_date=body.proposed_arrival_date,
            proposed_arrival_time=(body.proposed_arrival_time or "").strip() or None,
            proposed_by=actor_id,
        )
        assert row.case_created is False

        # Race losers and any post-validate claim miss share the replay pipeline.
        if not created:
            return self._complete_replay(
                row,
                request_id=cleaned_request_id,
                channel_message_id=cleaned_channel,
                actor_id=actor_id,
                authorize_replay=authorize_replay,
            )

        parsed_intake = parse_intake_description(row.description or "")
        self._side_effects.record(
            events.complaint_created(
                complaint_id=row.complaint_id,
                complaint_number=row.complaint_number,
                customer_id=row.customer_id,
                request_id=cleaned_request_id,
                channel_message_id=cleaned_channel,
                actor_id=actor_id,
                created_at=row.created_at,
                recording_unit_id=unit or body.recording_unit_id,
                note=parsed_intake.narrative or None,
                priority=chosen_priority,
            )
        )
        if intake_disposition:
            # Sort above ComplaintRegistered on the dashboard feed when times
            # would otherwise collide (create + escalate is one user action).
            disposition_at = row.created_at
            if (
                intake_disposition == "ESCALATE_PENDING_APPROVAL"
                and disposition_at is not None
            ):
                disposition_at = disposition_at + timedelta(seconds=1)
            self._side_effects.record(
                events.intake_disposition_recorded(
                    complaint_id=row.complaint_id,
                    complaint_number=row.complaint_number,
                    intake_disposition=intake_disposition,
                    actor_id=actor_id,
                    occurred_at=disposition_at,
                    note=(
                        None
                        if intake_disposition == "BRANCH_CLOSED"
                        else parsed_intake.escalation_reason
                    ),
                    priority=chosen_priority,
                )
            )
        if (
            intake_disposition == "ESCALATE_PENDING_APPROVAL"
            and auto_approve_escalation
        ):
            note = _supervisor_note_from_intake(parsed_intake.escalation_reason)
            approved = self._store.update_intake_disposition(
                row.complaint_id,
                intake_disposition="ESCALATE_APPROVED",
                description=append_supervisor_note(row.description or "", note),
                priority=chosen_priority,
                decided_by=actor_id,
            )
            if approved is not None:
                row = approved
            self._side_effects.record(
                events.intake_escalation_decided(
                    complaint_id=row.complaint_id,
                    complaint_number=row.complaint_number,
                    decision="APPROVE",
                    next_disposition="ESCALATE_APPROVED",
                    actor_id=actor_id,
                    note_present=True,
                    priority=row.priority,
                    note=note,
                )
            )
        if dup_result == "overridden":
            override_rec = self._store.save_duplicate_decision(
                customer_id=body.customer_id.strip(),
                decision="override",
                surviving_complaint_id=None,
                source_complaint_id=row.complaint_id,
                justification=(body.duplicate_override_justification or "").strip(),
                staging_token=body.staging_token,
                warning=True,
                hard_block=False,
                policy_version=self._dup_config.policy_version,
                candidate_snapshot=None,
                actor_id=actor_id,
                later_review_work_item_id=None,
            )
            self._side_effects.record_many(
                events.duplicate_decision_events(
                    decision="override",
                    customer_id=body.customer_id.strip(),
                    surviving_complaint_id=row.complaint_id,
                    actor_id=actor_id,
                    decision_id=override_rec.decision_id,
                    justification_present=True,
                )
            )
        self._store.commit()
        resp = self._to_complaint_response(row, replayed=False)
        resp.duplicate_check_result = dup_result
        return resp

    def _complete_replay(
        self,
        row: ComplaintAggregate,
        *,
        request_id: str,
        channel_message_id: str | None,
        actor_id: str | None,
        authorize_replay: Callable[[str], None] | None = None,
    ) -> ComplaintBatch1Response:
        # R3 — every successful replay key resolves to the canonical ComplaintId.
        self._store.ensure_request_alias(request_id, row.complaint_id)
        if channel_message_id:
            self._store.ensure_channel_alias(
                channel_message_id, row.complaint_id
            )
        # R2 — authorize actual resource before commit / outbox / audit / response.
        if authorize_replay is not None:
            authorize_replay(row.complaint_id)
        self._side_effects.record(
            events.create_replayed(
                complaint_id=row.complaint_id,
                request_id=request_id,
                channel_message_id=channel_message_id,
                actor_id=actor_id,
            )
        )
        self._store.commit()
        return self._to_complaint_response(row, replayed=True)

    def get_complaint(self, complaint_id: str) -> ComplaintBatch1Response:
        row = self._store.get(complaint_id)
        if row is None:
            raise NotFoundError(m("complaint.not_found"))
        return self._to_complaint_response(row, replayed=False)

    def decide_intake_escalation(
        self,
        complaint_id: str,
        body: IntakeEscalationDecisionRequest,
        *,
        actor_id: str | None,
    ) -> ComplaintBatch1Response:
        """API-515 — supervisor approve/reject/cancel intake escalate (disposition only)."""
        row = self._store.get(complaint_id)
        if row is None:
            raise NotFoundError(m("complaint.not_found"))

        _require_open_complaint(row, "intake escalation decision")

        current = (row.intake_disposition or "").strip().upper()
        decision = (body.decision or "").strip().upper()
        note = (body.note or "").strip()
        next_description: str | None = None
        next_priority: str | None = None

        if decision == "CANCEL":
            # Batalkan Eskalasi — only before HQ accepted. Bound Case stays.
            if current != "ESCALATE_APPROVED":
                raise InvalidStateError(
                    "batalkan eskalasi only allowed when ESCALATE_APPROVED",
                    details={
                        "status": row.status,
                        "intakeDisposition": row.intake_disposition,
                    },
                )
            if row.hq_accepted_at is not None:
                raise InvalidStateError(
                    "cannot batalkan eskalasi after HQ accepted",
                    details={
                        "intakeDisposition": row.intake_disposition,
                        "hqAcceptedAt": row.hq_accepted_at.isoformat(),
                    },
                )
            if len(note) < 20:
                raise ValidationAppError(
                    "batalkan eskalasi note must be at least 20 characters",
                    details={"field": "note", "minLength": 20, "decision": "CANCEL"},
                )
            next_disp = "ESCALATE_CANCELLED"
            next_description = append_cancellation_note(row.description or "", note)
        elif decision in {"APPROVE", "REJECT"}:
            if current != "ESCALATE_PENDING_APPROVAL":
                raise InvalidStateError(
                    "intake escalation is not awaiting approval",
                    details={
                        "status": row.status,
                        "intakeDisposition": row.intake_disposition,
                    },
                )
            if decision == "APPROVE":
                if len(note) < 20:
                    raise ValidationAppError(
                        "supervisor note for HQ must be at least 20 characters",
                        details={
                            "field": "note",
                            "minLength": 20,
                            "decision": "APPROVE",
                        },
                    )
                priority = (body.priority or "").strip().upper()
                allowed_priority = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
                if priority not in allowed_priority:
                    raise ValidationAppError(
                        "priority required for APPROVE (LOW|MEDIUM|HIGH|CRITICAL)",
                        details={
                            "field": "priority",
                            "decision": "APPROVE",
                            "allowed": sorted(allowed_priority),
                        },
                    )
                next_disp = "ESCALATE_APPROVED"
                next_description = append_supervisor_note(row.description or "", note)
                next_priority = priority
            else:
                if len(note) < 20:
                    raise ValidationAppError(
                        "reject note must be at least 20 characters",
                        details={"field": "note", "minLength": 20},
                    )
                next_disp = "ESCALATE_REJECTED"
                next_description = append_rejection_note(row.description or "", note)
        else:
            raise ValidationAppError(
                "unsupported intake escalation decision",
                details={"decision": body.decision},
            )

        updated = self._store.update_intake_disposition(
            complaint_id,
            intake_disposition=next_disp,
            description=next_description,
            priority=next_priority,
            decided_by=actor_id,
            clear_proposed=decision in {"CANCEL", "REJECT"},
        )
        if updated is None:
            raise NotFoundError(m("complaint.not_found"))

        self._side_effects.record(
            events.intake_escalation_decided(
                complaint_id=updated.complaint_id,
                complaint_number=updated.complaint_number,
                decision=decision,
                next_disposition=next_disp,
                actor_id=actor_id,
                note_present=bool(note),
                priority=updated.priority if decision == "APPROVE" else None,
                note=note,
            )
        )
        self._store.commit()
        return self._to_complaint_response(updated, replayed=False)

    def request_intake_escalation(
        self,
        complaint_id: str,
        body: IntakeEscalationRequestBody,
        *,
        actor_id: str | None,
        auto_approve_escalation: bool = False,
    ) -> ComplaintBatch1Response:
        """Re-ajukan eskalasi setelah CANCELLED/REJECTED — history append-only."""
        row = self._store.get(complaint_id)
        if row is None:
            raise NotFoundError(m("complaint.not_found"))

        _require_open_complaint(row, "intake escalation request")

        current = (row.intake_disposition or "").strip().upper()
        # Idempotent: already awaiting approval again (e.g. double-submit after success).
        if current == "ESCALATE_PENDING_APPROVAL":
            return self._to_complaint_response(row, replayed=False)
        if current not in {
            "ESCALATE_CANCELLED",
            "ESCALATE_REJECTED",
            "RETURNED_TO_BRANCH",
        }:
            raise InvalidStateError(
                "re-escalate only allowed after ESCALATE_CANCELLED, "
                "ESCALATE_REJECTED, or RETURNED_TO_BRANCH",
                details={
                    "status": row.status,
                    "intakeDisposition": row.intake_disposition,
                },
            )
        if row.hq_accepted_at is not None:
            raise InvalidStateError(
                "cannot re-escalate after HQ accepted",
                details={
                    "intakeDisposition": row.intake_disposition,
                    "hqAcceptedAt": row.hq_accepted_at.isoformat(),
                },
            )

        reason = (body.reason or "").strip()
        if len(reason) < 20:
            raise ValidationAppError(
                "re-escalate reason must be at least 20 characters",
                details={"field": "reason", "minLength": 20},
            )

        next_priority: str | None = None
        if body.priority is not None:
            priority = (body.priority or "").strip().upper()
            allowed_priority = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
            if priority not in allowed_priority:
                raise ValidationAppError(
                    "priority must be LOW|MEDIUM|HIGH|CRITICAL",
                    details={
                        "field": "priority",
                        "allowed": sorted(allowed_priority),
                    },
                )
            next_priority = priority

        _validate_proposed_arrival(
            body.proposed_arrival_date, body.proposed_arrival_time
        )

        next_disp = "ESCALATE_PENDING_APPROVAL"
        next_description = append_re_escalation_reason(row.description or "", reason)

        # Re-escalate always drops the stale proposal (if any) — a fresh
        # proposal is set below only when the branch supplied one this time.
        updated = self._store.update_intake_disposition(
            complaint_id,
            intake_disposition=next_disp,
            description=next_description,
            priority=next_priority,
            clear_proposed=True,
        )
        if updated is None:
            raise NotFoundError(m("complaint.not_found"))
        if body.proposed_arrival_date is not None:
            updated = self._store.propose_arrival(
                complaint_id,
                proposed_date=body.proposed_arrival_date,
                proposed_time=(body.proposed_arrival_time or "").strip(),
                proposed_by=actor_id,
            )
            if updated is None:
                raise NotFoundError(m("complaint.not_found"))

        self._side_effects.record(
            events.intake_escalation_decided(
                complaint_id=updated.complaint_id,
                complaint_number=updated.complaint_number,
                decision="RE_ESCALATE",
                next_disposition=next_disp,
                actor_id=actor_id,
                note_present=True,
                priority=updated.priority if next_priority else None,
                note=reason,
            )
        )
        if auto_approve_escalation:
            note = _supervisor_note_from_intake(reason)
            approved = self._store.update_intake_disposition(
                complaint_id,
                intake_disposition="ESCALATE_APPROVED",
                description=append_supervisor_note(updated.description or "", note),
                priority=next_priority,
                decided_by=actor_id,
            )
            if approved is None:
                raise NotFoundError(m("complaint.not_found"))
            updated = approved
            self._side_effects.record(
                events.intake_escalation_decided(
                    complaint_id=updated.complaint_id,
                    complaint_number=updated.complaint_number,
                    decision="APPROVE",
                    next_disposition="ESCALATE_APPROVED",
                    actor_id=actor_id,
                    note_present=True,
                    priority=updated.priority,
                    note=note,
                )
            )
        self._store.commit()
        return self._to_complaint_response(updated, replayed=False)

    def return_from_hq(
        self,
        complaint_id: str,
        body: HqReturnRequest,
        *,
        actor_id: str | None,
    ) -> ComplaintBatch1Response:
        """Pusat menolak/mengembalikan eskalasi ke cabang (sebelum HQ accept)."""
        row = self._store.get(complaint_id)
        if row is None:
            raise NotFoundError(m("complaint.not_found"))
        _require_open_complaint(row, "HQ return")
        current = (row.intake_disposition or "").strip().upper()
        if current != "ESCALATE_APPROVED":
            raise InvalidStateError(
                "HQ return only allowed when ESCALATE_APPROVED",
                details={"intakeDisposition": row.intake_disposition},
            )
        if row.hq_accepted_at is not None:
            raise InvalidStateError(
                "cannot return after HQ accepted — schedule or handle at HQ",
                details={"hqAcceptedAt": row.hq_accepted_at.isoformat()},
            )

        note = (body.note or "").strip()
        if len(note) < 10:
            raise ValidationAppError(
                "HQ return note must be at least 10 characters",
                details={"field": "note", "minLength": 10},
            )
        reason_code = (body.reason_code or "").strip().upper()
        return_body = f"[{reason_code}] {note}"
        next_description = append_hq_return_note(
            row.description or "", return_body
        )
        updated = self._store.update_intake_disposition(
            complaint_id,
            intake_disposition="RETURNED_TO_BRANCH",
            description=next_description,
            decided_by=actor_id,
            clear_proposed=True,
        )
        if updated is None:
            raise NotFoundError(m("complaint.not_found"))

        self._side_effects.record(
            events.hq_returned(
                complaint_id=updated.complaint_id,
                complaint_number=updated.complaint_number,
                actor_id=actor_id,
                reason_code=reason_code,
                note=note,
            )
        )
        self._store.commit()
        return self._to_complaint_response(updated, replayed=False)

    def accept_at_hq(
        self,
        complaint_id: str,
        body: HqAcceptRequest,
        *,
        actor_id: str | None,
    ) -> ComplaintBatch1Response:
        """Pusat menerima eskalasi (tanpa jadwal) — prefer accept_and_schedule_at_hq."""
        row = self._store.get(complaint_id)
        if row is None:
            raise NotFoundError(m("complaint.not_found"))
        _require_open_complaint(row, "HQ accept")
        current = (row.intake_disposition or "").strip().upper()
        if current != "ESCALATE_APPROVED":
            raise InvalidStateError(
                "HQ accept only allowed when ESCALATE_APPROVED",
                details={"intakeDisposition": row.intake_disposition},
            )
        if row.hq_accepted_at is not None:
            raise InvalidStateError(
                "escalation already accepted by HQ",
                details={"hqAcceptedAt": row.hq_accepted_at.isoformat()},
            )

        note = (body.note or "").strip()
        if note and len(note) < 20:
            raise ValidationAppError(
                "HQ accept note must be at least 20 characters when provided",
                details={"field": "note", "minLength": 20},
            )
        accepted_at = datetime.now(UTC)
        accept_text = note or (
            "Pengaduan diterima oleh Pusat untuk penanganan lanjutan."
        )
        next_description = append_hq_acceptance_note(
            row.description or "", accept_text
        )
        updated = self._store.accept_at_hq(
            complaint_id,
            hq_accepted_at=accepted_at,
            description=next_description,
        )
        if updated is None:
            raise NotFoundError(m("complaint.not_found"))

        self._side_effects.record(
            events.hq_accepted(
                complaint_id=updated.complaint_id,
                complaint_number=updated.complaint_number,
                actor_id=actor_id,
                accepted_at=accepted_at,
                note=accept_text,
            )
        )
        self._store.commit()
        return self._to_complaint_response(updated, replayed=False)

    def accept_and_schedule_at_hq(
        self,
        complaint_id: str,
        body: HqAcceptAndScheduleRequest,
        *,
        actor_id: str | None,
    ) -> ComplaintBatch1Response:
        """Terima + jadwalkan sekaligus → HQ_SCHEDULED (cabang informasikan customer)."""
        row = self._store.get(complaint_id)
        if row is None:
            raise NotFoundError(m("complaint.not_found"))
        _require_open_complaint(row, "HQ accept-and-schedule")
        current = (row.intake_disposition or "").strip().upper()
        if current != "ESCALATE_APPROVED":
            raise InvalidStateError(
                "HQ accept-and-schedule only allowed when ESCALATE_APPROVED",
                details={"intakeDisposition": row.intake_disposition},
            )
        if row.hq_accepted_at is not None:
            raise InvalidStateError(
                "escalation already accepted by HQ",
                details={"hqAcceptedAt": row.hq_accepted_at.isoformat()},
            )

        arrival_time = (body.arrival_time or "").strip()
        if not _is_hhmm(arrival_time):
            raise ValidationAppError(
                "arrivalTime must be HH:MM",
                details={"field": "arrivalTime"},
            )
        note = (body.note or "").strip()
        if len(note) < 10:
            raise ValidationAppError(
                "HQ schedule info note must be at least 10 characters",
                details={"field": "note", "minLength": 10},
            )
        destination_unit = _validate_hq_destination_unit(
            body.destination_unit_id, required=True
        )

        accepted_at = datetime.now(UTC)
        accept_text = (
            "Pengaduan diterima Pusat; jadwal kedatangan dan unit tujuan diset, "
            "Pusat yang menginformasikan ke wajib pajak."
        )
        schedule_body = _arrival_history_body(
            row=row,
            arrival_date=body.arrival_date,
            arrival_time=arrival_time,
            destination_unit_id=destination_unit,
            note=note,
        )
        next_description = append_hq_arrival_note(
            append_hq_acceptance_note(row.description or "", accept_text),
            schedule_body,
        )
        updated = self._store.accept_and_schedule_at_hq(
            complaint_id,
            hq_accepted_at=accepted_at,
            arrival_date=body.arrival_date,
            arrival_time=arrival_time,
            description=next_description,
            intake_disposition="HQ_SCHEDULED",
            destination_unit_id=destination_unit,
            destination_set_by=actor_id,
        )
        if updated is None:
            raise NotFoundError(m("complaint.not_found"))

        self._side_effects.record(
            events.hq_accepted(
                complaint_id=updated.complaint_id,
                complaint_number=updated.complaint_number,
                actor_id=actor_id,
                accepted_at=accepted_at,
                note=accept_text,
            )
        )
        self._side_effects.record(
            events.hq_arrival_scheduled(
                complaint_id=updated.complaint_id,
                complaint_number=updated.complaint_number,
                actor_id=actor_id,
                arrival_date=body.arrival_date.isoformat(),
                arrival_time=arrival_time,
                note=schedule_body,
                next_disposition="HQ_SCHEDULED",
                destination_unit_id=updated.hq_destination_unit_id,
                proposed_arrival_date=(
                    row.proposed_arrival_date.isoformat()
                    if row.proposed_arrival_date
                    else None
                ),
                proposed_arrival_time=row.proposed_arrival_time,
            )
        )
        self._store.commit()
        return self._to_complaint_response(updated, replayed=False)

    def schedule_hq_arrival(
        self,
        complaint_id: str,
        body: HqScheduleArrivalRequest,
        *,
        actor_id: str | None,
    ) -> ComplaintBatch1Response:
        """Jadwalkan / ubah jadwal kedatangan (setelah accept atau HQ_SCHEDULED)."""
        row = self._store.get(complaint_id)
        if row is None:
            raise NotFoundError(m("complaint.not_found"))
        _require_open_complaint(row, "HQ schedule")
        current = (row.intake_disposition or "").strip().upper()
        if current not in {"ESCALATE_APPROVED", "HQ_SCHEDULED"}:
            raise InvalidStateError(
                "HQ schedule only allowed when ESCALATE_APPROVED or HQ_SCHEDULED",
                details={"intakeDisposition": row.intake_disposition},
            )
        if row.hq_accepted_at is None:
            raise InvalidStateError(
                "HQ must accept escalation before scheduling arrival",
                details={"hqAcceptedAt": None},
            )

        arrival_time = (body.arrival_time or "").strip()
        if not _is_hhmm(arrival_time):
            raise ValidationAppError(
                "arrivalTime must be HH:MM",
                details={"field": "arrivalTime"},
            )
        note = (body.note or "").strip()
        destination_unit = _validate_hq_destination_unit(
            body.destination_unit_id, required=False
        )
        schedule_body = _arrival_history_body(
            row=row,
            arrival_date=body.arrival_date,
            arrival_time=arrival_time,
            destination_unit_id=destination_unit,
            note=note or None,
        )
        next_description = append_hq_arrival_note(
            row.description or "", schedule_body
        )
        updated = self._store.schedule_hq_arrival(
            complaint_id,
            arrival_date=body.arrival_date,
            arrival_time=arrival_time,
            description=next_description,
            intake_disposition="HQ_SCHEDULED",
            destination_unit_id=destination_unit,
            destination_set_by=actor_id,
        )
        if updated is None:
            raise NotFoundError(m("complaint.not_found"))

        self._side_effects.record(
            events.hq_arrival_scheduled(
                complaint_id=updated.complaint_id,
                complaint_number=updated.complaint_number,
                actor_id=actor_id,
                arrival_date=body.arrival_date.isoformat(),
                arrival_time=arrival_time,
                note=schedule_body,
                next_disposition="HQ_SCHEDULED",
                destination_unit_id=updated.hq_destination_unit_id,
                proposed_arrival_date=(
                    row.proposed_arrival_date.isoformat()
                    if row.proposed_arrival_date
                    else None
                ),
                proposed_arrival_time=row.proposed_arrival_time,
            )
        )
        self._store.commit()
        return self._to_complaint_response(updated, replayed=False)

    def complete_at_hq(
        self,
        complaint_id: str,
        body: HqCompleteRequest,
        *,
        actor_id: str | None,
    ) -> ComplaintBatch1Response:
        """Selesai di Pusat setelah WP dilayani → CLOSED + HQ_CLOSED.

        Kunjungan tetap tampil di kalender hari itu (completed); kapasitas slot dibebaskan.
        """
        row = self._store.get(complaint_id)
        if row is None:
            raise NotFoundError(m("complaint.not_found"))
        _require_open_complaint(row, "HQ complete")
        if row.hq_accepted_at is None:
            raise InvalidStateError(
                "HQ complete only allowed after HQ accepted",
                details={"hqAcceptedAt": None},
            )
        current = (row.intake_disposition or "").strip().upper()
        if current not in {"ESCALATE_APPROVED", "HQ_SCHEDULED"}:
            raise InvalidStateError(
                "HQ complete only allowed when ESCALATE_APPROVED or HQ_SCHEDULED",
                details={"intakeDisposition": row.intake_disposition},
            )
        note = (body.note or "").strip()
        if len(note) < 10:
            raise ValidationAppError(
                "HQ complete note must be at least 10 characters",
                details={"field": "note", "minLength": 10},
            )
        next_description = append_hq_completion_note(row.description or "", note)
        updated = self._store.complete_at_hq(
            complaint_id,
            description=next_description,
            intake_disposition="HQ_CLOSED",
            closed_by=actor_id,
        )
        if updated is None:
            raise NotFoundError(m("complaint.not_found"))
        arrival_date = (
            updated.hq_arrival_date.isoformat() if updated.hq_arrival_date else None
        )
        self._side_effects.record(
            events.hq_completed(
                complaint_id=updated.complaint_id,
                complaint_number=updated.complaint_number,
                actor_id=actor_id,
                note=note,
                arrival_date=arrival_date,
                arrival_time=updated.hq_arrival_time,
            )
        )
        self._store.commit()
        return self._to_complaint_response(updated, replayed=False)

    def list_complaints(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        keyword: str | None = None,
        priority: str | None = None,
        category: str | None = None,
        status: str | None = None,
        intake_disposition: str | None = None,
        created_by: str | None = None,
        decided_by: str | None = None,
        principal: Principal | None = None,
        org_unit_id: str | None = None,
    ) -> tuple[list[ComplaintBatch1Response], int]:
        if principal is not None:
            visibility = resolve_row_visibility(principal).value
            actor_id = str(principal.user_id)
            effective_org = (
                org_unit_id
                if org_unit_id is not None
                else principal.org_unit_id
            )
        else:
            # Unit-test / internal callers without a principal see all rows.
            visibility = "ALL"
            actor_id = None
            effective_org = org_unit_id
        rows, total = self._store.list_complaints(
            page=page,
            page_size=page_size,
            keyword=keyword,
            priority=priority,
            category=category,
            status=status,
            intake_disposition=intake_disposition,
            created_by=created_by,
            decided_by=decided_by,
            visibility=visibility,
            actor_id=actor_id,
            org_unit_id=effective_org,
            pusat_unit_codes=DEFAULT_PUSAT_UNIT_CODES,
        )
        labels = self._customer_labels_for(
            {row.customer_id for row in rows if row.customer_id}
        )
        officers = self._officer_labels_for(
            {row.created_by for row in rows if row.created_by}
        )
        return (
            [
                self._to_complaint_response(
                    row,
                    replayed=False,
                    customer_labels=labels,
                    officer_labels=officers,
                )
                for row in rows
            ],
            total,
        )

    def work_stats_for_user(self, user_key: str) -> UserWorkStatsResponse:
        stats = self._store.work_stats_for_user(user_key)
        return UserWorkStatsResponse.model_validate(stats)

    def _customer_labels_for(
        self, customer_ids: set[str]
    ) -> dict[str, tuple[str | None, str | None]]:
        """Resolve display name + business customer number (not internal UUID)."""
        out: dict[str, tuple[str | None, str | None]] = {}
        for customer_id in customer_ids:
            display_name: str | None = None
            customer_number: str | None = None
            try:
                lookup = self._customers.get_minimal_customer(customer_id)
            except Exception:
                out[customer_id] = (None, None)
                continue
            if (
                lookup.status == CustomerLookupStatus.FOUND
                and lookup.customer is not None
            ):
                display_name = (lookup.customer.display_name or "").strip() or None
                customer_number = (
                    lookup.customer.customer_number or ""
                ).strip() or None
            out[customer_id] = (display_name, customer_number)
        return out

    def _officer_labels_for(self, actor_ids: set[str]) -> dict[str, str]:
        """Resolve intake officer (PIC) names — directory is not ECMP SoR."""
        wanted = {a for a in actor_ids if a}
        if not wanted:
            return {}
        try:
            return self._directory.display_names(wanted)
        except Exception:
            return {}

    def _to_complaint_response(
        self,
        row: ComplaintAggregate,
        *,
        replayed: bool,
        customer_labels: dict[str, tuple[str | None, str | None]] | None = None,
        officer_labels: dict[str, str] | None = None,
    ) -> ComplaintBatch1Response:
        labels = customer_labels
        if labels is None and row.customer_id:
            labels = self._customer_labels_for({row.customer_id})
        display_name, customer_number = (None, None)
        if labels and row.customer_id in labels:
            display_name, customer_number = labels[row.customer_id]
        officers = officer_labels
        if officers is None and row.created_by:
            officers = self._officer_labels_for({row.created_by})
        created_by_name = (
            officers.get(row.created_by) if officers and row.created_by else None
        )
        parsed = parse_intake_description(row.description or "")
        return ComplaintBatch1Response(
            complaintId=row.complaint_id,
            complaintNumber=row.complaint_number,
            status=_aggregate_status(row.status),
            customerId=row.customer_id,
            customerDisplayName=display_name,
            customerNumber=customer_number,
            createdBy=row.created_by,
            createdByName=created_by_name,
            intakeDisposition=row.intake_disposition,
            caseCreated=bool(row.case_created),
            replayed=replayed,
            category=row.category,
            channel=row.channel,
            subject=row.subject,
            description=row.description,
            intakeNarrative=parsed.narrative or None,
            branchResolution=parsed.branch_resolution,
            escalationReason=parsed.escalation_reason,
            supervisorNote=parsed.supervisor_note,
            rejectionNote=parsed.rejection_note,
            cancellationNote=parsed.cancellation_note,
            hqAcceptedAt=row.hq_accepted_at,
            hqArrivalDate=row.hq_arrival_date,
            hqArrivalTime=row.hq_arrival_time,
            hqDestinationUnitId=row.hq_destination_unit_id,
            hqDestinationSetBy=row.hq_destination_set_by,
            hqDestinationSetAt=row.hq_destination_set_at,
            hqAcceptanceNote=parsed.hq_acceptance_note,
            hqArrivalNote=parsed.hq_arrival_note,
            hqReturnNote=parsed.hq_return_note,
            hqCompletionNote=parsed.hq_completion_note,
            proposedArrivalDate=row.proposed_arrival_date,
            proposedArrivalTime=row.proposed_arrival_time,
            proposedBy=row.proposed_by,
            proposedAt=row.proposed_at,
            owningUnitId=row.owning_unit_id,
            priority=row.priority,
            createdAt=row.created_at,
            closedAt=row.closed_at,
            sla=self._sla_view(row),
        )

    def _sla_view(self, row: ComplaintAggregate) -> ComplaintSlaView | None:
        """DEC-031 resolution SLA, computed fresh on every read."""
        sla = resolve_complaint_sla(
            created_at=row.created_at,
            closed_at=row.closed_at,
            status=row.status,
            target_days=self._settings.complaint_resolution_target_days,
            warning_percent=self._settings.complaint_sla_warning_percent,
        )
        if sla is None:
            return None
        return ComplaintSlaView(
            status=sla.status,
            targetDays=sla.target_days,
            dueAt=sla.due_at,
            elapsedDays=sla.elapsed_days,
            remainingDays=sla.remaining_days,
            overdueDays=sla.overdue_days,
            isWarning=sla.is_warning,
        )
