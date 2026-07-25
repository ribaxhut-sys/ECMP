"""CAPABILITY-013 Queue dashboard aggregates (SQL only)."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.modules.dashboard.domain.dto import DashboardFilters, QueueSummaryMetrics
from app.modules.queue.models import QueueTicketStatus
from app.modules.queue.orm.models import QueueORM, QueueTicketORM


class QueueDashboardProvider:
    """Read-only queue ticket counts. Reuses queue_tickets / queues tables."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def summary(self, filters: DashboardFilters) -> QueueSummaryMetrics:
        now = datetime.now(UTC)
        clauses = self._ticket_filters(filters)

        stmt = select(
            func.coalesce(
                func.sum(
                    case(
                        (
                            QueueTicketORM.status
                            == QueueTicketStatus.WAITING.value,
                            1,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label("waiting"),
            func.coalesce(
                func.sum(
                    case(
                        (
                            QueueTicketORM.status
                            == QueueTicketStatus.SERVING.value,
                            1,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label("serving"),
            func.coalesce(
                func.sum(
                    case(
                        (
                            QueueTicketORM.status
                            == QueueTicketStatus.COMPLETED.value,
                            1,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label("completed"),
            func.coalesce(
                func.sum(
                    case(
                        (
                            QueueTicketORM.status
                            == QueueTicketStatus.CANCELLED.value,
                            1,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label("cancelled"),
        ).select_from(QueueTicketORM)

        if filters.branch_id is not None:
            stmt = stmt.join(
                QueueORM, QueueORM.queue_id == QueueTicketORM.queue_id
            )
            clauses = [
                *clauses,
                QueueORM.organization_id == filters.branch_id,
            ]
        if clauses:
            stmt = stmt.where(*clauses)

        row = self._session.execute(stmt).one()

        avg_clauses: list[object] = [
            *self._ticket_filters(filters),
            QueueTicketORM.status == QueueTicketStatus.WAITING.value,
        ]
        avg_wait_stmt = select(
            func.avg(func.extract("epoch", now - QueueTicketORM.created_at))
        ).select_from(QueueTicketORM)
        if filters.branch_id is not None:
            avg_wait_stmt = avg_wait_stmt.join(
                QueueORM, QueueORM.queue_id == QueueTicketORM.queue_id
            )
            avg_clauses.append(QueueORM.organization_id == filters.branch_id)
        avg_wait_stmt = avg_wait_stmt.where(*avg_clauses)
        avg_wait = float(self._session.scalar(avg_wait_stmt) or 0.0)

        return QueueSummaryMetrics(
            waiting=int(row.waiting or 0),
            serving=int(row.serving or 0),
            completed=int(row.completed or 0),
            cancelled=int(row.cancelled or 0),
            average_waiting_time=round(avg_wait, 2),
        )

    def average_waiting_time(self, filters: DashboardFilters) -> float:
        return self.summary(filters).average_waiting_time

    def _ticket_filters(self, filters: DashboardFilters) -> list[object]:
        clauses: list[object] = []
        if filters.date_from is not None:
            clauses.append(QueueTicketORM.created_at >= filters.date_from)
        if filters.date_to is not None:
            clauses.append(QueueTicketORM.created_at <= filters.date_to)
        return clauses
