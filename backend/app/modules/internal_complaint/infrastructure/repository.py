"""SQLAlchemy adapter for InternalComplaintRepository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.internal_complaint.domain.aggregate import InternalComplaintAggregate
from app.modules.internal_complaint.domain.value_objects import InternalComplaintNumber
from app.modules.internal_complaint.infrastructure import mappers
from app.modules.internal_complaint.infrastructure.orm import (
    InternalComplaintAcceptanceORM,
    InternalComplaintEventORM,
    InternalComplaintNumberCounterORM,
    InternalComplaintORM,
    InternalComplaintResolutionORM,
)


class SqlAlchemyInternalComplaintRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def next_number(self, year: int) -> str:
        counter = self._session.get(InternalComplaintNumberCounterORM, year)
        if counter is None:
            counter = InternalComplaintNumberCounterORM(year=year, last_seq=0)
            self._session.add(counter)
            self._session.flush()
        counter.last_seq += 1
        self._session.flush()
        return InternalComplaintNumber.format(year, counter.last_seq).value

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
                .order_by(InternalComplaintResolutionORM.created_at.asc())
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
                .order_by(InternalComplaintEventORM.occurred_at.asc())
            )
        )
        return mappers.complaint_from_orm(row, resolutions, acceptances, events)

    def list_summaries(
        self,
        *,
        visibility: str,
        actor_id: str,
        org_unit_id: str | None,
        pusat_unit_codes: frozenset[str],
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[InternalComplaintORM], int]:
        page = max(1, int(page))
        page_size = max(1, min(int(page_size), 100))
        stmt = select(InternalComplaintORM)
        if status and status.strip():
            stmt = stmt.where(
                InternalComplaintORM.status == status.strip().upper()
            )

        vis = (visibility or "").upper()
        if vis == "ALL":
            pass
        elif vis == "SELF":
            stmt = stmt.where(InternalComplaintORM.created_by == actor_id)
        elif vis == "UNIT":
            unit = (org_unit_id or "").strip()
            if not unit:
                return [], 0
            stmt = stmt.where(
                (InternalComplaintORM.handling_unit_id == unit)
                | (InternalComplaintORM.owner_unit_id == unit)
            )
        elif vis == "PUSAT":
            codes = {c.upper() for c in pusat_unit_codes}
            stmt = stmt.where(
                func.upper(InternalComplaintORM.handling_unit_id).in_(sorted(codes))
                | func.upper(InternalComplaintORM.owner_unit_id).in_(sorted(codes))
            )
        else:
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

    def commit(self) -> None:
        self._session.commit()
