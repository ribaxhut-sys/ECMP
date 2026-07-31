"""Persistent repository for CM Batch 1 Aggregate (S2 Task 01).

Concurrency (TASK-PLATFORM-SECMIG-P5-001A): repository owns Atomic Claim via
``INSERT … ON CONFLICT DO NOTHING`` (no full-session race rollback).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session

from app.modules.cm_batch1.entities import (
    ComplaintAggregate,
    DuplicateDecisionRecord,
    LaterReviewWorkItem,
)
from app.modules.cm_batch1.exceptions import ReplayConflict
from app.modules.cm_batch1.models import (
    CmBatch1ChannelMessageORM,
    CmBatch1ComplaintORM,
    CmBatch1CustomerLockORM,
    CmBatch1DuplicateDecisionORM,
    CmBatch1IdempotencyORM,
    CmBatch1LaterReviewItemORM,
    CmBatch1NumberCounterORM,
)

_COUNTER_NAME = "complaint_number"


def _to_entity(row: CmBatch1ComplaintORM) -> ComplaintAggregate:
    return ComplaintAggregate(
        complaint_id=str(row.id),
        complaint_number=row.complaint_number,
        customer_id=row.customer_id,
        category=row.category,
        channel=row.channel,
        subject=row.subject,
        description=row.description,
        priority=row.priority,
        status=row.status,
        created_at=row.created_at,
        created_by=row.created_by,
        case_created=False,
    )


class CmBatch1Repository:
    """SQLAlchemy-backed Aggregate + idempotency store."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def commit(self) -> None:
        self._session.commit()

    def confirm(self, principal_key: str, customer_id: str) -> None:
        row = self._session.scalar(
            select(CmBatch1CustomerLockORM).where(
                CmBatch1CustomerLockORM.principal_key == principal_key
            )
        )
        if row is None:
            self._session.add(
                CmBatch1CustomerLockORM(
                    principal_key=principal_key,
                    customer_id=customer_id,
                    locked_at=datetime.now(UTC),
                )
            )
        else:
            row.customer_id = customer_id
            row.locked_at = datetime.now(UTC)
        self._session.flush()

    def get_confirmed(self, principal_key: str) -> str | None:
        row = self._session.scalar(
            select(CmBatch1CustomerLockORM).where(
                CmBatch1CustomerLockORM.principal_key == principal_key
            )
        )
        return row.customer_id if row is not None else None

    def get_idempotent(self, request_id: str) -> ComplaintAggregate | None:
        rec = self._session.scalar(
            select(CmBatch1IdempotencyORM).where(
                CmBatch1IdempotencyORM.request_id == request_id
            )
        )
        if rec is None:
            return None
        return self.get(str(rec.complaint_id))

    def get_by_channel_message(self, message_id: str) -> ComplaintAggregate | None:
        rec = self._session.scalar(
            select(CmBatch1ChannelMessageORM).where(
                CmBatch1ChannelMessageORM.channel_message_id == message_id
            )
        )
        if rec is None:
            return None
        return self.get(str(rec.complaint_id))

    def resolve_create_keys(
        self,
        request_id: str,
        channel_message_id: str | None,
    ) -> ComplaintAggregate | None:
        """Return existing aggregate for replay, or None when a create is needed.

        Raises :class:`ReplayConflict` when both keys exist but point at
        different ComplaintIds (canonical identity clash).
        """
        by_req = self.get_idempotent(request_id)
        by_ch = (
            self.get_by_channel_message(channel_message_id)
            if channel_message_id
            else None
        )
        return self._reconcile_key_owners(
            request_id=request_id,
            channel_message_id=channel_message_id,
            by_req=by_req,
            by_ch=by_ch,
        )

    @staticmethod
    def _reconcile_key_owners(
        *,
        request_id: str,
        channel_message_id: str | None,
        by_req: ComplaintAggregate | None,
        by_ch: ComplaintAggregate | None,
    ) -> ComplaintAggregate | None:
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
        """Bind ``request_id`` → canonical ``complaint_id`` (no-op if already bound).

        Raises :class:`ReplayConflict` when the key is already owned by a
        different ComplaintId.
        """
        existing = self.get_idempotent(request_id)
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
        try:
            cid = uuid.UUID(complaint_id)
        except ValueError as exc:
            raise RuntimeError(
                f"Invalid canonical complaint_id for alias bind: {complaint_id}"
            ) from exc
        self._claim_insert(
            CmBatch1IdempotencyORM.__table__,
            {
                "id": uuid.uuid4(),
                "request_id": request_id,
                "complaint_id": cid,
                "created_at": datetime.now(UTC),
            },
            conflict_column="request_id",
        )
        # Concurrent binder may have won; verify canonical owner.
        bound = self.get_idempotent(request_id)
        if bound is None:
            raise RuntimeError("Failed to bind request_id alias after claim")
        if bound.complaint_id != complaint_id:
            raise ReplayConflict(
                diagnostic_details={
                    "requestId": request_id,
                    "requestComplaintId": bound.complaint_id,
                    "canonicalComplaintId": complaint_id,
                }
            )

    def ensure_channel_alias(
        self, channel_message_id: str, complaint_id: str
    ) -> None:
        """Bind ``channel_message_id`` → canonical ``complaint_id`` (no-op if bound).

        Raises :class:`ReplayConflict` when the key is already owned by a
        different ComplaintId.
        """
        existing = self.get_by_channel_message(channel_message_id)
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
        try:
            cid = uuid.UUID(complaint_id)
        except ValueError as exc:
            raise RuntimeError(
                f"Invalid canonical complaint_id for alias bind: {complaint_id}"
            ) from exc
        self._claim_insert(
            CmBatch1ChannelMessageORM.__table__,
            {
                "id": uuid.uuid4(),
                "channel_message_id": channel_message_id,
                "complaint_id": cid,
                "created_at": datetime.now(UTC),
            },
            conflict_column="channel_message_id",
        )
        # Concurrent binder may have won; verify canonical owner.
        bound = self.get_by_channel_message(channel_message_id)
        if bound is None:
            raise RuntimeError(
                "Failed to bind channel_message_id alias after claim"
            )
        if bound.complaint_id != complaint_id:
            raise ReplayConflict(
                diagnostic_details={
                    "channelMessageId": channel_message_id,
                    "channelComplaintId": bound.complaint_id,
                    "canonicalComplaintId": complaint_id,
                }
            )

    def get(self, complaint_id: str) -> ComplaintAggregate | None:
        try:
            cid = uuid.UUID(complaint_id)
        except ValueError:
            return None
        row = self._session.get(CmBatch1ComplaintORM, cid)
        return _to_entity(row) if row is not None else None

    def list_active_for_customer(self, customer_id: str) -> list[ComplaintAggregate]:
        rows = self._session.scalars(
            select(CmBatch1ComplaintORM)
            .where(CmBatch1ComplaintORM.customer_id == customer_id)
            .where(CmBatch1ComplaintORM.status != "CLOSED")
            .order_by(CmBatch1ComplaintORM.created_at.asc())
        ).all()
        return [_to_entity(r) for r in rows]

    def _next_complaint_number(self) -> str:
        row = self._session.scalar(
            select(CmBatch1NumberCounterORM)
            .where(CmBatch1NumberCounterORM.name == _COUNTER_NAME)
            .with_for_update()
        )
        if row is None:
            row = CmBatch1NumberCounterORM(name=_COUNTER_NAME, value=0)
            self._session.add(row)
            self._session.flush()
            row = self._session.scalar(
                select(CmBatch1NumberCounterORM)
                .where(CmBatch1NumberCounterORM.name == _COUNTER_NAME)
                .with_for_update()
            )
            assert row is not None
        row.value += 1
        self._session.flush()
        return f"CM-{row.value:08d}"

    def _dialect_name(self) -> str:
        bind = self._session.get_bind()
        if isinstance(bind, Connection):
            return bind.dialect.name
        return bind.dialect.name  # type: ignore[union-attr]

    def _claim_insert(self, table, values: dict, *, conflict_column: str) -> bool:
        """Insert row; return True if this session won the unique claim."""
        dialect = self._dialect_name()
        if dialect == "sqlite":
            stmt = (
                sqlite_insert(table)
                .values(**values)
                .on_conflict_do_nothing(index_elements=[conflict_column])
                .returning(table.c.id)
            )
        else:
            stmt = (
                pg_insert(table)
                .values(**values)
                .on_conflict_do_nothing(index_elements=[conflict_column])
                .returning(table.c.id)
            )
        return self._session.execute(stmt).first() is not None

    def _delete_idempotency(self, request_id: str) -> None:
        row = self._session.scalar(
            select(CmBatch1IdempotencyORM).where(
                CmBatch1IdempotencyORM.request_id == request_id
            )
        )
        if row is not None:
            self._session.delete(row)

    def _rebind_idempotency(self, request_id: str, complaint_id: str) -> None:
        """Point an existing request_id claim at the canonical ComplaintId."""
        row = self._session.scalar(
            select(CmBatch1IdempotencyORM).where(
                CmBatch1IdempotencyORM.request_id == request_id
            )
        )
        if row is None:
            self.ensure_request_alias(request_id, complaint_id)
            return
        if str(row.complaint_id) == complaint_id:
            return
        row.complaint_id = uuid.UUID(complaint_id)
        self._session.flush()

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
        """Atomic Claim create — ``created=False`` on idempotent / race-loser replay.

        Claim authority: unique indexes via ``ON CONFLICT DO NOTHING``.
        Race losers never call ``session.rollback()``; provisional rows are deleted
        in the same outer transaction (savepoint-free recovery).

        Outcomes: ``(aggregate, True)`` NEW | ``(aggregate, False)`` REPLAY |
        :class:`ReplayConflict` | internal error. Never returns NEW for a deleted
        provisional aggregate.
        """
        existing = self.resolve_create_keys(request_id, channel_message_id)
        if existing is not None:
            self.ensure_request_alias(request_id, existing.complaint_id)
            if channel_message_id:
                self.ensure_channel_alias(
                    channel_message_id, existing.complaint_id
                )
            return existing, False

        complaint_id = uuid.uuid4()
        now = datetime.now(UTC)
        complaint_number = self._next_complaint_number()
        orm = CmBatch1ComplaintORM(
            id=complaint_id,
            complaint_number=complaint_number,
            customer_id=customer_id,
            category=category,
            channel=channel,
            subject=subject,
            description=description,
            priority=priority,
            status="REGISTERED",
            case_created=False,
            created_by=created_by,
            created_at=now,
            updated_at=now,
        )
        self._session.add(orm)
        self._session.flush()

        won_request = self._claim_insert(
            CmBatch1IdempotencyORM.__table__,
            {
                "id": uuid.uuid4(),
                "request_id": request_id,
                "complaint_id": complaint_id,
                "created_at": now,
            },
            conflict_column="request_id",
        )
        if not won_request:
            self._session.delete(orm)
            self._session.flush()
            winner = self.resolve_create_keys(request_id, channel_message_id)
            if winner is not None:
                return winner, False
            raise RuntimeError("Atomic claim lost without a visible winner")

        if channel_message_id:
            won_channel = self._claim_insert(
                CmBatch1ChannelMessageORM.__table__,
                {
                    "id": uuid.uuid4(),
                    "channel_message_id": channel_message_id,
                    "complaint_id": complaint_id,
                    "created_at": now,
                },
                conflict_column="channel_message_id",
            )
            if not won_channel:
                by_ch = self.get_by_channel_message(channel_message_id)
                if by_ch is None:
                    self._delete_idempotency(request_id)
                    self._session.delete(orm)
                    self._session.flush()
                    raise RuntimeError(
                        "Channel claim lost without a visible winner"
                    )
                # Channel owner is canonical — keep request_id alias bound to it.
                self._rebind_idempotency(request_id, by_ch.complaint_id)
                self._session.delete(orm)
                self._session.flush()
                winner = self.resolve_create_keys(
                    request_id, channel_message_id
                )
                if winner is None:
                    raise RuntimeError(
                        "Channel winner lost during request_id rebind"
                    )
                return winner, False

        return _to_entity(orm), True

    def find_duplicate_candidates(
        self,
        *,
        customer_id: str,
        since: datetime,
        limit: int,
    ) -> list[ComplaintAggregate]:
        rows = self._session.scalars(
            select(CmBatch1ComplaintORM)
            .where(CmBatch1ComplaintORM.customer_id == customer_id)
            .where(CmBatch1ComplaintORM.created_at >= since)
            .order_by(CmBatch1ComplaintORM.created_at.desc())
            .limit(limit)
        ).all()
        return [_to_entity(r) for r in rows]

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
        decision_id = uuid.uuid4()
        surviving_uuid = (
            uuid.UUID(surviving_complaint_id) if surviving_complaint_id else None
        )
        source_uuid = uuid.UUID(source_complaint_id) if source_complaint_id else None
        created_at = datetime.now(UTC)
        orm = CmBatch1DuplicateDecisionORM(
            id=decision_id,
            customer_id=customer_id,
            decision=decision,
            surviving_complaint_id=surviving_uuid,
            source_complaint_id=source_uuid,
            justification=justification,
            staging_token=staging_token,
            warning=warning,
            hard_block=hard_block,
            policy_version=policy_version,
            candidate_snapshot=candidate_snapshot,
            actor_id=actor_id,
            later_review_work_item_id=later_review_work_item_id,
            case_created=False,
            created_at=created_at,
        )
        self._session.add(orm)
        self._session.flush()
        return DuplicateDecisionRecord(
            decision_id=str(decision_id),
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
            created_at=created_at,
            case_created=False,
        )

    def get_duplicate_history(
        self, *, customer_id: str, limit: int = 50
    ) -> list[DuplicateDecisionRecord]:
        rows = self._session.scalars(
            select(CmBatch1DuplicateDecisionORM)
            .where(CmBatch1DuplicateDecisionORM.customer_id == customer_id)
            .order_by(CmBatch1DuplicateDecisionORM.created_at.desc())
            .limit(limit)
        ).all()
        return [
            DuplicateDecisionRecord(
                decision_id=str(r.id),
                customer_id=r.customer_id,
                decision=r.decision,
                surviving_complaint_id=(
                    str(r.surviving_complaint_id)
                    if r.surviving_complaint_id is not None
                    else None
                ),
                source_complaint_id=(
                    str(r.source_complaint_id)
                    if r.source_complaint_id is not None
                    else None
                ),
                justification=r.justification,
                staging_token=r.staging_token,
                warning=r.warning,
                hard_block=r.hard_block,
                policy_version=r.policy_version,
                candidate_snapshot=r.candidate_snapshot,
                actor_id=r.actor_id,
                later_review_work_item_id=r.later_review_work_item_id,
                created_at=r.created_at,
                case_created=False,
            )
            for r in rows
        ]

    def create_later_review_work_item(
        self,
        *,
        customer_id: str,
        reason: str,
        complaint_id: str | None = None,
    ) -> str:
        work_item_id = f"LR-{uuid.uuid4().hex[:12].upper()}"
        cleaned_complaint = (complaint_id or "").strip() or None
        self._session.add(
            CmBatch1LaterReviewItemORM(
                id=uuid.uuid4(),
                work_item_id=work_item_id,
                customer_id=customer_id,
                complaint_id=cleaned_complaint,
                reason=reason,
                status="OPEN",
                created_at=datetime.now(UTC),
            )
        )
        self._session.flush()
        return work_item_id

    def list_later_review_items(
        self, *, status: str | None = "OPEN", limit: int = 100
    ) -> list[LaterReviewWorkItem]:
        stmt = select(CmBatch1LaterReviewItemORM).order_by(
            CmBatch1LaterReviewItemORM.created_at.asc()
        )
        if status and status != "ALL":
            stmt = stmt.where(CmBatch1LaterReviewItemORM.status == status)
        stmt = stmt.limit(limit)
        rows = self._session.scalars(stmt).all()
        return [
            LaterReviewWorkItem(
                work_item_id=r.work_item_id,
                customer_id=r.customer_id,
                reason=r.reason,
                status=r.status,
                created_at=r.created_at,
                complaint_id=r.complaint_id,
            )
            for r in rows
        ]

    def list_aging_without_case(
        self, *, older_than: datetime, limit: int = 100
    ) -> list[ComplaintAggregate]:
        rows = self._session.scalars(
            select(CmBatch1ComplaintORM)
            .where(CmBatch1ComplaintORM.case_created.is_(False))
            .where(CmBatch1ComplaintORM.created_at <= older_than)
            .order_by(CmBatch1ComplaintORM.created_at.asc())
            .limit(limit)
        ).all()
        return [_to_entity(r) for r in rows]
