"""In-memory Aggregate store for CM Batch 1 unit tests / S1 compatibility.

Production path uses :class:`CmBatch1Repository` (SQLAlchemy).
"""

from __future__ import annotations

import itertools
import uuid
from datetime import UTC, datetime
from threading import Lock

from app.modules.cm_batch1.entities import (
    ComplaintAggregate,
    DuplicateDecisionRecord,
    IdempotencyRecord,
)


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
        self._later_reviews: list[tuple[str, str, str]] = []
        self._seq = itertools.count(1)
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
            self._seq = itertools.count(1)
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
    ) -> tuple[ComplaintAggregate, bool]:
        with self._lock:
            existing = self._idempotency.get(request_id)
            if existing is not None:
                return self._complaints[existing.complaint_id], False
            if channel_message_id:
                existing_ch = self._channel_msg.get(channel_message_id)
                if existing_ch is not None:
                    return self._complaints[existing_ch.complaint_id], False

            n = next(self._seq)
            complaint_id = str(uuid.uuid4())
            complaint_number = f"CM-{n:08d}"
            row = ComplaintAggregate(
                complaint_id=complaint_id,
                complaint_number=complaint_number,
                customer_id=customer_id,
                category=category,
                channel=channel,
                subject=subject,
                description=description,
                priority=priority,
                created_by=created_by,
                case_created=False,
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
        self, *, customer_id: str, reason: str
    ) -> str:
        with self._lock:
            work_item_id = f"LR-{uuid.uuid4().hex[:12].upper()}"
            self._later_reviews.append((work_item_id, customer_id, reason))
            return work_item_id


# Retained for rare process-local fallbacks / migrations; router uses DB repo.
STORE = Batch1Store()
