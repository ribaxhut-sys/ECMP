"""SQLAlchemy adapter for InternalComplaintRepository."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.core.authorization.visibility import is_pusat_unit, pusat_unit_clause
from app.modules.cm_batch1.complaint_number import resolve_unit_code
from app.modules.internal_complaint.domain.aggregate import InternalComplaintAggregate
from app.modules.internal_complaint.domain.value_objects import InternalComplaintNumber
from app.modules.internal_complaint.infrastructure import mappers
from app.modules.internal_complaint.infrastructure.orm import (
    InternalComplaintAcceptanceORM,
    InternalComplaintEventORM,
    InternalComplaintORM,
    InternalComplaintResolutionORM,
    InternalComplaintUnitCounterORM,
)


def _actor_unit_clause(column, unit: str, pusat_unit_codes: frozenset[str]):
    """Cabang: exact unit. Pusat login: any Pusat unit code."""
    if is_pusat_unit(unit, pusat_unit_codes=pusat_unit_codes):
        return pusat_unit_clause(column, pusat_unit_codes=pusat_unit_codes)
    return column == unit


def _latest_resolution_status():
    """Status resolusi terbaru by decision/proposal time, then id."""
    res = InternalComplaintResolutionORM
    event_at = func.coalesce(res.decided_at, res.proposed_at, res.created_at)
    return (
        select(res.status)
        .where(res.complaint_id == InternalComplaintORM.id)
        .order_by(event_at.desc(), res.id.desc())
        .limit(1)
        .scalar_subquery()
    )


def _needs_action_clause(unit: str, pusat_unit_codes: frozenset[str]):
    """Work waiting on this unit — receive, usulan, rebound, withdraw, close."""
    handling = _actor_unit_clause(
        InternalComplaintORM.handling_unit_id, unit, pusat_unit_codes
    )
    owner = _actor_unit_clause(
        InternalComplaintORM.owner_unit_id, unit, pusat_unit_codes
    )
    latest_pending = _latest_resolution_status()
    latest_rebound = _latest_resolution_status()
    incoming = and_(
        InternalComplaintORM.status.in_(("CREATED", "ASSIGNED")),
        handling,
    )
    pending_proposal = and_(
        InternalComplaintORM.status == "IN_PROGRESS",
        owner,
        latest_pending == "PENDING_APPROVAL",
    )
    # Ball back to handling: Cabang tolak usulan, or kembalikan dari gerbang tutup.
    handling_rebound = and_(
        InternalComplaintORM.status == "IN_PROGRESS",
        handling,
        latest_rebound.in_(("REJECTED", "ACCEPTED")),
    )
    pending_withdraw = and_(
        InternalComplaintORM.withdraw_request_status == "PENDING",
        handling,
    )
    close_gate = and_(
        InternalComplaintORM.status == "RESOLVED",
        or_(owner, handling),
    )
    return or_(
        incoming,
        pending_proposal,
        handling_rebound,
        pending_withdraw,
        close_gate,
    )


def _pusat_inbox_clause(pusat_unit_codes: frozenset[str]):
    """Pusat inbox: live tickets at Pusat; WITHDRAWN only after Pusat handled."""
    pusat_owner = pusat_unit_clause(
        InternalComplaintORM.owner_unit_id, pusat_unit_codes=pusat_unit_codes
    )
    pusat_handling = pusat_unit_clause(
        InternalComplaintORM.handling_unit_id, pusat_unit_codes=pusat_unit_codes
    )
    withdrawn = InternalComplaintORM.status == "WITHDRAWN"
    handled = InternalComplaintORM.pusat_handled_at.isnot(None)
    return or_(
        and_(withdrawn, or_(pusat_owner, handled)),
        and_(~withdrawn, or_(pusat_owner, pusat_handling)),
    )


class SqlAlchemyInternalComplaintRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def next_number(self, *, owner_unit_id: str) -> str:
        """``PI-{UNIT}-{YYMM}-{NNN}`` — per-unit-per-month counter.

        Reuses cm_batch1's Branch.code -> 3-letter unit code mapping so
        internal numbers use the same vocabulary as WP numbers.
        """
        now = datetime.now(UTC)
        unit_code = resolve_unit_code(owner_unit_id)
        period = now.year * 100 + now.month
        counter = self._session.get(InternalComplaintUnitCounterORM, (unit_code, period))
        if counter is None:
            counter = InternalComplaintUnitCounterORM(
                unit_code=unit_code, period=period, last_seq=0
            )
            self._session.add(counter)
            self._session.flush()
        counter.last_seq += 1
        self._session.flush()
        return InternalComplaintNumber.format_unit(
            unit_code, year=now.year, month=now.month, sequence=counter.last_seq
        ).value

    def save(self, complaint: InternalComplaintAggregate) -> InternalComplaintAggregate:
        row = self._session.get(InternalComplaintORM, complaint.complaint_id)
        if row is None:
            row = InternalComplaintORM(id=complaint.complaint_id)
            self._session.add(row)
        mappers.apply_complaint_to_orm(complaint, row)
        # Flush parent before child FK rows — PostgreSQL rejects event inserts
        # when the parent is still pending in the same flush unit.
        self._session.flush()

        existing_res = list(
            self._session.scalars(
                select(InternalComplaintResolutionORM).where(
                    InternalComplaintResolutionORM.complaint_id == complaint.complaint_id
                )
            )
        )
        existing_res_ids = {str(r.id) for r in existing_res}
        for record in complaint.resolution_history:
            if record.resolution_id in existing_res_ids:
                continue
            self._session.add(
                mappers.resolution_to_orm(complaint.complaint_id, record)
            )

        existing_acc = list(
            self._session.scalars(
                select(InternalComplaintAcceptanceORM).where(
                    InternalComplaintAcceptanceORM.complaint_id == complaint.complaint_id
                )
            )
        )
        existing_acc_ids = {str(a.id) for a in existing_acc}
        for record in complaint.acceptance_history:
            if record.acceptance_id in existing_acc_ids:
                continue
            self._session.add(
                mappers.acceptance_to_orm(complaint.complaint_id, record)
            )

        existing_ev = list(
            self._session.scalars(
                select(InternalComplaintEventORM).where(
                    InternalComplaintEventORM.complaint_id == complaint.complaint_id
                )
            )
        )
        existing_ev_ids = {str(e.id) for e in existing_ev}
        for record in complaint.history:
            if record.event_id in existing_ev_ids:
                continue
            self._session.add(mappers.event_to_orm(complaint.complaint_id, record))

        self._session.flush()
        return complaint

    def get(self, complaint_id: str) -> InternalComplaintAggregate | None:
        key = (complaint_id or "").strip()
        if not key:
            return None
        row: InternalComplaintORM | None = None
        try:
            row = self._session.get(InternalComplaintORM, UUID(key))
        except ValueError:
            row = None
        if row is None:
            row = self._session.scalar(
                select(InternalComplaintORM).where(
                    InternalComplaintORM.complaint_number == key
                )
            )
        if row is None:
            return None
        resolutions = list(
            self._session.scalars(
                select(InternalComplaintResolutionORM)
                .where(InternalComplaintResolutionORM.complaint_id == row.id)
                .order_by(
                    func.coalesce(
                        InternalComplaintResolutionORM.decided_at,
                        InternalComplaintResolutionORM.proposed_at,
                        InternalComplaintResolutionORM.created_at,
                    ).asc(),
                    InternalComplaintResolutionORM.id.asc(),
                )
            )
        )
        acceptances = list(
            self._session.scalars(
                select(InternalComplaintAcceptanceORM)
                .where(InternalComplaintAcceptanceORM.complaint_id == row.id)
                .order_by(InternalComplaintAcceptanceORM.decided_at.asc())
            )
        )
        events = list(
            self._session.scalars(
                select(InternalComplaintEventORM)
                .where(InternalComplaintEventORM.complaint_id == row.id)
                .order_by(
                    InternalComplaintEventORM.occurred_at.asc(),
                    InternalComplaintEventORM.created_at.asc(),
                )
            )
        )
        return mappers.complaint_from_orm(row, resolutions, acceptances, events)

    def _visible_stmt(
        self,
        *,
        visibility: str,
        actor_id: str,
        org_unit_id: str | None,
        pusat_unit_codes: frozenset[str],
        status: str | None = None,
        category: str | None = None,
        priority: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        query: str | None = None,
        pending_transfer_request: bool | None = None,
        pending_withdraw_request: bool | None = None,
        needs_receive: bool | None = None,
        needs_action: bool | None = None,
    ):
        """Filtered + visibility-scoped SELECT, or ``None`` when nothing is visible.

        One place decides what a caller may see, so the paged list, the report
        PDF and the report breakdown can never disagree about the population.
        """
        stmt = select(InternalComplaintORM)
        if status and status.strip():
            stmt = stmt.where(
                InternalComplaintORM.status == status.strip().upper()
            )
        if category and category.strip():
            stmt = stmt.where(
                InternalComplaintORM.category == category.strip().upper()
            )
        if priority and priority.strip():
            stmt = stmt.where(
                InternalComplaintORM.priority == priority.strip().upper()
            )
        if date_from is not None:
            stmt = stmt.where(InternalComplaintORM.created_at >= date_from)
        if date_to is not None:
            stmt = stmt.where(InternalComplaintORM.created_at <= date_to)
        if query and query.strip():
            # Mirrors the on-screen search (number, subject, description, units).
            # The reporter's display name lives in the directory, not on this
            # row, so a name-only search can match on screen and not here.
            needle = f"%{query.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(InternalComplaintORM.complaint_number).like(needle),
                    func.lower(InternalComplaintORM.subject).like(needle),
                    func.lower(InternalComplaintORM.description).like(needle),
                    func.lower(InternalComplaintORM.owner_unit_id).like(needle),
                    func.lower(InternalComplaintORM.handling_unit_id).like(needle),
                )
            )
        if pending_transfer_request:
            stmt = stmt.where(InternalComplaintORM.transfer_request_status == "PENDING")
        if pending_withdraw_request:
            stmt = stmt.where(InternalComplaintORM.withdraw_request_status == "PENDING")
        if needs_action:
            unit = (org_unit_id or "").strip()
            if not unit:
                return None
            stmt = stmt.where(_needs_action_clause(unit, pusat_unit_codes))
        elif needs_receive:
            # Incoming queue: not yet received at the actor's handling unit.
            # Cabang: handling == unit. Pusat: handling is any Pusat unit.
            # No unit (lab admin without membership) → empty, not a global count.
            unit = (org_unit_id or "").strip()
            if not unit:
                return None
            stmt = stmt.where(
                InternalComplaintORM.status.in_(("CREATED", "ASSIGNED"))
            )
            if is_pusat_unit(unit, pusat_unit_codes=pusat_unit_codes):
                stmt = stmt.where(
                    pusat_unit_clause(
                        InternalComplaintORM.handling_unit_id,
                        pusat_unit_codes=pusat_unit_codes,
                    )
                )
            else:
                stmt = stmt.where(InternalComplaintORM.handling_unit_id == unit)

        vis = (visibility or "").upper()
        if vis == "ALL":
            return stmt
        if vis == "SELF":
            return stmt.where(InternalComplaintORM.created_by == actor_id)
        if vis == "UNIT":
            unit = (org_unit_id or "").strip()
            if not unit:
                return None
            if is_pusat_unit(unit, pusat_unit_codes=pusat_unit_codes):
                return stmt.where(_pusat_inbox_clause(pusat_unit_codes))
            return stmt.where(
                (InternalComplaintORM.handling_unit_id == unit)
                | (InternalComplaintORM.owner_unit_id == unit)
            )
        if vis == "PUSAT":
            return stmt.where(_pusat_inbox_clause(pusat_unit_codes))
        return None

    def list_summaries(
        self,
        *,
        visibility: str,
        actor_id: str,
        org_unit_id: str | None,
        pusat_unit_codes: frozenset[str],
        status: str | None = None,
        category: str | None = None,
        priority: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        query: str | None = None,
        page: int = 1,
        page_size: int = 20,
        max_page_size: int = 100,
        pending_transfer_request: bool | None = None,
        pending_withdraw_request: bool | None = None,
        needs_receive: bool | None = None,
        needs_action: bool | None = None,
    ) -> tuple[list[InternalComplaintORM], int]:
        page = max(1, int(page))
        page_size = max(1, min(int(page_size), max(1, int(max_page_size))))
        stmt = self._visible_stmt(
            visibility=visibility,
            actor_id=actor_id,
            org_unit_id=org_unit_id,
            pusat_unit_codes=pusat_unit_codes,
            status=status,
            category=category,
            priority=priority,
            date_from=date_from,
            date_to=date_to,
            query=query,
            pending_transfer_request=pending_transfer_request,
            pending_withdraw_request=pending_withdraw_request,
            needs_receive=needs_receive,
            needs_action=needs_action,
        )
        if stmt is None:
            return [], 0

        total = int(
            self._session.scalar(select(func.count()).select_from(stmt.subquery()))
            or 0
        )
        rows = list(
            self._session.scalars(
                stmt.order_by(InternalComplaintORM.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        return rows, total

    def latest_resolution_statuses(
        self, complaint_ids: list[UUID]
    ) -> dict[UUID, str]:
        """Newest resolution status per ticket (decision/proposal time, then id)."""
        if not complaint_ids:
            return {}
        event_at = func.coalesce(
            InternalComplaintResolutionORM.decided_at,
            InternalComplaintResolutionORM.proposed_at,
            InternalComplaintResolutionORM.created_at,
        )
        stmt = (
            select(
                InternalComplaintResolutionORM.complaint_id,
                InternalComplaintResolutionORM.status,
            )
            .where(InternalComplaintResolutionORM.complaint_id.in_(complaint_ids))
            .order_by(
                event_at.desc(),
                InternalComplaintResolutionORM.id.desc(),
            )
        )
        out: dict[UUID, str] = {}
        for complaint_id, status in self._session.execute(stmt):
            if complaint_id not in out:
                out[complaint_id] = status
        return out

    def summarize(
        self,
        *,
        visibility: str,
        actor_id: str,
        org_unit_id: str | None,
        pusat_unit_codes: frozenset[str],
        status: str | None = None,
        category: str | None = None,
        priority: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        query: str | None = None,
    ) -> tuple[int, list[tuple[str, int]], list[tuple[str, int]], list[tuple[str, int]]]:
        """Counts for the report breakdown: total, by status, priority, unit.

        Counted in the database over the whole visible population, so the
        numbers hold even when the client only ever loads a page of rows.
        """
        stmt = self._visible_stmt(
            visibility=visibility,
            actor_id=actor_id,
            org_unit_id=org_unit_id,
            pusat_unit_codes=pusat_unit_codes,
            status=status,
            category=category,
            priority=priority,
            date_from=date_from,
            date_to=date_to,
            query=query,
        )
        if stmt is None:
            return 0, [], [], []

        scoped = stmt.subquery()
        total = int(
            self._session.scalar(select(func.count()).select_from(scoped)) or 0
        )

        def _group(column) -> list[tuple[str, int]]:  # noqa: ANN001
            rows = self._session.execute(
                select(column, func.count())
                .select_from(scoped)
                .group_by(column)
                .order_by(func.count().desc(), column.asc())
            ).all()
            return [(str(value or ""), int(count)) for value, count in rows]

        return (
            total,
            _group(scoped.c.status),
            _group(scoped.c.priority),
            _group(scoped.c.handling_unit_id),
        )

    def commit(self) -> None:
        self._session.commit()
