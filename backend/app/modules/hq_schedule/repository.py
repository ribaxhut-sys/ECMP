"""HQ arrival schedule persistence — holidays + arrival/proposal read-side."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.core.authorization.visibility import is_hq_schedule_destination_unit
from app.models import Branch
from app.modules.cm_batch1.models import CmBatch1ComplaintORM
from app.modules.cm_case.infrastructure.orm import CmCaseORM
from app.modules.hq_schedule.models import CmHqHolidayORM


@dataclass(frozen=True, slots=True)
class PusatUnit:
    """One Pusat door a taxpayer can be directed to, from the org directory."""

    code: str
    name: str


@dataclass(frozen=True, slots=True)
class CaseRef:
    """A Case tracking this complaint's escalation — id so the board can link to it."""

    case_id: str
    case_number: str


@dataclass(frozen=True, slots=True)
class ArrivalRow:
    complaint_id: str
    complaint_number: str
    owning_unit_id: str | None
    hq_arrival_date: date | None
    hq_arrival_time: str | None
    proposed_arrival_date: date | None
    proposed_arrival_time: str | None
    proposed_by: str | None
    proposed_at: datetime | None
    # Case(s) tracking this complaint's escalation — empty if none created yet.
    cases: tuple[CaseRef, ...] = ()
    # True when the HQ visit was completed (HQ_CLOSED) — still listed that day.
    completed: bool = False
    # Which Pusat unit the taxpayer reports to (CRO / Sekretariat / Suban).
    # None while the branch proposal is still awaiting a Pusat decision, and
    # on rows scheduled before the destination column existed.
    hq_destination_unit_id: str | None = None
    # Master Customer id — resolved to a display name in the service (not SoR).
    customer_id: str | None = None


class HqScheduleRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    # -- Holidays ---------------------------------------------------------

    def list_holidays(self, *, date_from: date, date_to: date) -> list[CmHqHolidayORM]:
        stmt = (
            select(CmHqHolidayORM)
            .where(CmHqHolidayORM.holiday_date >= date_from)
            .where(CmHqHolidayORM.holiday_date <= date_to)
            .order_by(CmHqHolidayORM.holiday_date)
        )
        return list(self._session.scalars(stmt).all())

    def get_holiday(self, holiday_date: date) -> CmHqHolidayORM | None:
        return self._session.get(CmHqHolidayORM, holiday_date)

    def create_holiday(
        self,
        *,
        holiday_date: date,
        label: str,
        created_by: str | None,
        kind: str | None = None,
        source: str | None = None,
        imported_at: datetime | None = None,
    ) -> CmHqHolidayORM:
        row = CmHqHolidayORM(
            holiday_date=holiday_date,
            label=label,
            kind=kind,
            source=source,
            imported_at=imported_at,
            created_by=created_by,
            created_at=datetime.now(UTC),
        )
        self._session.add(row)
        self._session.flush()
        return row

    def delete_holiday(self, holiday_date: date) -> bool:
        row = self.get_holiday(holiday_date)
        if row is None:
            return False
        self._session.delete(row)
        self._session.flush()
        return True

    # -- Arrivals / proposals ----------------------------------------------

    # Proposals only count while the escalation is actually pending/live —
    # a stale proposed_* value from a since-returned/rejected/cancelled row
    # must never surface as a pending proposal in the grid.
    _PROPOSAL_LIVE_DISPOSITIONS = ("ESCALATE_PENDING_APPROVAL", "ESCALATE_APPROVED")

    def list_arrivals_in_range(
        self, *, date_from: date, date_to: date
    ) -> list[ArrivalRow]:
        """Live HQ_SCHEDULED visits plus completed HQ_CLOSED visits that day.

        Completed rows stay visible on the calendar (same arrival slot) and
        count toward the slot's occupied ratio — see
        HqScheduleService._slots_for_day for scheduled_count/bookable.
        """
        stmt = (
            select(CmBatch1ComplaintORM)
            .where(
                or_(
                    and_(
                        CmBatch1ComplaintORM.status != "CLOSED",
                        CmBatch1ComplaintORM.intake_disposition == "HQ_SCHEDULED",
                        CmBatch1ComplaintORM.hq_arrival_date.between(
                            date_from, date_to
                        ),
                    ),
                    and_(
                        CmBatch1ComplaintORM.status == "CLOSED",
                        CmBatch1ComplaintORM.intake_disposition == "HQ_CLOSED",
                        CmBatch1ComplaintORM.hq_arrival_date.between(
                            date_from, date_to
                        ),
                    ),
                    and_(
                        CmBatch1ComplaintORM.status != "CLOSED",
                        CmBatch1ComplaintORM.proposed_arrival_date.between(
                            date_from, date_to
                        ),
                    ),
                )
            )
        )
        rows = self._session.scalars(stmt).all()
        cases_by_complaint = self._cases_by_complaint([str(r.id) for r in rows])
        return [
            ArrivalRow(
                complaint_id=str(r.id),
                complaint_number=r.complaint_number,
                owning_unit_id=r.owning_unit_id,
                hq_arrival_date=r.hq_arrival_date,
                hq_arrival_time=r.hq_arrival_time,
                proposed_arrival_date=(
                    r.proposed_arrival_date
                    if r.intake_disposition in self._PROPOSAL_LIVE_DISPOSITIONS
                    else None
                ),
                proposed_arrival_time=(
                    r.proposed_arrival_time
                    if r.intake_disposition in self._PROPOSAL_LIVE_DISPOSITIONS
                    else None
                ),
                proposed_by=r.proposed_by,
                proposed_at=r.proposed_at,
                cases=tuple(cases_by_complaint.get(str(r.id), ())),
                completed=(
                    (r.status or "").strip().upper() == "CLOSED"
                    and (r.intake_disposition or "").strip().upper() == "HQ_CLOSED"
                ),
                hq_destination_unit_id=r.hq_destination_unit_id,
                customer_id=r.customer_id,
            )
            for r in rows
        ]

    def list_pusat_units(self) -> list[PusatUnit]:
        """Active HQ CRO units — the only schedule destination in this app.

        Suban / Sekretariat remain Pusat for visibility, but are not booked
        here. Read from the org directory (Branch) rather than an ECMP-owned
        list. Capacity per unit is the only thing ECMP configures
        (hq.schedule.capacity_by_unit).
        """
        stmt = (
            select(Branch.code, Branch.name)
            .where(Branch.deleted_at.is_(None))
            .where(Branch.is_active.is_(True))
            .order_by(Branch.code)
        )
        return [
            PusatUnit(code=code, name=name)
            for code, name in self._session.execute(stmt)
            if is_hq_schedule_destination_unit(code)
        ]

    def _cases_by_complaint(self, complaint_ids: list[str]) -> dict[str, list[CaseRef]]:
        """Case.complaint_id is a plain string column (no FK) — join by hand."""
        if not complaint_ids:
            return {}
        stmt = (
            select(CmCaseORM.complaint_id, CmCaseORM.id, CmCaseORM.case_number)
            .where(CmCaseORM.complaint_id.in_(complaint_ids))
            .order_by(CmCaseORM.created_at)
        )
        result: dict[str, list[CaseRef]] = {}
        for complaint_id, case_id, case_number in self._session.execute(stmt):
            result.setdefault(complaint_id, []).append(
                CaseRef(case_id=str(case_id), case_number=case_number)
            )
        return result

    def commit(self) -> None:
        self._session.commit()
