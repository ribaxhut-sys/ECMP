"""KPI Foundation repository — read-only SQL aggregations (no KPI tables)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.core.enums import ComplaintStatus, SlaStatus
from app.models import Complaint, SlaRecord


class KpiRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _complaint_filters(
        self,
        *,
        branch_id: uuid.UUID | None,
        date_from: datetime | None,
        date_to: datetime | None,
        category: str | None,
        priority: str | None,
    ) -> list[object]:
        filters: list[object] = [Complaint.deleted_at.is_(None)]
        if branch_id is not None:
            filters.append(Complaint.branch_id == branch_id)
        if date_from is not None:
            filters.append(Complaint.reported_at >= date_from)
        if date_to is not None:
            filters.append(Complaint.reported_at <= date_to)
        if category is not None:
            filters.append(Complaint.category == category)
        if priority is not None:
            filters.append(Complaint.priority == priority)
        return filters

    def count_complaints(
        self,
        *,
        branch_id: uuid.UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        category: str | None = None,
        priority: str | None = None,
    ) -> tuple[int, int, int]:
        """Return (total, open, closed). Open = not CLOSED; closed = CLOSED."""
        filters = self._complaint_filters(
            branch_id=branch_id,
            date_from=date_from,
            date_to=date_to,
            category=category,
            priority=priority,
        )
        total_stmt: Select[tuple[int]] = (
            select(func.count()).select_from(Complaint).where(*filters)
        )
        total = int(self._session.scalar(total_stmt) or 0)

        closed_stmt = (
            select(func.count())
            .select_from(Complaint)
            .where(*filters, Complaint.status == ComplaintStatus.CLOSED)
        )
        closed = int(self._session.scalar(closed_stmt) or 0)
        open_count = total - closed
        return total, open_count, closed

    def count_sla_stage(
        self,
        *,
        status_column,
        target_status: SlaStatus,
        branch_id: uuid.UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        category: str | None = None,
        priority: str | None = None,
    ) -> int:
        filters = self._complaint_filters(
            branch_id=branch_id,
            date_from=date_from,
            date_to=date_to,
            category=category,
            priority=priority,
        )
        stmt = (
            select(func.count())
            .select_from(SlaRecord)
            .join(Complaint, Complaint.id == SlaRecord.complaint_id)
            .where(*filters, status_column == target_status)
        )
        return int(self._session.scalar(stmt) or 0)

    def count_sla_pair(
        self,
        *,
        status_column,
        branch_id: uuid.UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        category: str | None = None,
        priority: str | None = None,
    ) -> tuple[int, int]:
        completed = self.count_sla_stage(
            status_column=status_column,
            target_status=SlaStatus.COMPLETED,
            branch_id=branch_id,
            date_from=date_from,
            date_to=date_to,
            category=category,
            priority=priority,
        )
        breached = self.count_sla_stage(
            status_column=status_column,
            target_status=SlaStatus.BREACHED,
            branch_id=branch_id,
            date_from=date_from,
            date_to=date_to,
            category=category,
            priority=priority,
        )
        return completed, breached
