"""CAPABILITY-013 Notification dashboard aggregates (SQL only)."""

from __future__ import annotations

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.core.enums import NotificationQueueStatus
from app.modules.dashboard.domain.dto import (
    DashboardFilters,
    NotificationSummaryMetrics,
)
from app.modules.notification.models import NotificationQueue


class NotificationDashboardProvider:
    """Read-only notification queue counts. Reuses notification_queue table."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def summary(self, filters: DashboardFilters) -> NotificationSummaryMetrics:
        clauses = self._base_filters(filters)
        stmt = (
            select(
                func.coalesce(
                    func.sum(
                        case(
                            (
                                NotificationQueue.status
                                == NotificationQueueStatus.PENDING.value,
                                1,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label("pending"),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                NotificationQueue.status
                                == NotificationQueueStatus.SENT.value,
                                1,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label("sent"),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                NotificationQueue.status
                                == NotificationQueueStatus.FAILED.value,
                                1,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label("failed"),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                NotificationQueue.status
                                == NotificationQueueStatus.CANCELLED.value,
                                1,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label("cancelled"),
            ).select_from(NotificationQueue)
        )
        if clauses:
            stmt = stmt.where(*clauses)
        row = self._session.execute(stmt).one()
        return NotificationSummaryMetrics(
            pending=int(row.pending or 0),
            sent=int(row.sent or 0),
            failed=int(row.failed or 0),
            cancelled=int(row.cancelled or 0),
        )

    def _base_filters(self, filters: DashboardFilters) -> list[object]:
        # Notification rows have no branch_id — branch filter is intentionally ignored.
        clauses: list[object] = []
        if filters.date_from is not None:
            clauses.append(NotificationQueue.created_at >= filters.date_from)
        if filters.date_to is not None:
            clauses.append(NotificationQueue.created_at <= filters.date_to)
        return clauses
