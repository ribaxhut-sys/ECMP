"""Report persistence repository (SQLAlchemy 2.x aggregations)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models import Branch, Complaint


class ReportRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _base_filters(
        self,
        *,
        branch_id: uuid.UUID | None,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> list[object]:
        filters: list[object] = [Complaint.deleted_at.is_(None)]
        if branch_id is not None:
            filters.append(Complaint.branch_id == branch_id)
        if date_from is not None:
            filters.append(Complaint.reported_at >= date_from)
        if date_to is not None:
            filters.append(Complaint.reported_at <= date_to)
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
        stmt: Select[tuple[int]] = (
            select(func.count())
            .select_from(Complaint)
            .where(*filters)
        )
        return int(self._session.scalar(stmt) or 0)

    def count_by_status(
        self,
        *,
        branch_id: uuid.UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[tuple[str, int]]:
        filters = self._base_filters(
            branch_id=branch_id, date_from=date_from, date_to=date_to
        )
        stmt = (
            select(Complaint.status, func.count())
            .where(*filters)
            .group_by(Complaint.status)
            .order_by(Complaint.status.asc())
        )
        rows = self._session.execute(stmt).all()
        return [(str(status), int(count)) for status, count in rows]

    def count_by_branch(
        self,
        *,
        branch_id: uuid.UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[tuple[uuid.UUID | None, str | None, str | None, int]]:
        filters = self._base_filters(
            branch_id=branch_id, date_from=date_from, date_to=date_to
        )
        total_col = func.count().label("total")
        stmt = (
            select(
                Complaint.branch_id,
                Branch.code,
                Branch.name,
                total_col,
            )
            .outerjoin(Branch, Branch.id == Complaint.branch_id)
            .where(*filters)
            .group_by(Complaint.branch_id, Branch.code, Branch.name)
            .order_by(total_col.desc())
        )
        rows = self._session.execute(stmt).all()
        return [
            (branch_uuid, code, name, int(total))
            for branch_uuid, code, name, total in rows
        ]
