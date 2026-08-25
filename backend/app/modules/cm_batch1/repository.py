"""Persistent repository for CM Batch 1 Aggregate (S2 Task 01).

Concurrency (TASK-PLATFORM-SECMIG-P5-001A): repository owns Atomic Claim via
``INSERT … ON CONFLICT DO NOTHING`` (no full-session race rollback).
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

from sqlalchemy import String, and_, cast, exists, func, literal, or_, select
from sqlalchemy import case as sql_case
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session

from app.core.authorization.visibility import (
    DEFAULT_PUSAT_UNIT_CODES,
    pusat_unit_clause,
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
    CmBatch1PusatQueueSeenORM,
)
from app.modules.cm_batch1.predicates import (
    AGGREGATE_STATUSES,
    CLOSED_STATUS,
    ESCALATION_FAMILY,
    HQ_SCHEDULED,
)
from app.modules.cm_batch1.sla import apply_complaint_status
from app.modules.cm_case.infrastructure.orm import CmCaseORM


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
        closed_at=row.closed_at,
        intake_disposition=row.intake_disposition,
        hq_accepted_at=row.hq_accepted_at,
        hq_arrival_date=row.hq_arrival_date,
        hq_arrival_time=row.hq_arrival_time,
        hq_destination_unit_id=row.hq_destination_unit_id,
        hq_destination_set_by=row.hq_destination_set_by,
        hq_destination_set_at=row.hq_destination_set_at,
        proposed_arrival_date=row.proposed_arrival_date,
        proposed_arrival_time=row.proposed_arrival_time,
        proposed_by=row.proposed_by,
        proposed_at=row.proposed_at,
        owning_unit_id=row.owning_unit_id,
        created_at=row.created_at,
        created_by=row.created_by,
        decided_by=row.decided_by,
        decided_at=row.decided_at,
        case_created=bool(row.case_created),
    )


def _clear_proposed(row: CmBatch1ComplaintORM) -> None:
    row.proposed_arrival_date = None
    row.proposed_arrival_time = None
    row.proposed_by = None
    row.proposed_at = None


_TERMINAL_CASE_STATUSES = ("CLOSED", "CANCELLED", "RESOLVED")


def _parent_id_text():
    """``cm_batch1_complaints.id`` as the text form ``cm_cases.complaint_id`` uses.

    Postgres ``id::text`` keeps the hyphens; SQLite cast strips them — rebuild
    the canonical 8-4-4-4-12 shape so correlated EXISTS matches on both.
    """
    raw_id = cast(CmBatch1ComplaintORM.id, String)
    return sql_case(
        (func.length(raw_id) == 36, raw_id),
        else_=func.concat(
            func.substr(raw_id, 1, 8),
            literal("-"),
            func.substr(raw_id, 9, 4),
            literal("-"),
            func.substr(raw_id, 13, 4),
            literal("-"),
            func.substr(raw_id, 17, 4),
            literal("-"),
            func.substr(raw_id, 21, 12),
        ),
    )


def pusat_row_scope_clause(*, pusat_unit_codes: frozenset[str] | None = None):
    """Rows a Pusat actor may see (DEC-024 visibility ``PUSAT``).

    HQ-owned / approved escalate path, but never a parent whose only Cases are
    branch-closed (non-escalated) — that produced a false "Belum ada case" row
    after the embed filter.
    """
    codes = pusat_unit_codes or DEFAULT_PUSAT_UNIT_CODES
    parent_id_txt = _parent_id_text()
    pusat_clause = or_(
        pusat_unit_clause(
            CmBatch1ComplaintORM.owning_unit_id, pusat_unit_codes=codes
        ),
        CmBatch1ComplaintORM.intake_disposition.in_(
            ["ESCALATE_APPROVED", "HQ_SCHEDULED"]
        ),
        CmBatch1ComplaintORM.hq_accepted_at.is_not(None),
    )
    pusat_case_predicate = or_(
        CmCaseORM.escalated_to_pusat.is_(True),
        pusat_unit_clause(CmCaseORM.owning_unit_id, pusat_unit_codes=codes),
        pusat_unit_clause(CmCaseORM.owner_unit_id, pusat_unit_codes=codes),
    )
    has_any_case = exists(
        select(1)
        .select_from(CmCaseORM)
        .where(CmCaseORM.complaint_id == parent_id_txt)
    )
    has_pusat_case = exists(
        select(1)
        .select_from(CmCaseORM)
        .where(
            CmCaseORM.complaint_id == parent_id_txt,
            pusat_case_predicate,
        )
    )
    # A Case escalated straight to Pusat (DEC-029 / API-520) is HQ work even
    # when the parent never took the intake escalate path — without this the
    # row is invisible to Pusat and nobody can claim it.
    return and_(
        or_(pusat_clause, has_pusat_case),
        or_(~has_any_case, has_pusat_case),
    )


def pusat_handling_clause():
    """Still needs a Pusat handler — the ``needsPusatHandling=1`` queue.

    Pengaduan Pusat = escalated from the branch and never handled (never
    accepted, never claimed). Accepted / HQ_SCHEDULED work is Tindak lanjut.
    A later unclaimed Case on a RETURNED_TO_BRANCH parent still counts.

    Single source of truth: the list filter and the sidebar badge both call
    this, so the badge can never count a row the list will not show.
    """
    parent_id_txt = _parent_id_text()
    unclaimed_escalated = exists(
        select(1)
        .select_from(CmCaseORM)
        .where(
            CmCaseORM.complaint_id == parent_id_txt,
            CmCaseORM.escalated_to_pusat.is_(True),
            or_(
                CmCaseORM.handling_claimed_by.is_(None),
                CmCaseORM.handling_claimed_by == "",
            ),
            ~CmCaseORM.status.in_(_TERMINAL_CASE_STATUSES),
        )
    )
    waiting_accept = and_(
        CmBatch1ComplaintORM.intake_disposition == "ESCALATE_APPROVED",
        CmBatch1ComplaintORM.hq_accepted_at.is_(None),
        CmBatch1ComplaintORM.status != CLOSED_STATUS,
    )
    # Do not use NOT (x OR intake = HQ_SCHEDULED): NULL intake makes that
    # UNKNOWN in SQL and drops DEC-029 rows that never set disposition.
    not_yet_handled = and_(
        CmBatch1ComplaintORM.hq_accepted_at.is_(None),
        or_(
            CmBatch1ComplaintORM.intake_disposition.is_(None),
            CmBatch1ComplaintORM.intake_disposition != HQ_SCHEDULED,
        ),
    )
    return and_(
        CmBatch1ComplaintORM.status != CLOSED_STATUS,
        not_yet_handled,
        or_(unclaimed_escalated, waiting_accept),
    )


def _case_is_claimed():
    return and_(
        CmCaseORM.handling_claimed_by.is_not(None),
        CmCaseORM.handling_claimed_by != "",
    )


def pusat_follow_up_case_clause():
    """Case Pusat already handles — Tindak lanjut, still open.

    Mutually exclusive with ``pusat_handling_clause`` per Case: never accepted
    and never claimed stays on Pengaduan. NULL intake is not treated as
    RETURNED / pending (SQL ``!=`` on NULL would drop the row).
    """
    accepted = CmBatch1ComplaintORM.hq_accepted_at.is_not(None)
    scheduled = CmBatch1ComplaintORM.intake_disposition == HQ_SCHEDULED
    claimed = _case_is_claimed()
    escalated = CmCaseORM.escalated_to_pusat.is_(True)
    return and_(
        CmBatch1ComplaintORM.status != CLOSED_STATUS,
        ~CmCaseORM.status.in_(_TERMINAL_CASE_STATUSES),
        or_(
            CmBatch1ComplaintORM.intake_disposition.is_(None),
            CmBatch1ComplaintORM.intake_disposition != "RETURNED_TO_BRANCH",
        ),
        or_(
            CmBatch1ComplaintORM.intake_disposition.is_(None),
            CmBatch1ComplaintORM.intake_disposition
            != "ESCALATE_PENDING_APPROVAL",
        ),
        or_(accepted, claimed, scheduled),
        or_(escalated, accepted, scheduled),
    )


def pusat_queue_unread_clause(user_id: str):
    """Queue rows this Pusat user has not opened since the last branch move.

    Read means: a receipt exists for this user whose ``seen_at`` is not older
    than the parent and every Case under it. Any later movement (a new Case, a
    fresh escalation, a branch edit) makes ``seen_at`` stale and the row lights
    up again — for that one user only.
    """
    uid = (user_id or "").strip()
    parent_id_txt = _parent_id_text()
    seen = CmBatch1PusatQueueSeenORM
    # Two levels deep, so correlate explicitly — otherwise SQLAlchemy adds a
    # second cm_batch1_complaints to the inner FROM and the comparison turns
    # into a cross join over every complaint.
    last_case_move = (
        select(func.max(CmCaseORM.updated_at))
        .where(CmCaseORM.complaint_id == parent_id_txt)
        .correlate(CmBatch1ComplaintORM)
        .scalar_subquery()
    )
    already_seen = exists(
        select(1)
        .select_from(seen)
        .where(
            seen.complaint_id == CmBatch1ComplaintORM.id,
            seen.user_id == uid,
            seen.seen_at >= CmBatch1ComplaintORM.updated_at,
            # No Case yet → nothing to be newer than.
            seen.seen_at >= func.coalesce(last_case_move, seen.seen_at),
        )
    ).correlate(CmBatch1ComplaintORM)
    return ~already_seen


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

    def complaint_numbers_by_ids(
        self, complaint_ids: set[uuid.UUID]
    ) -> dict[uuid.UUID, str]:
        """One round-trip map id → complaint_number (dashboard recent-activity)."""
        if not complaint_ids:
            return {}
        rows = self._session.execute(
            select(CmBatch1ComplaintORM.id, CmBatch1ComplaintORM.complaint_number).where(
                CmBatch1ComplaintORM.id.in_(complaint_ids)
            )
        ).all()
        return {row.id: row.complaint_number for row in rows}

    def list_active_for_customer(self, customer_id: str) -> list[ComplaintAggregate]:
        rows = self._session.scalars(
            select(CmBatch1ComplaintORM)
            .where(CmBatch1ComplaintORM.customer_id == customer_id)
            .where(CmBatch1ComplaintORM.status != "CLOSED")
            .order_by(CmBatch1ComplaintORM.created_at.asc())
        ).all()
        return [_to_entity(r) for r in rows]

    def count_for_customer(self, customer_id: str) -> int:
        return int(
            self._session.scalar(
                select(func.count())
                .select_from(CmBatch1ComplaintORM)
                .where(CmBatch1ComplaintORM.customer_id == customer_id)
            )
            or 0
        )

    def list_for_customer(
        self, customer_id: str, *, limit: int = 50
    ) -> list[ComplaintAggregate]:
        """Newest-first history (open + closed) for Customer 360 / BR-010."""
        lim = max(1, min(int(limit), 100))
        rows = self._session.scalars(
            select(CmBatch1ComplaintORM)
            .where(CmBatch1ComplaintORM.customer_id == customer_id)
            .order_by(CmBatch1ComplaintORM.created_at.desc())
            .limit(lim)
        ).all()
        return [_to_entity(r) for r in rows]

    def _next_complaint_number(
        self,
        *,
        owning_unit_id: str | None = None,
        at: datetime | None = None,
    ) -> str:
        """Allocate ``CM{UNIT}-YYMM-NNNN``; counter per unit+month."""
        when = at or datetime.now(UTC)
        if when.tzinfo is None:
            when = when.replace(tzinfo=UTC)
        unit = resolve_unit_code(owning_unit_id)
        name = complaint_counter_name(unit, year=when.year, month=when.month)
        row = self._session.scalar(
            select(CmBatch1NumberCounterORM)
            .where(CmBatch1NumberCounterORM.name == name)
            .with_for_update()
        )
        if row is None:
            row = CmBatch1NumberCounterORM(name=name, value=0)
            self._session.add(row)
            self._session.flush()
            row = self._session.scalar(
                select(CmBatch1NumberCounterORM)
                .where(CmBatch1NumberCounterORM.name == name)
                .with_for_update()
            )
            assert row is not None
        row.value += 1
        self._session.flush()
        return format_next_complaint_number(
            owning_unit_id=unit,
            sequence=row.value,
            at=when,
        )

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
        status: str = "REGISTERED",
        intake_disposition: str | None = None,
        owning_unit_id: str | None = None,
        proposed_arrival_date: date | None = None,
        proposed_arrival_time: str | None = None,
        proposed_by: str | None = None,
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
        unit = (owning_unit_id or "").strip() or None
        complaint_number = self._next_complaint_number(
            owning_unit_id=unit, at=now
        )
        initial_status = (status or "REGISTERED").strip().upper() or "REGISTERED"
        if initial_status not in {"REGISTERED", "CLOSED"}:
            initial_status = "REGISTERED"
        disposition = (intake_disposition or "").strip().upper() or None
        orm = CmBatch1ComplaintORM(
            id=complaint_id,
            complaint_number=complaint_number,
            customer_id=customer_id,
            category=category,
            channel=channel,
            subject=subject,
            description=description,
            priority=priority,
            status=initial_status,
            # Branch walk-away close at intake resolves the complaint the same
            # moment it is registered (DEC-031: elapsed 0 days → MET).
            closed_at=now if initial_status == CLOSED_STATUS else None,
            intake_disposition=disposition,
            owning_unit_id=unit,
            case_created=False,
            created_by=created_by,
            created_at=now,
            updated_at=now,
            proposed_arrival_date=proposed_arrival_date,
            proposed_arrival_time=proposed_arrival_time,
            proposed_by=proposed_by if proposed_arrival_date else None,
            proposed_at=now if proposed_arrival_date else None,
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

    def close_later_review_items(
        self,
        *,
        complaint_id: str,
        reason: str = "attachment_bind_failed",
    ) -> int:
        """Close OPEN later-review rows for a complaint (internal compensation)."""
        cid = (complaint_id or "").strip()
        if not cid:
            return 0
        rows = list(
            self._session.scalars(
                select(CmBatch1LaterReviewItemORM)
                .where(CmBatch1LaterReviewItemORM.complaint_id == cid)
                .where(CmBatch1LaterReviewItemORM.status == "OPEN")
                .where(CmBatch1LaterReviewItemORM.reason == reason)
            ).all()
        )
        for row in rows:
            row.status = "CLOSED"
        if rows:
            self._session.flush()
        return len(rows)

    def list_aging_without_case(
        self, *, older_than: datetime, limit: int = 100
    ) -> list[ComplaintAggregate]:
        rows = self._session.scalars(
            select(CmBatch1ComplaintORM)
            .where(CmBatch1ComplaintORM.case_created.is_(False))
            .where(CmBatch1ComplaintORM.status != "CLOSED")
            .where(CmBatch1ComplaintORM.created_at <= older_than)
            .order_by(CmBatch1ComplaintORM.created_at.asc())
            .limit(limit)
        ).all()
        return [_to_entity(r) for r in rows]

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
        """Update intake path label (API-515). Optionally refresh description/priority."""
        try:
            uid = uuid.UUID(str(complaint_id).strip())
        except ValueError:
            return None
        row = self._session.get(CmBatch1ComplaintORM, uid)
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
            _clear_proposed(row)
        row.updated_at = datetime.now(UTC)
        self._session.flush()
        return _to_entity(row)

    def accept_at_hq(
        self,
        complaint_id: str,
        *,
        hq_accepted_at: datetime,
        description: str | None = None,
        intake_disposition: str | None = None,
    ) -> ComplaintAggregate | None:
        try:
            uid = uuid.UUID(str(complaint_id).strip())
        except ValueError:
            return None
        row = self._session.get(CmBatch1ComplaintORM, uid)
        if row is None:
            return None
        row.hq_accepted_at = hq_accepted_at
        if description is not None:
            row.description = description
        if intake_disposition is not None:
            row.intake_disposition = intake_disposition
        _clear_proposed(row)
        row.updated_at = datetime.now(UTC)
        self._session.flush()
        return _to_entity(row)

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
    ) -> ComplaintAggregate | None:
        try:
            uid = uuid.UUID(str(complaint_id).strip())
        except ValueError:
            return None
        row = self._session.get(CmBatch1ComplaintORM, uid)
        if row is None:
            return None
        row.hq_arrival_date = arrival_date
        row.hq_arrival_time = arrival_time
        # None means "keep the current destination" — rescheduling a time must
        # not silently unset where the taxpayer was told to go.
        if destination_unit_id is not None:
            row.hq_destination_unit_id = destination_unit_id
            row.hq_destination_set_by = destination_set_by
            row.hq_destination_set_at = datetime.now(UTC)
        if description is not None:
            row.description = description
        if intake_disposition is not None:
            row.intake_disposition = intake_disposition
        _clear_proposed(row)
        row.updated_at = datetime.now(UTC)
        self._session.flush()
        return _to_entity(row)

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
    ) -> ComplaintAggregate | None:
        try:
            uid = uuid.UUID(str(complaint_id).strip())
        except ValueError:
            return None
        row = self._session.get(CmBatch1ComplaintORM, uid)
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
        _clear_proposed(row)
        row.updated_at = datetime.now(UTC)
        self._session.flush()
        return _to_entity(row)

    def complete_at_hq(
        self,
        complaint_id: str,
        *,
        description: str,
        intake_disposition: str = "HQ_CLOSED",
        closed_by: str | None = None,
    ) -> ComplaintAggregate | None:
        """Close Aggregate after HQ visit; terminalize open Cases; free HQ slot."""
        try:
            uid = uuid.UUID(str(complaint_id).strip())
        except ValueError:
            return None
        row = self._session.get(CmBatch1ComplaintORM, uid)
        if row is None:
            return None
        now = datetime.now(UTC)
        complaint_key = str(uid)
        cases = self._session.scalars(
            select(CmCaseORM).where(CmCaseORM.complaint_id == complaint_key)
        ).all()
        for case in cases:
            status = (case.status or "").strip().upper()
            if status in {"CLOSED", "CANCELLED"}:
                continue
            case.status = "CLOSED"
            case.closed_by = closed_by
            case.closed_at = now
            case.updated_at = now
        row.description = description
        row.intake_disposition = intake_disposition
        apply_complaint_status(row, "CLOSED", now=now)
        row.updated_at = now
        self._session.flush()
        return _to_entity(row)

    def propose_arrival(
        self,
        complaint_id: str,
        *,
        proposed_date: date,
        proposed_time: str,
        proposed_by: str | None,
    ) -> ComplaintAggregate | None:
        try:
            uid = uuid.UUID(str(complaint_id).strip())
        except ValueError:
            return None
        row = self._session.get(CmBatch1ComplaintORM, uid)
        if row is None:
            return None
        row.proposed_arrival_date = proposed_date
        row.proposed_arrival_time = proposed_time
        row.proposed_by = proposed_by
        row.proposed_at = datetime.now(UTC)
        row.updated_at = datetime.now(UTC)
        self._session.flush()
        return _to_entity(row)

    def clear_proposed_arrival(self, complaint_id: str) -> ComplaintAggregate | None:
        try:
            uid = uuid.UUID(str(complaint_id).strip())
        except ValueError:
            return None
        row = self._session.get(CmBatch1ComplaintORM, uid)
        if row is None:
            return None
        _clear_proposed(row)
        row.updated_at = datetime.now(UTC)
        self._session.flush()
        return _to_entity(row)

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
        """Newest-first Aggregate list (API-514) with DEC-024 row visibility."""
        page = max(1, int(page))
        page_size = max(1, min(int(page_size), 100))
        stmt = select(CmBatch1ComplaintORM)
        count_stmt = select(func.count()).select_from(CmBatch1ComplaintORM)

        vis = (visibility or "ALL").strip().upper()
        codes = pusat_unit_codes or DEFAULT_PUSAT_UNIT_CODES
        if vis == "ALL":
            pass
        elif vis == "SELF":
            actor = (actor_id or "").strip()
            if not actor:
                return [], 0
            stmt = stmt.where(CmBatch1ComplaintORM.created_by == actor)
            count_stmt = count_stmt.where(CmBatch1ComplaintORM.created_by == actor)
        elif vis == "UNIT":
            unit = (org_unit_id or "").strip()
            if not unit:
                return [], 0
            stmt = stmt.where(CmBatch1ComplaintORM.owning_unit_id == unit)
            count_stmt = count_stmt.where(CmBatch1ComplaintORM.owning_unit_id == unit)
        elif vis == "PUSAT":
            scope = pusat_row_scope_clause(pusat_unit_codes=codes)
            stmt = stmt.where(scope)
            count_stmt = count_stmt.where(scope)
        else:
            return [], 0

        kw = (keyword or "").strip()
        if kw:
            escaped = (
                kw.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            )
            pattern = f"%{escaped}%"
            keyword_clause = (
                CmBatch1ComplaintORM.complaint_number.ilike(pattern, escape="\\")
                | CmBatch1ComplaintORM.subject.ilike(pattern, escape="\\")
                | CmBatch1ComplaintORM.description.ilike(pattern, escape="\\")
                | CmBatch1ComplaintORM.customer_id.ilike(pattern, escape="\\")
            )
            stmt = stmt.where(keyword_clause)
            count_stmt = count_stmt.where(keyword_clause)

        st = (status or "").strip().upper()
        if st == "OPEN":
            open_clause = CmBatch1ComplaintORM.status != CLOSED_STATUS
            stmt = stmt.where(open_clause)
            count_stmt = count_stmt.where(open_clause)
        elif st in AGGREGATE_STATUSES:
            stmt = stmt.where(CmBatch1ComplaintORM.status == st)
            count_stmt = count_stmt.where(CmBatch1ComplaintORM.status == st)

        disp = (intake_disposition or "").strip().upper()
        _allowed_disp = {"BRANCH_CLOSED", *ESCALATION_FAMILY}
        if disp == "ESCALATED":
            # Pseudo-value: any escalate-family state (Users directory drill-down).
            stmt = stmt.where(
                CmBatch1ComplaintORM.intake_disposition.in_(ESCALATION_FAMILY)
            )
            count_stmt = count_stmt.where(
                CmBatch1ComplaintORM.intake_disposition.in_(ESCALATION_FAMILY)
            )
        elif disp == "UNESCALATED":
            unescalated = or_(
                CmBatch1ComplaintORM.intake_disposition.is_(None),
                ~CmBatch1ComplaintORM.intake_disposition.in_(ESCALATION_FAMILY),
            )
            stmt = stmt.where(unescalated)
            count_stmt = count_stmt.where(unescalated)
        elif disp in _allowed_disp:
            stmt = stmt.where(CmBatch1ComplaintORM.intake_disposition == disp)
            count_stmt = count_stmt.where(
                CmBatch1ComplaintORM.intake_disposition == disp
            )

        pri = (priority or "").strip().upper()
        if pri:
            stmt = stmt.where(CmBatch1ComplaintORM.priority == pri)
            count_stmt = count_stmt.where(CmBatch1ComplaintORM.priority == pri)

        cat = (category or "").strip()
        if cat:
            # Case-insensitive exact match on trimmed category.
            cat_clause = func.lower(CmBatch1ComplaintORM.category) == cat.lower()
            stmt = stmt.where(cat_clause)
            count_stmt = count_stmt.where(cat_clause)

        cb = (created_by or "").strip()
        if cb:
            stmt = stmt.where(CmBatch1ComplaintORM.created_by == cb)
            count_stmt = count_stmt.where(CmBatch1ComplaintORM.created_by == cb)

        db_ = (decided_by or "").strip()
        if db_:
            stmt = stmt.where(CmBatch1ComplaintORM.decided_by == db_)
            count_stmt = count_stmt.where(CmBatch1ComplaintORM.decided_by == db_)

        if needs_pusat_handling:
            handling_clause = pusat_handling_clause()
            stmt = stmt.where(handling_clause)
            count_stmt = count_stmt.where(handling_clause)

        total = int(self._session.scalar(count_stmt) or 0)
        rows = self._session.scalars(
            stmt.order_by(CmBatch1ComplaintORM.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
        return [_to_entity(r) for r in rows], total

    def count_pusat_queue_unread(self, user_id: str) -> int:
        """Sidebar badge for one Pusat user: queue rows they have not opened.

        Same scope + handling predicates as ``list_complaints`` with
        ``needs_pusat_handling=True``, so the badge can never disagree with the
        list behind it.
        """
        uid = (user_id or "").strip()
        if not uid:
            return 0
        stmt = (
            select(func.count())
            .select_from(CmBatch1ComplaintORM)
            .where(
                pusat_row_scope_clause(),
                pusat_handling_clause(),
                pusat_queue_unread_clause(uid),
            )
        )
        return int(self._session.scalar(stmt) or 0)

    def count_pusat_follow_up_unread(self, user_id: str) -> int:
        """Tindak lanjut parents this Pusat user has not opened since last move.

        Same unread receipt as the Pengaduan badge (``cm_pusat_queue_seen``),
        scoped to follow-up Cases so one row cannot light both menus.
        Count is parents (same grain as ``pusatQueue``).
        """
        uid = (user_id or "").strip()
        if not uid:
            return 0
        follow_up_exists = (
            exists(
                select(1)
                .select_from(CmCaseORM)
                .where(
                    CmCaseORM.complaint_id == _parent_id_text(),
                    pusat_follow_up_case_clause(),
                )
            ).correlate(CmBatch1ComplaintORM)
        )
        stmt = (
            select(func.count())
            .select_from(CmBatch1ComplaintORM)
            .where(
                pusat_row_scope_clause(),
                follow_up_exists,
                pusat_queue_unread_clause(uid),
            )
        )
        return int(self._session.scalar(stmt) or 0)

    def mark_pusat_queue_seen(self, complaint_id: str, user_id: str) -> None:
        """Upsert this user's read receipt for one parent (idempotent)."""
        try:
            cid = uuid.UUID(str(complaint_id).strip())
        except ValueError:
            return
        uid = (user_id or "").strip()
        if not uid:
            return
        now = datetime.now(UTC)
        row = self._session.scalar(
            select(CmBatch1PusatQueueSeenORM).where(
                CmBatch1PusatQueueSeenORM.complaint_id == cid,
                CmBatch1PusatQueueSeenORM.user_id == uid,
            )
        )
        if row is None:
            self._session.add(
                CmBatch1PusatQueueSeenORM(
                    complaint_id=cid, user_id=uid, seen_at=now
                )
            )
        else:
            row.seen_at = now
        self._session.flush()

    def unread_parent_ids(self, user_id: str, complaint_ids: list[str]) -> set[str]:
        """Which of these parents are still unread for this Pusat user."""
        uid = (user_id or "").strip()
        ids: list[uuid.UUID] = []
        for raw in complaint_ids:
            try:
                ids.append(uuid.UUID(str(raw).strip()))
            except ValueError:
                continue
        if not uid or not ids:
            return set()
        stmt = select(CmBatch1ComplaintORM.id).where(
            CmBatch1ComplaintORM.id.in_(ids),
            pusat_queue_unread_clause(uid),
        )
        return {str(cid) for cid in self._session.scalars(stmt)}


    def work_stats_for_user(self, user_key: str) -> dict[str, int]:
        """Complaint work counters for one actor (UM-BUG-006 / Users directory)."""
        key = (user_key or "").strip()
        if not key:
            return {
                "created_count": 0,
                "escalation_requested_count": 0,
                "escalation_approved_count": 0,
                "escalation_rejected_count": 0,
            }
        created_count = int(
            self._session.scalar(
                select(func.count())
                .select_from(CmBatch1ComplaintORM)
                .where(CmBatch1ComplaintORM.created_by == key)
            )
            or 0
        )
        escalation_requested_count = int(
            self._session.scalar(
                select(func.count())
                .select_from(CmBatch1ComplaintORM)
                .where(
                    CmBatch1ComplaintORM.created_by == key,
                    # Same predicate as the ESCALATED list drill-down, so the
                    # counter and the list it opens cannot disagree.
                    CmBatch1ComplaintORM.intake_disposition.in_(ESCALATION_FAMILY),
                )
            )
            or 0
        )
        escalation_approved_count = int(
            self._session.scalar(
                select(func.count())
                .select_from(CmBatch1ComplaintORM)
                .where(
                    CmBatch1ComplaintORM.decided_by == key,
                    CmBatch1ComplaintORM.intake_disposition == "ESCALATE_APPROVED",
                )
            )
            or 0
        )
        escalation_rejected_count = int(
            self._session.scalar(
                select(func.count())
                .select_from(CmBatch1ComplaintORM)
                .where(
                    CmBatch1ComplaintORM.decided_by == key,
                    CmBatch1ComplaintORM.intake_disposition == "ESCALATE_REJECTED",
                )
            )
            or 0
        )
        return {
            "created_count": created_count,
            "escalation_requested_count": escalation_requested_count,
            "escalation_approved_count": escalation_approved_count,
            "escalation_rejected_count": escalation_rejected_count,
        }

    def list_cases_for_complaint_ids(
        self,
        complaint_ids: list[str],
        *,
        visibility: str | None = None,
        pusat_unit_codes: frozenset[str] | None = None,
    ) -> dict[str, list[dict[str, object]]]:
        """Parent-scoped Case rows for Aggregate list (API-514 embed).

        For ``PUSAT`` visibility, only Cases that are with Pusat are embedded
        (``escalated_to_pusat`` or Pusat owning/owner unit). Branch-closed
        sibling Cases on a mixed complaint must not appear in the Pusat queue.
        """
        keys = [str(i).strip() for i in complaint_ids if str(i).strip()]
        if not keys:
            return {}
        from app.modules.cm_case.infrastructure.orm import CmCaseORM

        codes = pusat_unit_codes or DEFAULT_PUSAT_UNIT_CODES
        stmt = (
            select(CmCaseORM)
            .where(CmCaseORM.complaint_id.in_(keys))
            .order_by(CmCaseORM.created_at.desc())
        )
        if (visibility or "").strip().upper() == "PUSAT":
            stmt = stmt.where(
                (CmCaseORM.escalated_to_pusat.is_(True))
                | pusat_unit_clause(
                    CmCaseORM.owning_unit_id, pusat_unit_codes=codes
                )
                | pusat_unit_clause(
                    CmCaseORM.owner_unit_id, pusat_unit_codes=codes
                )
            )
        rows = list(self._session.scalars(stmt))
        out: dict[str, list[dict[str, object]]] = {k: [] for k in keys}
        for row in rows:
            cid = str(row.complaint_id)
            if cid not in out:
                out[cid] = []
            out[cid].append(
                {
                    "caseId": str(row.id),
                    "caseNumber": row.case_number,
                    "complaintId": cid,
                    "status": row.status,
                    "subject": row.subject,
                    "priority": row.priority,
                    "escalatedToPusat": bool(row.escalated_to_pusat),
                    "handlingClaimedBy": row.handling_claimed_by,
                }
            )
        return out
