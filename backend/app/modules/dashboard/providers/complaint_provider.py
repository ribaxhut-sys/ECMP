"""Dashboard complaint aggregates — CM Batch 1 only (DEC-026 / H1)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.modules.cm_batch1.models import CmBatch1ComplaintORM
from app.modules.cm_batch1.predicates import (
    CLOSED_STATUS,
    ESCALATION_ACTIVE,
)
from app.modules.cm_batch1.scope import owning_unit_for_branch
from app.modules.dashboard.domain.dto import (
    ComplaintSummaryMetrics,
    DashboardFilters,
    TrendBucket,
    TrendPeriod,
)


class ComplaintDashboardProvider:
    """Read-only counts from ``cm_batch1_complaints``. No Foundation tables."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def summary(self, filters: DashboardFilters) -> ComplaintSummaryMetrics:
        scoped = self._scope(filters)
        if scoped is None:
            return ComplaintSummaryMetrics(
                total_complaints=0,
                open_complaints=0,
                closed_complaints=0,
                pending_complaints=0,
                overdue_complaints=0,
                escalated_complaints=0,
                today_complaints=0,
                this_month_complaints=0,
            )
        now = datetime.now(UTC)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = today_start.replace(day=1)
        stmt = (
            select(
                func.count().label("total"),
                func.coalesce(
                    func.sum(
                        case(
                            (CmBatch1ComplaintORM.status != CLOSED_STATUS, 1),
                            else_=0,
                        )
                    ),
                    0,
                ).label("open_count"),
                func.coalesce(
                    func.sum(
                        case(
                            (CmBatch1ComplaintORM.status == CLOSED_STATUS, 1),
                            else_=0,
                        )
                    ),
                    0,
                ).label("closed_count"),
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
                ).label("escalated_count"),
                func.coalesce(
                    func.sum(
                        case(
                            (CmBatch1ComplaintORM.created_at >= today_start, 1),
                            else_=0,
                        )
                    ),
                    0,
                ).label("today_count"),
                func.coalesce(
                    func.sum(
                        case(
                            (CmBatch1ComplaintORM.created_at >= month_start, 1),
                            else_=0,
                        )
                    ),
                    0,
                ).label("month_count"),
            )
            .select_from(CmBatch1ComplaintORM)
            .where(*scoped)
        )
        row = self._session.execute(stmt).one()
        return ComplaintSummaryMetrics(
            total_complaints=int(row.total or 0),
            open_complaints=int(row.open_count or 0),
            closed_complaints=int(row.closed_count or 0),
            pending_complaints=0,
            overdue_complaints=0,
            escalated_complaints=int(row.escalated_count or 0),
            today_complaints=int(row.today_count or 0),
            this_month_complaints=int(row.month_count or 0),
        )

    def trends(
        self,
        filters: DashboardFilters,
        *,
        period: TrendPeriod,
    ) -> list[TrendBucket]:
        scoped = self._scope(filters)
        now = datetime.now(UTC)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if period is TrendPeriod.TODAY:
            range_from = today_start
            days = 1
        elif period is TrendPeriod.SEVEN_D:
            range_from = today_start - timedelta(days=6)
            days = 7
        else:
            range_from = today_start - timedelta(days=29)
            days = 30
        by_day: dict = {}
        if scoped is not None:
            day_expr = func.date_trunc("day", CmBatch1ComplaintORM.created_at)
            stmt = (
                select(day_expr.label("day"), func.count().label("count"))
                .where(
                    *scoped,
                    CmBatch1ComplaintORM.created_at >= range_from,
                    CmBatch1ComplaintORM.created_at <= now,
                )
                .group_by(day_expr)
                .order_by(day_expr)
            )
            for r in self._session.execute(stmt).all():
                key = r.day.date() if hasattr(r.day, "date") else r.day
                by_day[key] = int(r.count)
        buckets: list[TrendBucket] = []
        for offset in range(days):
            d = (range_from + timedelta(days=offset)).date()
            buckets.append(TrendBucket(day=d, count=by_day.get(d, 0)))
        return buckets

    def resolution_stats(
        self, filters: DashboardFilters
    ) -> tuple[int, int, float]:
        scoped = self._scope(filters)
        if scoped is None:
            return 0, 0, 0.0
        total = int(
            self._session.scalar(
                select(func.count())
                .select_from(CmBatch1ComplaintORM)
                .where(*scoped)
            )
            or 0
        )
        closed = int(
            self._session.scalar(
                select(func.count())
                .select_from(CmBatch1ComplaintORM)
                .where(*scoped, CmBatch1ComplaintORM.status == CLOSED_STATUS)
            )
            or 0
        )
        avg_seconds = self._session.scalar(
            select(
                func.avg(
                    func.extract(
                        "epoch",
                        CmBatch1ComplaintORM.updated_at
                        - CmBatch1ComplaintORM.created_at,
                    )
                )
            )
            .select_from(CmBatch1ComplaintORM)
            .where(*scoped, CmBatch1ComplaintORM.status == CLOSED_STATUS)
        )
        return total, closed, float(avg_seconds or 0.0)

    def escalation_count(self, filters: DashboardFilters) -> int:
        scoped = self._scope(filters)
        if scoped is None:
            return 0
        return int(
            self._session.scalar(
                select(func.count())
                .select_from(CmBatch1ComplaintORM)
                .where(
                    *scoped,
                    CmBatch1ComplaintORM.intake_disposition.in_(ESCALATION_ACTIVE),
                )
            )
            or 0
        )

    def _scope(self, filters: DashboardFilters) -> list[object] | None:
        """None = known empty scope (unknown branch). Empty list = unrestricted."""
        clauses: list[object] = []
        if filters.branch_id is not None:
            unit = owning_unit_for_branch(self._session, filters.branch_id)
            if not unit:
                return None
            clauses.append(CmBatch1ComplaintORM.owning_unit_id == unit)
        if filters.date_from is not None:
            clauses.append(CmBatch1ComplaintORM.created_at >= filters.date_from)
        if filters.date_to is not None:
            clauses.append(CmBatch1ComplaintORM.created_at <= filters.date_to)
        return clauses
