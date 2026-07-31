"""CM Batch 1 application service — FR-001 / FR-002 / FR-003."""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Protocol

from app.core.errors import (
    NotFoundError,
    RateLimitedError,
    ValidationAppError,
)
from app.integrations.customer import (
    CustomerLookupStatus,
    CustomerProvider,
    build_customer_provider,
    mask_identity,
)
from app.modules.cm_batch1 import event_factory as events
from app.modules.cm_batch1.duplicate_config import (
    DEFAULT_DUPLICATE_CONFIG,
    DuplicateConfig,
)
from app.modules.cm_batch1.duplicate_engine import evaluate_candidates
from app.modules.cm_batch1.entities import ComplaintAggregate, DuplicateDecisionRecord, LaterReviewWorkItem
from app.modules.cm_batch1.enumeration import EnumerationGuard
from app.modules.cm_batch1.schemas import (
    AgingComplaintItemResponse,
    ComplaintBatch1Response,
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
    LaterReviewWorkItemResponse,
    SupervisorQueueResponse,
)
from app.modules.cm_batch1.side_effects import (
    NoOpSideEffectRecorder,
    SideEffectRecorder,
)
from app.modules.cm_batch1.store import STORE, Batch1Store


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


DEFAULT_AGING_THRESHOLD_HOURS = 24
DEFAULT_SUPERVISOR_QUEUE_LIMIT = 100


