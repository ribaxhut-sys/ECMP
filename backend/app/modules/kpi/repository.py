"""KPI repository — CM Batch 1 counts; SLA stages always zero (CAP-006 deferred)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.modules.cm_batch1.models import CmBatch1ComplaintORM
from app.modules.cm_batch1.predicates import CLOSED_STATUS
from app.modules.cm_batch1.scope import owning_unit_for_branch


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
        if category is not None:
            filters.append(CmBatch1ComplaintORM.category == category)
        if priority is not None:
            filters.append(CmBatch1ComplaintORM.priority == priority)
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
        """Return (total, open, closed). Open = not CLOSED (DEC-025 M-025-1)."""
        filters = self._complaint_filters(
            branch_id=branch_id,
            date_from=date_from,
            date_to=date_to,
            category=category,
            priority=priority,
        )
        if filters is None:
            return 0, 0, 0
        total_stmt: Select[tuple[int]] = select(func.count()).select_from(
            CmBatch1ComplaintORM
        )
        if filters:
            total_stmt = total_stmt.where(*filters)
        total = int(self._session.scalar(total_stmt) or 0)

        closed_stmt = select(func.count()).select_from(CmBatch1ComplaintORM).where(
            CmBatch1ComplaintORM.status == CLOSED_STATUS
        )
        if filters:
            closed_stmt = closed_stmt.where(*filters)
        closed = int(self._session.scalar(closed_stmt) or 0)

        open_stmt = select(func.count()).select_from(CmBatch1ComplaintORM).where(
            CmBatch1ComplaintORM.status != CLOSED_STATUS
        )
        if filters:
            open_stmt = open_stmt.where(*filters)
        open_count = int(self._session.scalar(open_stmt) or 0)
        return total, open_count, closed

    def count_sla_stage(
        self,
        *,
        status_column,
        target_status,
        branch_id: uuid.UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        category: str | None = None,
        priority: str | None = None,
    ) -> int:
        _ = (
            status_column,
            target_status,
            branch_id,
            date_from,
            date_to,
            category,
            priority,
        )
        return 0

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
        _ = (
            status_column,
            branch_id,
            date_from,
            date_to,
            category,
            priority,
        )
        return 0, 0
