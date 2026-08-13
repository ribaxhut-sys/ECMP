"""Report aggregations from CM Batch 1 (DEC-026)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Select, case, func, select
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
        if filters is None:
            return []
        total_col = func.count().label("total")
        stmt = (
            select(
                Branch.id,
                Branch.code,
                Branch.name,
                total_col,
            )
            .select_from(CmBatch1ComplaintORM)
            .outerjoin(
                Branch,
                Branch.code == CmBatch1ComplaintORM.owning_unit_id,
            )
        )
        if filters:
            stmt = stmt.where(*filters)
        stmt = stmt.group_by(Branch.id, Branch.code, Branch.name).order_by(
            total_col.desc()
        )
        rows = self._session.execute(stmt).all()
        return [
            (branch_uuid, code, name, int(total))
            for branch_uuid, code, name, total in rows
        ]