class CmBatch1Service:
    def __init__(
        self,
        *,
        customer_provider: CustomerProvider | None = None,
        guard: EnumerationGuard | None = None,
        store: CmBatch1StoreProtocol | Batch1Store | None = None,
        strict_master: bool = True,
        duplicate_config: DuplicateConfig | None = None,
        scope_allows_candidate: Callable[[ComplaintAggregate], bool] | None = None,
        side_effects: SideEffectRecorder | None = None,
        # Deprecated alias — prefer customer_provider
        master: CustomerProvider | None = None,
    ) -> None:
        self._customers: CustomerProvider = (
            customer_provider
            or master
            or build_customer_provider("stub")
        )
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
                "Exactly one customer key type must be supplied",
                details={"provided": [n for n, _ in provided]},
            )

        outcome, delay = self._guard.check(principal_key)
        if outcome in {"blocked", "alerted"}:
            raise RateLimitedError(
                "Customer search temporarily blocked by enumeration protection",
                details={"enumerationOutcome": outcome, "retryAfterSeconds": delay},
            )
        if outcome == "delayed" and delay > 0:
            time.sleep(min(delay, 0.05))

        key_name, key_value = provided[0]
        assert key_value is not None
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
                    "Master Customer unavailable (Strict mode)",
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
                    CustomerCandidate(
                        customerId=m.customer_id,
                        displayName=m.display_name,
                        maskedIdentity=mask_identity(m.identity_number),
                    )
                    for m in lookup.candidates
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
            candidates=[
                CustomerCandidate(
                    customerId=hit.customer_id,
                    displayName=hit.display_name,
                    maskedIdentity=mask_identity(hit.identity_number),
                )
            ],
            enumerationOutcome="allowed",
            briefProfile={
                "customerId": hit.customer_id,
                "displayName": hit.display_name,
                "status": hit.status,
                "asOf": as_of.isoformat(),
            },
        )

    def confirm_customer(
        self, customer_id: str, *, principal_key: str
    ) -> ConfirmCustomerResponse:
        lookup = self._customers.get_minimal_customer(customer_id)
        if lookup.status == CustomerLookupStatus.UNAVAILABLE:
            raise NotFoundError("Customer not found in Master Customer")
        if lookup.status != CustomerLookupStatus.FOUND or lookup.customer is None:
            raise NotFoundError("Customer not found in Master Customer")
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
            raise NotFoundError("Customer not found")
        row = lookup.customer
        active = self._store.list_active_for_customer(customer_id)
        as_of = self._as_of()
        return Customer360Batch1Response(
            customerId=customer_id,
            profile={
                "customerId": row.customer_id,
                "displayName": row.display_name,
                "status": row.status,
                "customerNumber": row.customer_number,
            },
            activeComplaints=[
                {
                    "complaintId": c.complaint_id,
                    "complaintNumber": c.complaint_number,
                    "status": c.status,
                    "subject": c.subject,
                }
                for c in active
            ],
            complaintCount=len(active),
            asOf=as_of,
        )

    def reject_master_write_back(self) -> None:
        raise ValidationAppError(
            "Customer Master write-back is forbidden (ADR-002 / BR-002)",
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
            raise ValidationAppError("customerId is required")

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
                "Invalid duplicate decision",
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
                    "survivingComplaintId is required for link_existing",
                    details={"decision": decision},
                )
            existing = self._store.get(surviving)
            if existing is None:
                raise NotFoundError("Surviving Complaint not found")
            customer_id = customer_id or existing.customer_id

        elif decision == "override":
            if not customer_id:
                raise ValidationAppError(
                    "customerId is required for override",
                    details={"decision": decision},
                )
            justification = (body.justification or "").strip()
            if len(justification) < cfg.minimum_justification_length:
                raise ValidationAppError(
                    "Override justification is required (Reason Required)",
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
                    "customerId is required for blocked",
                    details={"decision": decision},
                )
            hard_block = True

        else:
            if surviving:
                existing = self._store.get(surviving)
                if existing is None:
                    raise NotFoundError("Surviving Complaint not found")
                customer_id = customer_id or existing.customer_id
            if not customer_id:
                raise ValidationAppError(
                    "customerId is required for recommend_only",
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
                "workItemStatus must be OPEN, CLOSED, or ALL",
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
                "Hard Block: duplicate policy prevents new Complaint create",
                details={
                    "duplicateCheckResult": "blocked",
                    "candidates": check.candidates,
                },
            )

        justification = (body.duplicate_override_justification or "").strip()
        if len(justification) < cfg.minimum_justification_length:
            raise ValidationAppError(
                "Duplicate Warning: override justification is required",
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
    ) -> ComplaintBatch1Response:
        if not request_id or not request_id.strip():
            raise ValidationAppError("Request Id (Idempotency-Key) is required")

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
            raise ValidationAppError("customerId is required")

        # TD-CM-001 / EX-D / FR-002 AC1 — confirm lock required before new create.
        lock_principal = (principal_key or actor_id or "").strip()
        if not lock_principal:
            raise ValidationAppError(
                "principal key is required to enforce customer confirm lock",
                details={"field": "principalKey"},
            )
        locked_customer_id = self._store.get_confirmed(lock_principal)
        customer_id = body.customer_id.strip()
        if locked_customer_id is None or locked_customer_id != customer_id:
            raise ValidationAppError(
                "CustomerId must be confirmed/locked for this actor before create",
                details={
                    "customerId": customer_id,
                    "lockedCustomerId": locked_customer_id,
                    "principalKey": lock_principal,
                },
            )

        existence = self._customers.exists(body.customer_id)
        if existence.status == CustomerLookupStatus.UNAVAILABLE and self.strict_master:
            raise ValidationAppError(
                "Master Customer unavailable (Strict mode) — create rejected"
            )
        if (
            existence.status == CustomerLookupStatus.NOT_FOUND
            and self.strict_master
        ):
            raise ValidationAppError(
                "customerId must be a verified Master Customer id",
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

        dup_result = self._enforce_duplicate_on_create(body)

        row, created = self._store.create(
            customer_id=customer_id,
            category=body.category.strip(),
            channel=body.channel.strip(),
            subject=body.subject.strip(),
            description=body.description.strip(),
            priority=(body.priority or "MEDIUM").strip(),
            created_by=actor_id,
            request_id=cleaned_request_id,
            channel_message_id=cleaned_channel,
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

        self._side_effects.record(
            events.complaint_created(
                complaint_id=row.complaint_id,
                complaint_number=row.complaint_number,
                customer_id=row.customer_id,
                request_id=cleaned_request_id,
                channel_message_id=cleaned_channel,
                actor_id=actor_id,
                created_at=row.created_at,
                recording_unit_id=body.recording_unit_id,
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
            raise NotFoundError("Complaint not found")
        return self._to_complaint_response(row, replayed=False)

    @staticmethod
    def _to_complaint_response(
        row: ComplaintAggregate, *, replayed: bool
    ) -> ComplaintBatch1Response:
        return ComplaintBatch1Response(
            complaintId=row.complaint_id,
            complaintNumber=row.complaint_number,
            status="REGISTERED",
            customerId=row.customer_id,
            caseCreated=False,
            replayed=replayed,
            category=row.category,
            channel=row.channel,
            subject=row.subject,
            priority=row.priority,
            createdAt=row.created_at,
        )
