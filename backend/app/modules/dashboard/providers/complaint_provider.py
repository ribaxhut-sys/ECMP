"""CAPABILITY-013 Complaint dashboard aggregates (SQL only, no domain writes)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import case, exists, func, select
from sqlalchemy.orm import Session

from app.core.enums import ComplaintStatus, SlaStatus
from app.models import Complaint, SlaRecord
from app.modules.dashboard.domain.dto import (
    ComplaintSummaryMetrics,
    DashboardFilters,
    TrendBucket,
    TrendPeriod,
)


class ComplaintDashboardProvider:
    """Read-only complaint counts / trends. Reuses Complaint + SlaRecord tables."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def summary(self, filters: DashboardFilters) -> ComplaintSummaryMetrics:
        now = datetime.now(UTC)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = today_start.replace(day=1)
        base = self._base_filters(filters)

        overdue_exists = exists(
            select(1).where(
                SlaRecord.complaint_id == Complaint.id,
                SlaRecord.overall_status == SlaStatus.BREACHED.value,
            )
        )

        stmt = (
            select(
                func.count().label("total"),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                Complaint.status.notin_(
                                    (
                                        ComplaintStatus.CLOSED.value,
                                        ComplaintStatus.RESOLVED.value,
                                    )
                                ),
                                1,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label("open_count"),
                func.coalesce(
                    func.sum(
                        case(
                            (Complaint.status == ComplaintStatus.CLOSED.value, 1),
                            else_=0,
                        )
                    ),
                    0,
                ).label("closed_count"),
                func.coalesce(
                    func.sum(
                        case(
                            (Complaint.status == ComplaintStatus.PENDING.value, 1),
                            else_=0,
                        )
                    ),
                    0,
                ).label("pending_count"),
                func.coalesce(
                    func.sum(case((overdue_exists, 1), else_=0)),
                    0,
                ).label("overdue_count"),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                Complaint.status == ComplaintStatus.ESCALATED.value,
                                1,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label("escalated_count"),
                func.coalesce(
                    func.sum(
                        case((Complaint.reported_at >= today_start, 1), else_=0)
                    ),
                    0,
                ).label("today_count"),
                func.coalesce(
                    func.sum(
                        case((Complaint.reported_at >= month_start, 1), else_=0)
                    ),
                    0,
                ).label("month_count"),
            )
            .select_from(Complaint)
            .where(*base)
        )

        row = self._session.execute(stmt).one()
        return ComplaintSummaryMetrics(
            total_complaints=int(row.total or 0),
            open_complaints=int(row.open_count or 0),
            closed_complaints=int(row.closed_count or 0),
            pending_complaints=int(row.pending_count or 0),
            overdue_complaints=int(row.overdue_count or 0),
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

        day_expr = func.date_trunc("day", Complaint.reported_at)
        stmt = (
            select(day_expr.label("day"), func.count().label("count"))
            .where(
                *self._base_filters(filters),
                Complaint.reported_at >= range_from,
                Complaint.reported_at <= now,
            )
            .group_by(day_expr)
            .order_by(day_expr)
        )
        rows = self._session.execute(stmt).all()
        by_day: dict = {}
        for r in rows:
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
        """Return (total, closed, avg_resolution_seconds)."""
        base = self._base_filters(filters)
        total = int(
            self._session.scalar(
                select(func.count()).select_from(Complaint).where(*base)
            )
            or 0
        )
        closed = int(
            self._session.scalar(
                select(func.count())
                .select_from(Complaint)
                .where(*base, Complaint.status == ComplaintStatus.CLOSED.value)
            )
            or 0
        )
        avg_seconds = self._session.scalar(
            select(
                func.avg(
                    func.extract(
                        "epoch",
                        Complaint.closed_at - Complaint.reported_at,
                    )
                )
            )
            .select_from(Complaint)
            .where(
                *base,
                Complaint.status == ComplaintStatus.CLOSED.value,
                Complaint.closed_at.is_not(None),
            )
        )
        return total, closed, float(avg_seconds or 0.0)

    def escalation_count(self, filters: DashboardFilters) -> int:
        return int(
            self._session.scalar(
                select(func.count())
                .select_from(Complaint)
                .where(
                    *self._base_filters(filters),
                    Complaint.status == ComplaintStatus.ESCALATED.value,
                )
            )
            or 0
        )

    def _base_filters(self, filters: DashboardFilters) -> list[object]:
        clauses: list[object] = [Complaint.deleted_at.is_(None)]
        if filters.branch_id is not None:
            clauses.append(Complaint.branch_id == filters.branch_id)
        if filters.date_from is not None:
            clauses.append(Complaint.reported_at >= filters.date_from)
        if filters.date_to is not None:
            clauses.append(Complaint.reported_at <= filters.date_to)
        return clauses
