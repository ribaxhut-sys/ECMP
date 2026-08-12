"""SQLAlchemy adapter for CaseRepository port."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.cm_batch1.models import CmBatch1ComplaintORM
from app.modules.cm_case.domain.aggregate import CaseAggregate
from app.modules.cm_case.domain.repositories import ParentComplaintRef
from app.modules.cm_case.domain.value_objects import CaseNumber
from app.modules.cm_case.infrastructure import mappers
from app.modules.cm_case.infrastructure.orm import (
    CmCaseAcceptanceORM,
    CmCaseNumberCounterORM,
    CmCaseORM,
    CmCaseResolutionORM,
)


class SqlAlchemyCaseRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_parent_complaint(self, complaint_id: str) -> ParentComplaintRef | None:
        key = (complaint_id or "").strip()
        if not key:
            return None
        row: CmBatch1ComplaintORM | None = None
        try:
            uid = UUID(key)
            row = self._session.get(CmBatch1ComplaintORM, uid)
        except ValueError:
            row = None
        if row is None:
            row = self._session.scalar(
                select(CmBatch1ComplaintORM).where(
                    CmBatch1ComplaintORM.complaint_number == key
                )
            )
        if row is None:
            return None
        cid = str(row.id)
        count = self.count_cases(cid)
        return ParentComplaintRef(
            complaint_id=cid,
            complaint_number=row.complaint_number,
            customer_id=row.customer_id,
            status=row.status,
            case_created=bool(row.case_created),
            case_count=count,
            owning_unit_id=row.owning_unit_id,
            created_by=row.created_by,
        )

    def count_cases(self, complaint_id: str) -> int:
        return int(
            self._session.scalar(
                select(func.count())
                .select_from(CmCaseORM)
                .where(CmCaseORM.complaint_id == complaint_id)
            )
            or 0
        )

    def next_case_number(self, year: int) -> str:
        counter = self._session.get(CmCaseNumberCounterORM, year)
        if counter is None:
            counter = CmCaseNumberCounterORM(year=year, last_seq=0)
            self._session.add(counter)
            self._session.flush()
        counter.last_seq += 1
        self._session.flush()
        return CaseNumber.format(year, counter.last_seq).value

    def save(self, case: CaseAggregate) -> CaseAggregate:
        row = self._session.get(CmCaseORM, case.case_id)
        if row is None:
            row = CmCaseORM(id=case.case_id)
            self._session.add(row)
        mappers.apply_case_to_orm(case, row)
        # Replace resolution history (append-only business; simplest durable rewrite)
        existing = list(
            self._session.scalars(
                select(CmCaseResolutionORM).where(
                    CmCaseResolutionORM.case_id == case.case_id
                )
            )
        )
        existing_ids = {str(r.id) for r in existing}
        for record in case.resolution_history:
            if record.resolution_id in existing_ids:
                continue
            self._session.add(mappers.resolution_to_orm(case.case_id, record))
        # Acceptance history (F4 closure rule) — same append-only pattern.
        existing_acceptances = list(
            self._session.scalars(
                select(CmCaseAcceptanceORM).where(
                    CmCaseAcceptanceORM.case_id == case.case_id
                )
            )
        )
        existing_acceptance_ids = {str(a.id) for a in existing_acceptances}
        for record in case.acceptance_history:
            if record.acceptance_id in existing_acceptance_ids:
                continue
            self._session.add(mappers.acceptance_to_orm(case.case_id, record))
        self._session.flush()
        return case

    def get(self, case_id: str) -> CaseAggregate | None:
        key = (case_id or "").strip()
        if not key:
            return None
        row: CmCaseORM | None = None
        try:
            row = self._session.get(CmCaseORM, UUID(key))
        except ValueError:
            row = None
        if row is None:
            row = self._session.scalar(
                select(CmCaseORM).where(CmCaseORM.case_number == key)
            )
        if row is None:
            return None
        resolutions = list(
            self._session.scalars(
                select(CmCaseResolutionORM)
                .where(CmCaseResolutionORM.case_id == row.id)
                .order_by(CmCaseResolutionORM.created_at.asc())
            )
        )
        acceptances = list(
            self._session.scalars(
                select(CmCaseAcceptanceORM)
                .where(CmCaseAcceptanceORM.case_id == row.id)
                .order_by(CmCaseAcceptanceORM.decided_at.asc())
            )
        )
        return mappers.case_from_orm(row, resolutions, acceptances)

    def list_summaries(
        self,
        *,
        visibility: str,
        actor_id: str,
        org_unit_id: str | None,
        pusat_unit_codes: frozenset[str],
        complaint_id: str | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[CmCaseORM], int]:
        """Newest-first Case rows filtered by DEC-024 visibility class."""
        page = max(1, int(page))
        page_size = max(1, min(int(page_size), 100))
        stmt = select(CmCaseORM)
        if complaint_id and complaint_id.strip():
            stmt = stmt.where(CmCaseORM.complaint_id == complaint_id.strip())
        if status and status.strip():
            stmt = stmt.where(CmCaseORM.status == status.strip().upper())

        vis = (visibility or "").upper()
        if vis == "ALL":
            pass
        elif vis == "SELF":
            # Mode A interim (BQ-006): no assigned_user column → created_by only
            stmt = stmt.where(CmCaseORM.created_by == actor_id)
        elif vis == "UNIT":
            unit = (org_unit_id or "").strip()
            if not unit:
                return [], 0
            # F4 visibility: Owner unit retains access after Handling Unit moves.
            stmt = stmt.where(
                (CmCaseORM.owning_unit_id == unit)
                | (CmCaseORM.owner_unit_id == unit)
            )
        elif vis == "PUSAT":
            codes = {c.upper() for c in pusat_unit_codes}
            # SQLite/Postgres: compare upper(owning_unit_id / owner_unit_id)
            stmt = stmt.where(
                func.upper(CmCaseORM.owning_unit_id).in_(sorted(codes))
                | func.upper(CmCaseORM.owner_unit_id).in_(sorted(codes))
            )
        else:
            return [], 0

        total = int(
            self._session.scalar(select(func.count()).select_from(stmt.subquery()))
            or 0
        )
        rows = list(
            self._session.scalars(
                stmt.order_by(CmCaseORM.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        return rows, total

    def mark_complaint_in_progress(self, complaint_id: str) -> None:
        try:
            uid = UUID(complaint_id)
        except ValueError:
            return
        row = self._session.get(CmBatch1ComplaintORM, uid)
        if row is None:
            return
        row.case_created = True
        if row.status == "REGISTERED":
            row.status = "IN_PROGRESS"
        self._session.flush()

    def sync_complaint_status_from_cases(self, complaint_id: str) -> str | None:
        """Mode A: induk terbuka selama Case aktif; tutup jika semua Case terminal."""
        try:
            uid = UUID(complaint_id)
        except ValueError:
            return None
        row = self._session.get(CmBatch1ComplaintORM, uid)
        if row is None:
            return None

        terminal = ("CLOSED", "CANCELLED")
        statuses = list(
            self._session.scalars(
                select(CmCaseORM.status).where(CmCaseORM.complaint_id == str(uid))
            )
        )
        if not statuses:
            return row.status

        active = [s for s in statuses if (s or "").strip().upper() not in terminal]
        if active:
            row.case_created = True
            if row.status == "CLOSED":
                row.status = "IN_PROGRESS"
            elif row.status == "REGISTERED":
                row.status = "IN_PROGRESS"
            disp = (row.intake_disposition or "").strip().upper()
            if disp == "BRANCH_CLOSED":
                row.intake_disposition = None
        else:
            # All Cases CLOSED/CANCELLED → Aggregate closed (branch done).
            row.case_created = True
            row.status = "CLOSED"
            disp = (row.intake_disposition or "").strip().upper()
            if not disp or disp == "BRANCH_CLOSED":
                row.intake_disposition = "BRANCH_CLOSED"

        self._session.flush()
        return row.status

    def commit(self) -> None:
        self._session.commit()
