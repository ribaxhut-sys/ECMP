"""In-memory Aggregate store for CM Batch 1 unit tests / S1 compatibility.

Production path uses :class:`CmBatch1Repository` (SQLAlchemy).
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from threading import Lock

from app.core.authorization.visibility import (
    DEFAULT_PUSAT_UNIT_CODES,
    complaint_visible_for_pusat,
)
from app.modules.cm_batch1.complaint_number import (
    counter_name as complaint_counter_name,
)
from app.modules.cm_batch1.complaint_number import (
    next_complaint_number as format_next_complaint_number,
)
from app.modules.cm_batch1.complaint_number import (
    resolve_unit_code,
)
from app.modules.cm_batch1.entities import (
    ComplaintAggregate,
    DuplicateDecisionRecord,
    IdempotencyRecord,
    LaterReviewWorkItem,
)
from app.modules.cm_batch1.exceptions import ReplayConflict
from app.modules.cm_batch1.predicates import (
    AGGREGATE_STATUSES,
    LIST_INTAKE_DISPOSITION_FILTERS,
    in_escalation_family,
    is_open,
    matches_intake_disposition_filter,
)
from app.modules.cm_batch1.sla import apply_complaint_status


class Batch1Store:
    """Process-local in-memory implementation of the Batch 1 store protocol."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._complaints: dict[str, ComplaintAggregate] = {}
        self._by_number: dict[str, str] = {}
        self._idempotency: dict[str, IdempotencyRecord] = {}
        self._channel_msg: dict[str, IdempotencyRecord] = {}
        self._confirmed: dict[str, str] = {}
        self._decisions: list[DuplicateDecisionRecord] = []
        self._later_reviews: list[LaterReviewWorkItem] = []
        self._counters: dict[str, int] = {}
        self.force_degraded: bool = False

    def reset(self) -> None:
        with self._lock:
            self._complaints.clear()
            self._by_number.clear()
            self._idempotency.clear()
            self._channel_msg.clear()
            self._confirmed.clear()
            self._decisions.clear()
            self._later_reviews.clear()
            self._counters.clear()
            self.force_degraded = False

    def commit(self) -> None:
        """No-op — retained for protocol parity with persistent repository."""

    def confirm(self, principal_key: str, customer_id: str) -> None:
        with self._lock:
            self._confirmed[principal_key] = customer_id

    def get_confirmed(self, principal_key: str) -> str | None:
        with self._lock:
            return self._confirmed.get(principal_key)

    def get_idempotent(self, request_id: str) -> ComplaintAggregate | None:
        with self._lock:
            rec = self._idempotency.get(request_id)
            if rec is None:
                return None
            return self._complaints.get(rec.complaint_id)

    def get_by_channel_message(self, message_id: str) -> ComplaintAggregate | None:
        with self._lock:
            rec = self._channel_msg.get(message_id)
            if rec is None:
                return None
            return self._complaints.get(rec.complaint_id)

    def resolve_create_keys(
        self,
        request_id: str,
        channel_message_id: str | None,
    ) -> ComplaintAggregate | None:
        with self._lock:
            by_req_rec = self._idempotency.get(request_id)
            by_req = (
                self._complaints.get(by_req_rec.complaint_id)
                if by_req_rec is not None
                else None
            )
            by_ch = None
            if channel_message_id:
                by_ch_rec = self._channel_msg.get(channel_message_id)
                if by_ch_rec is not None:
                    by_ch = self._complaints.get(by_ch_rec.complaint_id)
            if by_req is not None and by_ch is not None:
                if by_req.complaint_id != by_ch.complaint_id:
                    raise ReplayConflict(
                        diagnostic_details={
                            "requestId": request_id,
                            "channelMessageId": channel_message_id,
                            "requestComplaintId": by_req.complaint_id,
                            "channelComplaintId": by_ch.complaint_id,
                        }
                    )
                return by_req
            if by_req is not None:
                return by_req
            if by_ch is not None:
                return by_ch
            return None

    def ensure_request_alias(self, request_id: str, complaint_id: str) -> None:
        with self._lock:
            existing = self._idempotency.get(request_id)
            if existing is not None:
                if existing.complaint_id != complaint_id:
                    raise ReplayConflict(
                        diagnostic_details={
                            "requestId": request_id,
                            "requestComplaintId": existing.complaint_id,
                            "canonicalComplaintId": complaint_id,
                        }
                    )
                return
            self._idempotency[request_id] = IdempotencyRecord(
                key=request_id, complaint_id=complaint_id
            )

    def ensure_channel_alias(
        self, channel_message_id: str, complaint_id: str
    ) -> None:
        with self._lock:
            existing = self._channel_msg.get(channel_message_id)
            if existing is not None:
                if existing.complaint_id != complaint_id:
                    raise ReplayConflict(
                        diagnostic_details={
                            "channelMessageId": channel_message_id,
                            "channelComplaintId": existing.complaint_id,
                            "canonicalComplaintId": complaint_id,
                        }
                    )
                return
            self._channel_msg[channel_message_id] = IdempotencyRecord(
                key=channel_message_id, complaint_id=complaint_id
            )

    def get(self, complaint_id: str) -> ComplaintAggregate | None:
        with self._lock:
            return self._complaints.get(complaint_id)

    def list_active_for_customer(self, customer_id: str) -> list[ComplaintAggregate]:
        with self._lock:
            return [
                c
                for c in self._complaints.values()
                if c.customer_id == customer_id and c.status != "CLOSED"
            ]

    def count_for_customer(self, customer_id: str) -> int:
        with self._lock:
            return sum(
                1 for c in self._complaints.values() if c.customer_id == customer_id
            )

    def list_for_customer(
        self, customer_id: str, *, limit: int = 50
    ) -> list[ComplaintAggregate]:
        with self._lock:
            rows = [
                c
                for c in self._complaints.values()
                if c.customer_id == customer_id
            ]
            rows.sort(key=lambda c: c.created_at, reverse=True)
            return rows[: max(1, min(int(limit), 100))]

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
    ) -> tuple[ComplaintAggregate, bool]:
        with self._lock:
            by_req_rec = self._idempotency.get(request_id)
            by_req = (
                self._complaints.get(by_req_rec.complaint_id)
                if by_req_rec is not None
                else None
            )
            by_ch = None
            if channel_message_id:
                by_ch_rec = self._channel_msg.get(channel_message_id)
                if by_ch_rec is not None:
                    by_ch = self._complaints.get(by_ch_rec.complaint_id)
            if by_req is not None and by_ch is not None:
                if by_req.complaint_id != by_ch.complaint_id:
                    raise ReplayConflict(
                        diagnostic_details={
                            "requestId": request_id,
                            "channelMessageId": channel_message_id,
                            "requestComplaintId": by_req.complaint_id,
                            "channelComplaintId": by_ch.complaint_id,
                        }
                    )
                return by_req, False
            if by_req is not None:
                # Bind channel_message_id alias to canonical request owner.
                if channel_message_id:
                    existing_ch = self._channel_msg.get(channel_message_id)
                    if (
                        existing_ch is not None
                        and existing_ch.complaint_id != by_req.complaint_id
                    ):
                        raise ReplayConflict(
                            diagnostic_details={
                                "requestId": request_id,
                                "channelMessageId": channel_message_id,
                                "requestComplaintId": by_req.complaint_id,
                                "channelComplaintId": existing_ch.complaint_id,
                            }
                        )
                    self._channel_msg[channel_message_id] = IdempotencyRecord(
                        key=channel_message_id, complaint_id=by_req.complaint_id
                    )
                return by_req, False
            if by_ch is not None:
                # Bind request_id alias to canonical channel owner (R3).
                existing_alias = self._idempotency.get(request_id)
                if existing_alias is not None and existing_alias.complaint_id != by_ch.complaint_id:
                    raise ReplayConflict(
                        diagnostic_details={
                            "requestId": request_id,
                            "requestComplaintId": existing_alias.complaint_id,
                            "channelComplaintId": by_ch.complaint_id,
                        }
                    )
                self._idempotency[request_id] = IdempotencyRecord(
                    key=request_id, complaint_id=by_ch.complaint_id
                )
                return by_ch, False

            now = datetime.now(UTC)
            unit = (owning_unit_id or "").strip() or None
            unit_code = resolve_unit_code(unit)
            key = complaint_counter_name(
                unit_code, year=now.year, month=now.month
            )
            n = self._counters.get(key, 0) + 1
            self._counters[key] = n
            complaint_id = str(uuid.uuid4())
            complaint_number = format_next_complaint_number(
                owning_unit_id=unit_code, sequence=n, at=now
            )
            initial_status = (status or "REGISTERED").strip().upper() or "REGISTERED"
            if initial_status not in {"REGISTERED", "CLOSED"}:
                initial_status = "REGISTERED"
            disposition = (intake_disposition or "").strip().upper() or None
            row = ComplaintAggregate(
                complaint_id=complaint_id,
                complaint_number=complaint_number,
                customer_id=customer_id,
                category=category,
                channel=channel,
                subject=subject,
                description=description,
                priority=priority,
                status=initial_status,
                closed_at=now if initial_status == "CLOSED" else None,
                intake_disposition=disposition,
                owning_unit_id=unit,
                created_by=created_by,
                case_created=False,
                proposed_arrival_date=proposed_arrival_date,
                proposed_arrival_time=proposed_arrival_time,
                proposed_by=proposed_by if proposed_arrival_date else None,
                proposed_at=now if proposed_arrival_date else None,
            )
            self._complaints[complaint_id] = row
            self._by_number[complaint_number] = complaint_id
            self._idempotency[request_id] = IdempotencyRecord(
                key=request_id, complaint_id=complaint_id
            )
            if channel_message_id:
                self._channel_msg[channel_message_id] = IdempotencyRecord(
                    key=channel_message_id, complaint_id=complaint_id
                )
            return row, True

    def find_duplicate_candidates(
        self,
        *,
        customer_id: str,
        since: datetime,
        limit: int,
    ) -> list[ComplaintAggregate]:
        if self.force_degraded:
            raise RuntimeError("duplicate index unavailable")
        with self._lock:
            rows = [
                c
                for c in self._complaints.values()
                if c.customer_id == customer_id and c.created_at >= since
            ]
            rows.sort(key=lambda c: c.created_at, reverse=True)
            return rows[:limit]

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
    ) -> DuplicateDecisionRecord:
        with self._lock:
            rec = DuplicateDecisionRecord(
                decision_id=str(uuid.uuid4()),
                customer_id=customer_id,
                decision=decision,
                surviving_complaint_id=surviving_complaint_id,
                source_complaint_id=source_complaint_id,
                justification=justification,
                staging_token=staging_token,
                warning=warning,
                hard_block=hard_block,
                policy_version=policy_version,
                candidate_snapshot=candidate_snapshot,
                actor_id=actor_id,
                later_review_work_item_id=later_review_work_item_id,
                created_at=datetime.now(UTC),
                case_created=False,
            )
            self._decisions.append(rec)
            return rec

    def get_duplicate_history(
        self, *, customer_id: str, limit: int = 50
    ) -> list[DuplicateDecisionRecord]:
        with self._lock:
            rows = [d for d in self._decisions if d.customer_id == customer_id]
            rows.sort(key=lambda d: d.created_at, reverse=True)
            return rows[:limit]

    def create_later_review_work_item(
        self, *, customer_id: str, reason: str, complaint_id: str | None = None
    ) -> str:
        with self._lock:
            work_item_id = f"LR-{uuid.uuid4().hex[:12].upper()}"
            self._later_reviews.append(
                LaterReviewWorkItem(
                    work_item_id=work_item_id,
                    customer_id=customer_id,
                    reason=reason,
                    status="OPEN",
                    created_at=datetime.now(UTC),
                    complaint_id=(complaint_id.strip() if complaint_id else None)
                    or None,
                )
            )
            return work_item_id

    def list_later_review_items(
        self, *, status: str | None = "OPEN", limit: int = 100
    ) -> list[LaterReviewWorkItem]:
        with self._lock:
            rows = list(self._later_reviews)
            if status and status != "ALL":
                rows = [r for r in rows if r.status == status]
            rows.sort(key=lambda r: r.created_at)
            return rows[:limit]

    def close_later_review_items(
        self,
        *,
        complaint_id: str,
        reason: str = "attachment_bind_failed",
    ) -> int:
        cid = (complaint_id or "").strip()
        if not cid:
            return 0
        with self._lock:
            closed = 0
            for item in self._later_reviews:
                if (
                    item.status == "OPEN"
                    and item.reason == reason
                    and item.complaint_id == cid
                ):
                    item.status = "CLOSED"
                    closed += 1
            return closed

    def list_aging_without_case(
        self, *, older_than: datetime, limit: int = 100
    ) -> list[ComplaintAggregate]:
        with self._lock:
            rows = [
                c
                for c in self._complaints.values()
                if not c.case_created
                and c.status != "CLOSED"
                and c.created_at <= older_than
            ]
            rows.sort(key=lambda c: c.created_at)
            return rows[:limit]

    def update_intake_disposition(
        self,
        complaint_id: str,
        *,
        intake_disposition: str,
        description: str | None = None,
        priority: str | None = None,
        decided_by: str | None = None,
        clear_proposed: bool = False,
    ) -> ComplaintAggregate | None:
        with self._lock:
            row = self._complaints.get(str(complaint_id).strip())
            if row is None:
                return None
            disposition = (intake_disposition or "").strip().upper() or None
            row.intake_disposition = disposition
            if description is not None:
                row.description = description
            if priority is not None:
                row.priority = priority.strip().upper()
            if decided_by is not None:
                row.decided_by = decided_by
                row.decided_at = datetime.now(UTC)
            if clear_proposed:
                self._clear_proposed(row)
            return row

    def accept_at_hq(
        self,
        complaint_id: str,
        *,
        hq_accepted_at: datetime,
        description: str | None = None,
        intake_disposition: str | None = None,
    ) -> ComplaintAggregate | None:
        with self._lock:
            row = self._complaints.get(str(complaint_id).strip())
            if row is None:
                return None
            row.hq_accepted_at = hq_accepted_at
            if description is not None:
                row.description = description
            if intake_disposition is not None:
                row.intake_disposition = intake_disposition
            self._clear_proposed(row)
            return row

    def schedule_hq_arrival(
        self,
        complaint_id: str,
        *,
        arrival_date,
        arrival_time: str,
        description: str | None = None,
        intake_disposition: str | None = None,
        destination_unit_id: str | None = None,
        destination_set_by: str | None = None,
    ) -> ComplaintAggregate | None:
        with self._lock:
            row = self._complaints.get(str(complaint_id).strip())
            if row is None:
                return None
            row.hq_arrival_date = arrival_date
            row.hq_arrival_time = arrival_time
            if destination_unit_id is not None:
                row.hq_destination_unit_id = destination_unit_id
                row.hq_destination_set_by = destination_set_by
                row.hq_destination_set_at = datetime.now(UTC)
            if description is not None:
                row.description = description
            if intake_disposition is not None:
                row.intake_disposition = intake_disposition
            self._clear_proposed(row)
            return row

    def accept_and_schedule_at_hq(
        self,
        complaint_id: str,
        *,
        hq_accepted_at: datetime,
        arrival_date,
        arrival_time: str,
        description: str,
        intake_disposition: str = "HQ_SCHEDULED",
        destination_unit_id: str | None = None,
        destination_set_by: str | None = None,
    ) -> ComplaintAggregate | None:
        with self._lock:
            row = self._complaints.get(str(complaint_id).strip())
            if row is None:
                return None
            row.hq_accepted_at = hq_accepted_at
            row.hq_arrival_date = arrival_date
            row.hq_arrival_time = arrival_time
            if destination_unit_id is not None:
                row.hq_destination_unit_id = destination_unit_id
                row.hq_destination_set_by = destination_set_by
                row.hq_destination_set_at = datetime.now(UTC)
            row.description = description
            row.intake_disposition = intake_disposition
            self._clear_proposed(row)
            return row

    def complete_at_hq(
        self,
        complaint_id: str,
        *,
        description: str,
        intake_disposition: str = "HQ_CLOSED",
        closed_by: str | None = None,
    ) -> ComplaintAggregate | None:
        with self._lock:
            row = self._complaints.get(str(complaint_id).strip())
            if row is None:
                return None
            row.description = description
            row.intake_disposition = intake_disposition
            apply_complaint_status(row, "CLOSED")
            _ = closed_by
            return row

    @staticmethod
    def _clear_proposed(row: ComplaintAggregate) -> None:
        row.proposed_arrival_date = None
        row.proposed_arrival_time = None
        row.proposed_by = None
        row.proposed_at = None

    def propose_arrival(
        self,
        complaint_id: str,
        *,
        proposed_date: date,
        proposed_time: str,
        proposed_by: str | None,
    ) -> ComplaintAggregate | None:
        with self._lock:
            row = self._complaints.get(str(complaint_id).strip())
            if row is None:
                return None
            row.proposed_arrival_date = proposed_date
            row.proposed_arrival_time = proposed_time
            row.proposed_by = proposed_by
            row.proposed_at = datetime.now(UTC)
            return row

    def clear_proposed_arrival(self, complaint_id: str) -> ComplaintAggregate | None:
        with self._lock:
            row = self._complaints.get(str(complaint_id).strip())
            if row is None:
                return None
            self._clear_proposed(row)
            return row

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
        needs_pusat_handling: bool = False,
    ) -> tuple[list[ComplaintAggregate], int]:
        page = max(1, int(page))
        page_size = max(1, min(int(page_size), 100))
        with self._lock:
            rows = list(self._complaints.values())
            vis = (visibility or "ALL").strip().upper()
            codes = pusat_unit_codes or DEFAULT_PUSAT_UNIT_CODES
            if vis == "ALL":
                pass
            elif vis == "SELF":
                actor = (actor_id or "").strip()
                if not actor:
                    return [], 0
                rows = [c for c in rows if (c.created_by or "") == actor]
            elif vis == "UNIT":
                unit = (org_unit_id or "").strip()
                if not unit:
                    return [], 0
                rows = [c for c in rows if (c.owning_unit_id or "") == unit]
            elif vis == "PUSAT":
                rows = [
                    c
                    for c in rows
                    if complaint_visible_for_pusat(
                        owning_unit_id=c.owning_unit_id,
                        intake_disposition=c.intake_disposition,
                        hq_accepted_at=c.hq_accepted_at,
                        pusat_unit_codes=codes,
                    )
                ]
            else:
                return [], 0
            kw = (keyword or "").strip().lower()
            if kw:
                rows = [
                    c
                    for c in rows
                    if kw in c.complaint_number.lower()
                    or kw in (c.subject or "").lower()
                    or kw in (c.customer_id or "").lower()
                ]
            st = (status or "").strip().upper()
            if st == "OPEN":
                rows = [c for c in rows if is_open(c.status)]
            elif st in AGGREGATE_STATUSES:
                rows = [c for c in rows if (c.status or "").upper() == st]
            disp = (intake_disposition or "").strip().upper()
            if disp in LIST_INTAKE_DISPOSITION_FILTERS:
                rows = [
                    c
                    for c in rows
                    if matches_intake_disposition_filter(
                        c.intake_disposition, disp
                    )
                ]
            pri = (priority or "").strip().upper()
            if pri:
                rows = [c for c in rows if (c.priority or "").upper() == pri]
            cat = (category or "").strip().lower()
            if cat:
                rows = [c for c in rows if (c.category or "").lower() == cat]
            cb = (created_by or "").strip()
            if cb:
                rows = [c for c in rows if (c.created_by or "") == cb]
            db_ = (decided_by or "").strip()
            if db_:
                rows = [c for c in rows if (c.decided_by or "") == db_]
            if needs_pusat_handling:
                from app.modules.cm_case.infrastructure.inbox_repository import (
                    complaint_needs_pusat_handling,
                )

                rows = [
                    c
                    for c in rows
                    if complaint_needs_pusat_handling(
                        status=c.status,
                        intake_disposition=c.intake_disposition,
                        hq_accepted_at=c.hq_accepted_at,
                        cases=[],
                    )
                ]
            rows = sorted(rows, key=lambda c: c.created_at, reverse=True)
            total = len(rows)
            start = (page - 1) * page_size
            return rows[start : start + page_size], total

    def list_cases_for_complaint_ids(
        self,
        complaint_ids: list[str],
        *,
        visibility: str | None = None,
        pusat_unit_codes: frozenset[str] | None = None,
    ) -> dict[str, list[dict[str, object]]]:
        # In-memory lab store has no Case table — list UI falls back to empty.
        _ = (visibility, pusat_unit_codes)
        return {str(i).strip(): [] for i in complaint_ids if str(i).strip()}

    def unread_parent_ids(self, user_id: str, complaint_ids: list[str]) -> set[str]:
        # In-memory store has no read-receipt table.
        _ = (user_id, complaint_ids)
        return set()

    def work_stats_for_user(self, user_key: str) -> dict[str, int]:
        key = (user_key or "").strip()
        with self._lock:
            rows = list(self._complaints.values())
        if not key:
            return {
                "created_count": 0,
                "escalation_requested_count": 0,
                "escalation_approved_count": 0,
                "escalation_rejected_count": 0,
            }
        created = [c for c in rows if (c.created_by or "") == key]
        decided = [c for c in rows if (c.decided_by or "") == key]
        return {
            "created_count": len(created),
            "escalation_requested_count": len(
                [
                    c
                    for c in created
                    if in_escalation_family(c.intake_disposition)
                ]
            ),
            "escalation_approved_count": len(
                [c for c in decided if (c.intake_disposition or "") == "ESCALATE_APPROVED"]
            ),
            "escalation_rejected_count": len(
                [c for c in decided if (c.intake_disposition or "") == "ESCALATE_REJECTED"]
            ),
        }


# Retained for rare process-local fallbacks / migrations; router uses DB repo.
STORE = Batch1Store()
