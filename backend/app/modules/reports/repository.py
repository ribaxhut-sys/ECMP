"""Report aggregations from CM Batch 1 (DEC-026)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Select, String, case, cast, exists, func, select
from sqlalchemy.orm import Session

from app.models import Branch
from app.modules.cm_batch1.models import CmBatch1ComplaintORM
from app.modules.cm_batch1.predicates import CLOSED_STATUS, ESCALATION_ACTIVE
from app.modules.cm_batch1.scope import owning_unit_for_branch


class ReportRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _base_filters(
        self,
        *,
        branch_id: uuid.UUID | None,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> list[object] | None:
        filters: list[object] = []
        if branch_id is not None:
            unit = owning_unit_for_branch(self._session, branch_id)
            if not unit:
                return None
            filters.append(CmBatch1ComplaintORM.owning_unit_id == unit)
        if date_from is not None:
            filters.append(CmBatch1ComplaintORM.created_at >= date_from)
        if date_to is not None:
            filters.append(CmBatch1ComplaintORM.created_at <= date_to)
        return filters

    def count_total(
        self,
        *,
        branch_id: uuid.UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> int:
        filters = self._base_filters(
            branch_id=branch_id, date_from=date_from, date_to=date_to
        )
        if filters is None:
            return 0
        stmt: Select[tuple[int]] = select(func.count()).select_from(
            CmBatch1ComplaintORM
        )
        if filters:
            stmt = stmt.where(*filters)
        return int(self._session.scalar(stmt) or 0)

    def count_by_status(
        self,
        *,
        branch_id: uuid.UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[tuple[str, int]]:
        """Map CM statuses onto the existing report enum labels (donut-compatible).

        The wire contract still speaks the Foundation ``ComplaintStatus`` labels;
        migrating it to the CM vocabulary is a separate decision. What changes
        here is the mapping itself: ``status`` is the Aggregate SoT and decides
        first, ``intake_disposition`` only refines a still-REGISTERED row, and
        ESCALATED uses the one canonical active-escalation predicate. CM has no
        ASSIGNED state, so that label is no longer emitted.
        """
        filters = self._base_filters(
            branch_id=branch_id, date_from=date_from, date_to=date_to
        )
        if filters is None:
            return []
        mapped = case(
            (
                CmBatch1ComplaintORM.status == CLOSED_STATUS,
                "CLOSED",
            ),
            (
                CmBatch1ComplaintORM.status == "IN_PROGRESS",
                "IN_PROGRESS",
            ),
            (
                CmBatch1ComplaintORM.intake_disposition.in_(ESCALATION_ACTIVE),
                "ESCALATED",
            ),
            else_="NEW",
        )
        stmt = select(mapped.label("status"), func.count())
        if filters:
            stmt = stmt.where(*filters)
        stmt = stmt.group_by(mapped)
        rows = self._session.execute(stmt).all()
        return [(str(status), int(count)) for status, count in rows]

    def _case_counts_by_unit(
        self,
        *,
        branch_id: uuid.UUID | None,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> dict[str | None, tuple[int, int, int]]:
        """Map owning_unit_id → (total, open, closed) for CM cases."""
        from app.modules.cm_case.infrastructure.orm import CmCaseORM

        filters: list[object] = []
        if branch_id is not None:
            unit = owning_unit_for_branch(self._session, branch_id)
            if not unit:
                return {}
            filters.append(CmCaseORM.owning_unit_id == unit)
        if date_from is not None:
            filters.append(CmCaseORM.created_at >= date_from)
        if date_to is not None:
            filters.append(CmCaseORM.created_at <= date_to)
        closed_col = func.coalesce(
            func.sum(case((CmCaseORM.status == CLOSED_STATUS, 1), else_=0)),
            0,
        ).label("closed")
        total_col = func.count().label("total")
        stmt = select(CmCaseORM.owning_unit_id, total_col, closed_col)
        if filters:
            stmt = stmt.where(*filters)
        stmt = stmt.group_by(CmCaseORM.owning_unit_id)
        out: dict[str | None, tuple[int, int, int]] = {}
        for unit, total, closed in self._session.execute(stmt).all():
            total_n = int(total)
            closed_n = int(closed or 0)
            out[unit] = (total_n, max(0, total_n - closed_n), closed_n)
        return out

    def _implied_case_counts_by_unit(
        self,
        *,
        branch_id: uuid.UUID | None,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> dict[str | None, tuple[int, int, int]]:
        """Complaints with no Case row count as one case (closed iff complaint CLOSED)."""
        from app.modules.cm_case.infrastructure.orm import CmCaseORM

        filters = self._base_filters(
            branch_id=branch_id, date_from=date_from, date_to=date_to
        )
        if filters is None:
            return {}
        has_case = exists(
            select(CmCaseORM.id).where(
                CmCaseORM.complaint_id == cast(CmBatch1ComplaintORM.id, String)
            )
        )
        closed_col = func.coalesce(
            func.sum(
                case((CmBatch1ComplaintORM.status == CLOSED_STATUS, 1), else_=0)
            ),
            0,
        ).label("closed")
        total_col = func.count().label("total")
        stmt = select(
            CmBatch1ComplaintORM.owning_unit_id,
            total_col,
            closed_col,
        ).where(~has_case)
        if filters:
            stmt = stmt.where(*filters)
        stmt = stmt.group_by(CmBatch1ComplaintORM.owning_unit_id)
        out: dict[str | None, tuple[int, int, int]] = {}
        for unit, total, closed in self._session.execute(stmt).all():
            total_n = int(total)
            closed_n = int(closed or 0)
            out[unit] = (total_n, max(0, total_n - closed_n), closed_n)
        return out

    @staticmethod
    def _combine_case_counts(
        actual: tuple[int, int, int],
        implied: tuple[int, int, int],
    ) -> tuple[int, int, int]:
        return (
            actual[0] + implied[0],
            actual[1] + implied[1],
            actual[2] + implied[2],
        )

    def count_by_branch(
        self,
        *,
        branch_id: uuid.UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[
        tuple[uuid.UUID | None, str | None, str | None, int, int, int, int, int, int, int]
    ]:
        """Every active branch, zero-filled when the filter window has no work.

        LEFT JOIN from Branch (not from complaints) so Kesehatan Cabang can
        show the full unit set; idle units stay at 0 instead of disappearing.
        """
        if branch_id is not None:
            unit = owning_unit_for_branch(self._session, branch_id)
            if not unit:
                return []

        date_filters: list[object] = []
        if date_from is not None:
            date_filters.append(CmBatch1ComplaintORM.created_at >= date_from)
        if date_to is not None:
            date_filters.append(CmBatch1ComplaintORM.created_at <= date_to)

        complaint_sub = (
            select(
                CmBatch1ComplaintORM.owning_unit_id.label("unit"),
                func.count().label("total"),
                func.coalesce(
                    func.sum(
                        case(
                            (CmBatch1ComplaintORM.status == CLOSED_STATUS, 1),
                            else_=0,
                        )
                    ),
                    0,
                ).label("closed"),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                CmBatch1ComplaintORM.intake_disposition.in_(
                                    ESCALATION_ACTIVE
                                ),
                                1,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label("escalated"),
            )
            .where(*date_filters)
            .group_by(CmBatch1ComplaintORM.owning_unit_id)
            .subquery()
        )

        branch_filters: list[object] = [
            Branch.deleted_at.is_(None),
            Branch.is_active.is_(True),
        ]
        if branch_id is not None:
            branch_filters.append(Branch.id == branch_id)

        stmt = (
            select(
                Branch.id,
                Branch.code,
                Branch.name,
                func.coalesce(complaint_sub.c.total, 0),
                func.coalesce(complaint_sub.c.closed, 0),
                func.coalesce(complaint_sub.c.escalated, 0),
            )
            .outerjoin(complaint_sub, complaint_sub.c.unit == Branch.code)
            .where(*branch_filters)
            .order_by(Branch.name)
        )
        complaint_rows = list(self._session.execute(stmt).all())
        case_by_unit = self._case_counts_by_unit(
            branch_id=branch_id, date_from=date_from, date_to=date_to
        )
        implied_by_unit = self._implied_case_counts_by_unit(
            branch_id=branch_id, date_from=date_from, date_to=date_to
        )
        result: list[
            tuple[
                uuid.UUID | None, str | None, str | None, int, int, int, int, int, int, int
            ]
        ] = []
        for branch_uuid, code, name, total, closed, escalated in complaint_rows:
            total_n = int(total)
            closed_n = int(closed or 0)
            open_n = max(0, total_n - closed_n)
            escalated_n = int(escalated or 0)
            case_total, case_open, case_closed = self._combine_case_counts(
                case_by_unit.get(code, (0, 0, 0)),
                implied_by_unit.get(code, (0, 0, 0)),
            )
            result.append(
                (
                    branch_uuid,
                    code,
                    name,
                    total_n,
                    open_n,
                    closed_n,
                    escalated_n,
                    case_total,
                    case_open,
                    case_closed,
                )
            )
        result.sort(key=lambda row: (row[3], row[7]), reverse=True)
        return result

    def closed_case_durations_days(
        self,
        *,
        branch_id: uuid.UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[float]:
        """Days between Case creation and closure, for closed cases only.

        The window filters on ``closed_at`` (not ``created_at``): a cycle-time
        report answers "what did we finish this period", so a case opened in
        June and closed in August belongs to August.
        """
        from app.modules.cm_case.infrastructure.orm import CmCaseORM

        filters: list[object] = [
            CmCaseORM.status == CLOSED_STATUS,
            CmCaseORM.closed_at.is_not(None),
        ]
        if branch_id is not None:
            unit = owning_unit_for_branch(self._session, branch_id)
            if not unit:
                return []
            filters.append(CmCaseORM.owning_unit_id == unit)
        if date_from is not None:
            filters.append(CmCaseORM.closed_at >= date_from)
        if date_to is not None:
            filters.append(CmCaseORM.closed_at <= date_to)

        rows = self._session.execute(
            select(CmCaseORM.created_at, CmCaseORM.closed_at).where(*filters)
        ).all()
        durations: list[float] = []
        for created_at, closed_at in rows:
            if created_at is None or closed_at is None:
                continue
            seconds = (closed_at - created_at).total_seconds()
            # Clock skew or a backdated close must not produce a negative age.
            durations.append(max(0.0, seconds) / 86400.0)
        return durations
