"""SQLAlchemy adapter for CaseRepository port."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.authorization.visibility import pusat_unit_clause
from app.models import Customer
from app.modules.cm_batch1.complaint_number import case_counter_name, resolve_unit_code
from app.modules.cm_batch1.models import CmBatch1ComplaintORM
from app.modules.cm_batch1.sla import apply_complaint_status
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

_CUSTOMER_NAME_KEY_CAP = 500


def _ilike_contains_pattern(keyword: str) -> str:
    escaped = (
        keyword.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    )
    return f"%{escaped}%"


def _customer_keys_for_keyword(session: Session, pattern: str) -> list[str]:
    """Local customer cache only (ADR-002) — not Customer Master SoR."""
    rows = session.execute(
        select(Customer.id, Customer.external_customer_id)
        .where(
            Customer.deleted_at.is_(None),
            or_(
                Customer.full_name.ilike(pattern, escape="\\"),
                Customer.external_customer_id.ilike(pattern, escape="\\"),
            ),
        )
        .limit(_CUSTOMER_NAME_KEY_CAP)
    ).all()
    keys: list[str] = []
    seen: set[str] = set()
    for cid, external_id in rows:
        for raw in (str(cid) if cid is not None else "", (external_id or "").strip()):
            if raw and raw not in seen:
                seen.add(raw)
                keys.append(raw)
    return keys


def _apply_keyword_filter(session: Session, stmt, keyword: str | None):
    """Substring match on Case fields, parent number, and local customer name."""
    kw = (keyword or "").strip()[:200]
    if not kw:
        return stmt
    pattern = _ilike_contains_pattern(kw)
    parent_ids = [
        str(row_id)
        for row_id in session.scalars(
            select(CmBatch1ComplaintORM.id).where(
                CmBatch1ComplaintORM.complaint_number.ilike(pattern, escape="\\")
            )
        ).all()
    ]
    clauses = [
        CmCaseORM.case_number.ilike(pattern, escape="\\"),
        CmCaseORM.subject.ilike(pattern, escape="\\"),
        CmCaseORM.customer_id.ilike(pattern, escape="\\"),
        CmCaseORM.description.ilike(pattern, escape="\\"),
    ]
    if parent_ids:
        clauses.append(CmCaseORM.complaint_id.in_(parent_ids))
    customer_keys = _customer_keys_for_keyword(session, pattern)
    if customer_keys:
        clauses.append(CmCaseORM.customer_id.in_(customer_keys))
    return stmt.where(or_(*clauses))


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
            hq_accepted_at=row.hq_accepted_at,
            intake_disposition=row.intake_disposition,
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

    def next_case_number(
        self, owning_unit_id: str | None, *, at: datetime | None = None
    ) -> str:
        when = at or datetime.now(UTC)
        if when.tzinfo is None:
            when = when.replace(tzinfo=UTC)
        unit = resolve_unit_code(owning_unit_id)
        name = case_counter_name(unit, year=when.year, month=when.month)
        counter = self._session.get(CmCaseNumberCounterORM, name)
        if counter is None:
            counter = CmCaseNumberCounterORM(name=name, last_seq=0)
            self._session.add(counter)
            self._session.flush()
            counter = self._session.get(CmCaseNumberCounterORM, name)
            assert counter is not None
        counter.last_seq += 1
        self._session.flush()
        return CaseNumber.format(
            unit, year=when.year, month=when.month, sequence=counter.last_seq
        ).value

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

    def get(self, case_id: str, *, for_update: bool = False) -> CaseAggregate | None:
        key = (case_id or "").strip()
        if not key:
            return None
        row: CmCaseORM | None = None
        try:
            row = self._session.get(
                CmCaseORM, UUID(key), with_for_update=for_update or None
            )
        except ValueError:
            row = None
        if row is None:
            stmt = select(CmCaseORM).where(CmCaseORM.case_number == key)
            if for_update:
                stmt = stmt.with_for_update()
            row = self._session.scalar(stmt)
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

    def complaint_numbers_by_ids(self, complaint_ids: list[str]) -> dict[str, str]:
        uuids: list[UUID] = []
        seen: set[UUID] = set()
        for raw in complaint_ids:
            try:
                uid = UUID(str(raw).strip())
            except ValueError:
                continue
            if uid in seen:
                continue
            seen.add(uid)
            uuids.append(uid)
        if not uuids:
            return {}
        rows = self._session.execute(
            select(CmBatch1ComplaintORM.id, CmBatch1ComplaintORM.complaint_number).where(
                CmBatch1ComplaintORM.id.in_(uuids)
            )
        ).all()
        return {str(row_id): number for row_id, number in rows}

    def list_summaries(
        self,
        *,
        visibility: str,
        actor_id: str,
        org_unit_id: str | None,
        pusat_unit_codes: frozenset[str],
        complaint_id: str | None = None,
        status: str | None = None,
        keyword: str | None = None,
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
        stmt = _apply_keyword_filter(self._session, stmt, keyword)

        vis = (visibility or "").upper()
        if vis == "ALL":
            pass
        elif vis == "SELF":
            actor = (actor_id or "").strip()
            if not actor:
                return [], 0
            # Mode A interim (BQ-006): no assignee column. Inbox = Case.created_by.
            # Parent-scoped reads (complaintId=…) also include Cases under a
            # Complaint the actor created — another officer may have opened the
            # Case (list/detail penanganan must not show a false "no case").
            parent_key = (complaint_id or "").strip()
            if parent_key:
                parent = self.get_parent_complaint(parent_key)
                parent_owned = (
                    parent is not None
                    and (parent.created_by or "").strip() == actor
                )
                if not parent_owned:
                    stmt = stmt.where(CmCaseORM.created_by == actor)
            else:
                stmt = stmt.where(CmCaseORM.created_by == actor)
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
            # Root code or Pusat sub-unit (PUSAT-CRO, PUSAT-SUBAN-1, …) on
            # either side — Handling Unit may move between Pusat sub-units
            # while the Owner keeps its access.
            stmt = stmt.where(
                pusat_unit_clause(
                    CmCaseORM.owning_unit_id, pusat_unit_codes=pusat_unit_codes
                )
                | pusat_unit_clause(
                    CmCaseORM.owner_unit_id, pusat_unit_codes=pusat_unit_codes
                )
                | (CmCaseORM.escalated_to_pusat.is_(True))
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

    def unclaimed_escalated_case_ids(self, complaint_id: str) -> list[str]:
        """Open Cases under this parent still parked at Pusat, nobody claimed."""
        key = (complaint_id or "").strip()
        if not key:
            return []
        rows = self._session.scalars(
            select(CmCaseORM.id).where(
                CmCaseORM.complaint_id == key,
                CmCaseORM.escalated_to_pusat.is_(True),
                (CmCaseORM.handling_claimed_by.is_(None))
                | (CmCaseORM.handling_claimed_by == ""),
                CmCaseORM.status.not_in(("CLOSED", "CANCELLED", "RESOLVED")),
            )
        )
        return [str(row) for row in rows]

    def has_open_escalated_cases(self, complaint_id: str) -> bool:
        """True if any open Case under this parent is still with Pusat."""
        key = (complaint_id or "").strip()
        if not key:
            return False
        count = self._session.scalar(
            select(func.count())
            .select_from(CmCaseORM)
            .where(
                CmCaseORM.complaint_id == key,
                CmCaseORM.escalated_to_pusat.is_(True),
                CmCaseORM.status.not_in(("CLOSED", "CANCELLED", "RESOLVED")),
            )
        )
        return int(count or 0) > 0

    def mark_parent_returned_to_branch(self, complaint_id: str) -> None:
        """Case-level return (API-521) — parent leaves the HQ path.

        Only when no sibling Case remains at Pusat. Clears accept/slot so
        cabang tahap/CTA follow ``RETURNED_TO_BRANCH`` (not stale HQ_SCHEDULED).
        """
        try:
            uid = UUID(complaint_id)
        except ValueError:
            return
        row = self._session.get(CmBatch1ComplaintORM, uid)
        if row is None:
            return
        if (row.status or "").strip().upper() == "CLOSED":
            return
        row.intake_disposition = "RETURNED_TO_BRANCH"
        row.hq_accepted_at = None
        row.hq_arrival_date = None
        row.hq_arrival_time = None
        row.hq_destination_unit_id = None
        row.hq_destination_set_by = None
        row.hq_destination_set_at = None
        row.proposed_arrival_date = None
        row.proposed_arrival_time = None
        row.proposed_by = None
        row.proposed_at = None
        self._session.flush()

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
        """DEC-025 §3.4 — BR-009 Mode A auto-close (bukan Close Case = Close Complaint).

        Case ``CANCELLED`` diabaikan dalam hitungan "selesai". Induk auto-close
        jika tidak ada Case yang masih dikerjakan dan ada minimal satu Case
        ``CLOSED``. Semua Case ``CANCELLED`` (tanpa ``CLOSED``) juga menutup induk,
        tetapi ditandai ``ALL_CASES_CANCELLED`` — bukan penyelesaian kerja, jadi
        laporan bisa memisahkannya dari ``BRANCH_CLOSED``/``HQ_CLOSED``
        (keputusan Business Owner 2026-08-22, follow-up DEC-025 §3.4).
        """
        try:
            uid = UUID(complaint_id)
        except ValueError:
            return None
        row = self._session.get(CmBatch1ComplaintORM, uid)
        if row is None:
            return None

        statuses = [
            (s or "").strip().upper()
            for s in self._session.scalars(
                select(CmCaseORM.status).where(CmCaseORM.complaint_id == str(uid))
            )
        ]
        if not statuses:
            return row.status

        working = [s for s in statuses if s not in {"CLOSED", "CANCELLED"}]
        has_closed = any(s == "CLOSED" for s in statuses)
        row.case_created = True
        if working:
            if row.status in {"CLOSED", "REGISTERED"}:
                # Reopen: apply_complaint_status clears closed_at so the SLA
                # measures the reopened cycle, not the closure it superseded.
                apply_complaint_status(row, "IN_PROGRESS")
            disp = (row.intake_disposition or "").strip().upper()
            if disp in {"BRANCH_CLOSED", "ALL_CASES_CANCELLED"}:
                row.intake_disposition = None
        elif has_closed:
            apply_complaint_status(row, "CLOSED")
            disp = (row.intake_disposition or "").strip().upper()
            if not disp or disp in {"BRANCH_CLOSED", "ALL_CASES_CANCELLED"}:
                row.intake_disposition = "BRANCH_CLOSED"
        else:
            # Semua Case CANCELLED — induk ditutup sebagai batal, bukan selesai.
            apply_complaint_status(row, "CLOSED")
            row.intake_disposition = "ALL_CASES_CANCELLED"

        self._session.flush()
        return row.status

    def commit(self) -> None:
        self._session.commit()
