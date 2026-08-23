"""FR-030 SLA sweep + Mode A outbox drain (ADR-CAP006-002 / OPS-CM-B1-SLA-001).

Scheduled commands only — no CAP-005 transport, no new worker process.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.cm_batch1 import event_factory as events
from app.modules.cm_batch1.models import CmBatch1ComplaintORM
from app.modules.cm_batch1.outbox_repository import OutboxRepository
from app.modules.cm_batch1.predicates import CLOSED_STATUS
from app.modules.cm_batch1.side_effects import (
    CmBatch1SideEffectRecorder,
    SideEffectRecorder,
)
from app.modules.cm_batch1.sla import resolve_complaint_sla
from app.modules.cm_batch1.sla_thresholds import (
    SlaThresholdCode,
    candidate_created_at_cutoff,
    crossed_thresholds,
    sla_idempotency_key,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SlaSweepResult:
    scanned: int
    emitted: int
    skipped_idempotent: int


@dataclass(frozen=True)
class OutboxDrainResult:
    published: int


class CmBatch1SlaSweepService:
    """Detect H7/H3/H1/BREACH once per complaint and record durable side effects."""

    def __init__(
        self,
        session: Session,
        *,
        side_effects: SideEffectRecorder | None = None,
        outbox: OutboxRepository | None = None,
        target_days: int = 30,
        warning_percent: int = 80,
        batch_limit: int = 100,
    ) -> None:
        self._session = session
        self._side_effects = side_effects or CmBatch1SideEffectRecorder(session)
        self._outbox = outbox or OutboxRepository(session)
        self._target_days = target_days
        self._warning_percent = warning_percent
        self._batch_limit = batch_limit

    def list_candidates(
        self, *, now: datetime | None = None
    ) -> list[CmBatch1ComplaintORM]:
        """Open complaints old enough that at least H7 may apply (G3.2)."""
        if self._target_days <= 0:
            return []
        current = now or datetime.now(UTC)
        cutoff = candidate_created_at_cutoff(
            target_days=self._target_days, now=current
        )
        rows = self._session.scalars(
            select(CmBatch1ComplaintORM)
            .where(CmBatch1ComplaintORM.status != CLOSED_STATUS)
            .where(CmBatch1ComplaintORM.created_at <= cutoff)
            .order_by(CmBatch1ComplaintORM.created_at.asc())
            .limit(self._batch_limit)
        ).all()
        return list(rows)

    def sweep(
        self,
        *,
        now: datetime | None = None,
        actor_id: str = "ops-sla-sweep",
    ) -> SlaSweepResult:
        current = now or datetime.now(UTC)
        if self._target_days <= 0:
            logger.info(
                "sla sweep skipped target_days=%s reason=measurement_off",
                self._target_days,
            )
            return SlaSweepResult(scanned=0, emitted=0, skipped_idempotent=0)

        candidates = self.list_candidates(now=current)
        emitted = 0
        skipped = 0
        for row in candidates:
            sla = resolve_complaint_sla(
                created_at=row.created_at,
                closed_at=row.closed_at,
                status=row.status,
                target_days=self._target_days,
                warning_percent=self._warning_percent,
                now=current,
            )
            if sla is None or not sla.is_open:
                continue
            for code in crossed_thresholds(due_at=sla.due_at, now=current):
                key = sla_idempotency_key(
                    complaint_id=str(row.id), threshold=code
                )
                if self._outbox.exists_idempotency_key(key):
                    skipped += 1
                    continue
                event = events.complaint_sla_threshold(
                    complaint_id=str(row.id),
                    complaint_number=row.complaint_number,
                    threshold=code,
                    due_at=sla.due_at,
                    occurred_at=current,
                    actor_id=actor_id,
                    elapsed_days=sla.elapsed_days,
                    remaining_days=sla.remaining_days,
                    overdue_days=sla.overdue_days,
                )
                if self._side_effects.record(event):
                    emitted += 1
                else:
                    skipped += 1

        if emitted:
            self._session.commit()
        else:
            self._session.rollback()

        logger.info(
            "sla sweep complete scanned=%s emitted=%s skippedIdempotent=%s "
            "targetDays=%s batchLimit=%s",
            len(candidates),
            emitted,
            skipped,
            self._target_days,
            self._batch_limit,
        )
        return SlaSweepResult(
            scanned=len(candidates),
            emitted=emitted,
            skipped_idempotent=skipped,
        )


class CmBatch1OutboxDrainService:
    """Mark catalog ``EVT-%`` outbox rows PUBLISHED (Mode A local acknowledgment)."""

    def __init__(
        self,
        session: Session,
        *,
        outbox: OutboxRepository | None = None,
        batch_limit: int = 100,
    ) -> None:
        self._session = session
        self._outbox = outbox or OutboxRepository(session)
        self._batch_limit = batch_limit

    def drain(self) -> OutboxDrainResult:
        rows = self._outbox.list_unpublished(limit=self._batch_limit)
        published = 0
        for row in rows:
            if self._outbox.mark_published(row.id):
                published += 1
                logger.info(
                    "outbox drained id=%s eventId=%s eventName=%s aggregateId=%s",
                    row.id,
                    row.event_id,
                    row.event_name,
                    row.aggregate_id,
                )
        if published:
            self._session.commit()
        else:
            self._session.rollback()
        logger.info(
            "outbox drain complete published=%s batchLimit=%s",
            published,
            self._batch_limit,
        )
        return OutboxDrainResult(published=published)


__all__ = [
    "SlaSweepResult",
    "OutboxDrainResult",
    "CmBatch1SlaSweepService",
    "CmBatch1OutboxDrainService",
    "SlaThresholdCode",
]
