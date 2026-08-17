"""HQ arrival schedule persistence — holidays + arrival/proposal read-side."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.modules.cm_batch1.models import CmBatch1ComplaintORM
from app.modules.hq_schedule.models import CmHqHolidayORM


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
        self, *, holiday_date: date, label: str, created_by: str | None
    ) -> CmHqHolidayORM:
        row = CmHqHolidayORM(
            holiday_date=holiday_date,
            label=label,
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
        """Open complaints with a scheduled or proposed slot in [date_from, date_to]."""
        stmt = (
            select(CmBatch1ComplaintORM)
            .where(CmBatch1ComplaintORM.status != "CLOSED")
            .where(
                or_(
                    CmBatch1ComplaintORM.hq_arrival_date.between(date_from, date_to),
                    CmBatch1ComplaintORM.proposed_arrival_date.between(
                        date_from, date_to
                    ),
                )
            )
        )
        rows = self._session.scalars(stmt).all()
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
            )
            for r in rows
        ]

    def commit(self) -> None:
        self._session.commit()
