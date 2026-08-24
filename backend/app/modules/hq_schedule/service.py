"""HQ arrival schedule availability + holiday calendar (advisory, read-mostly).

Pusat remains the sole authority over ``hq_arrival_date`` / ``hq_arrival_time``
(see cm_batch1.service.accept_and_schedule_at_hq / schedule_hq_arrival). This
service only answers "what does the grid look like" — it never writes a
complaint's schedule.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.core.errors import NotFoundError, ValidationAppError
from app.modules.cm_batch1.complaint_number import resolve_unit_code
from app.modules.hq_schedule.repository import (
    ArrivalRow,
    HqScheduleRepository,
    PusatUnit,
)
from app.modules.hq_schedule.schemas import (
    AvailabilityResponse,
    DayAvailability,
    HolidayCreateRequest,
    HolidayResponse,
    ProposalSummary,
    SlotAvailability,
    SlotUnitAvailability,
)
from app.modules.settings.registry import SettingsKey
from app.modules.settings.service import SettingsService

_MAX_RANGE_DAYS = 62

# Lab operators are WIB — see cm_batch1.service._operator_today for why UTC
# must not be used for "is this slot in the past" checks.
_OPERATOR_TZ = ZoneInfo("Asia/Jakarta")


def _parse_hhmm(value: str) -> time:
    hour_s, _, minute_s = value.partition(":")
    return time(hour=int(hour_s), minute=int(minute_s))


def _minutes(t: time) -> int:
    return t.hour * 60 + t.minute


def _from_minutes(value: int) -> time:
    return time(hour=value // 60, minute=value % 60)


def _parse_capacity_by_unit(raw: object) -> dict[str, int]:
    """``{"PUSAT-SEKRETARIAT": 1}`` -> ``{"PUSAT-SEKRETARIAT": 1}`` (upper keys).

    Units absent from the map keep ``capacity_per_slot``. Unreadable or
    negative entries are skipped rather than treated as zero, so a typo can
    never silently close a unit's whole day.
    """
    if not isinstance(raw, dict):
        return {}
    parsed: dict[str, int] = {}
    for key, value in raw.items():
        code = str(key).strip().upper()
        if not code:
            continue
        try:
            capacity = int(value)
        except (TypeError, ValueError):
            continue
        if capacity < 0:
            continue
        parsed[code] = capacity
    return parsed


def _same_unit(left: str | None, right: str | None) -> bool:
    return (left or "").strip().upper() == (right or "").strip().upper()


def _parse_break_overrides(raw: object) -> dict[int, tuple[time, time] | None]:
    """``{"5": {"start": "11:30", "end": "13:30"}}`` -> ``{5: (11:30, 13:30)}``.

    Keys are ISO weekdays (1=Mon..7=Sun); a ``null`` value means that weekday
    has no break at all. Unreadable entries are skipped so one bad key cannot
    hide the whole calendar — the weekday simply falls back to the default
    break window.
    """
    if not isinstance(raw, dict):
        return {}
    parsed: dict[int, tuple[time, time] | None] = {}
    for key, value in raw.items():
        try:
            weekday = int(key)
        except (TypeError, ValueError):
            continue
        if not 1 <= weekday <= 7:
            continue
        if value is None:
            parsed[weekday] = None
            continue
        if not isinstance(value, dict):
            continue
        start_raw = str(value.get("start", "")).strip()
        end_raw = str(value.get("end", "")).strip()
        if not start_raw or not end_raw:
            parsed[weekday] = None
            continue
        try:
            parsed[weekday] = (_parse_hhmm(start_raw), _parse_hhmm(end_raw))
        except ValueError:
            continue
    return parsed


@dataclass(frozen=True, slots=True)
class ScheduleConfig:
    start: time
    end: time
    slot_minutes: int
    capacity_per_slot: int
    workdays: frozenset[int]
    break_start: time | None
    break_end: time | None
    # ISO weekday -> break window replacing the default one for that day
    # (``None`` = that weekday has no break at all). Jumat 11:30-13:30 lives
    # here; Senin-Kamis keep break_start/break_end.
    break_overrides: Mapping[int, tuple[time, time] | None]
    # Pusat unit code (upper-cased) -> arrivals that unit accepts per full slot.
    # A unit absent from the map keeps ``capacity_per_slot`` (today every unit
    # is configured the same as CRO; the setting exists to change that).
    capacity_by_unit: Mapping[str, int]

    def capacity_for_unit(self, unit_code: str) -> int:
        return self.capacity_by_unit.get(
            unit_code.strip().upper(), self.capacity_per_slot
        )

    def break_for(self, weekday: int) -> tuple[time, time] | None:
        if weekday in self.break_overrides:
            return self.break_overrides[weekday]
        if self.break_start is None or self.break_end is None:
            return None
        return self.break_start, self.break_end


@dataclass(frozen=True, slots=True)
class SlotSpec:
    """One grid cell of a given weekday, after the break window is cut out.

    A break that does not land on grid boundaries (Jumat 11:30-13:30 on an
    hourly grid) splits the slot it crosses: the usable remainder stays
    bookable with a pro-rated capacity, the break itself becomes one
    ``is_break`` block so arrivals already booked inside it stay visible.
    """

    start: time
    end: time
    is_break: bool
    partial: bool
    # Minutes actually usable in this cell — capacity is pro-rated from it,
    # per unit, because each Pusat unit has its own quota.
    usable_minutes: int


class HqScheduleService:
    def __init__(
        self, repository: HqScheduleRepository, settings_service: SettingsService
    ) -> None:
        self._repo = repository
        self._settings = settings_service

    def _load_config(self) -> ScheduleConfig:
        start_raw = self._settings.get_string(
            SettingsKey.HQ_SCHEDULE_START, default="08:00"
        )
        end_raw = self._settings.get_string(SettingsKey.HQ_SCHEDULE_END, default="16:00")
        slot_minutes = self._settings.get_int(
            SettingsKey.HQ_SCHEDULE_SLOT_MINUTES, default=60
        )
        capacity = self._settings.get_int(
            SettingsKey.HQ_SCHEDULE_CAPACITY_PER_SLOT, default=2
        )
        workdays_raw = self._settings.get_string(
            SettingsKey.HQ_SCHEDULE_WORKDAYS, default="1,2,3,4,5"
        )
        try:
            workdays = frozenset(
                int(part.strip())
                for part in workdays_raw.split(",")
                if part.strip()
            )
        except ValueError:
            workdays = frozenset({1, 2, 3, 4, 5})
        break_start_raw = self._settings.get_string(
            SettingsKey.HQ_SCHEDULE_BREAK_START, default="12:00"
        ).strip()
        break_end_raw = self._settings.get_string(
            SettingsKey.HQ_SCHEDULE_BREAK_END, default="13:00"
        ).strip()
        break_start = _parse_hhmm(break_start_raw) if break_start_raw else None
        break_end = _parse_hhmm(break_end_raw) if break_end_raw else None
        try:
            overrides_raw = self._settings.get_json(
                SettingsKey.HQ_SCHEDULE_BREAK_OVERRIDES, default={}
            )
        except ValidationAppError:
            # Malformed JSON must not take the whole calendar down — same
            # tolerance as the workdays setting above.
            overrides_raw = {}
        try:
            capacity_by_unit_raw = self._settings.get_json(
                SettingsKey.HQ_SCHEDULE_CAPACITY_BY_UNIT, default={}
            )
        except ValidationAppError:
            capacity_by_unit_raw = {}
        return ScheduleConfig(
            start=_parse_hhmm(start_raw),
            end=_parse_hhmm(end_raw),
            slot_minutes=max(1, slot_minutes),
            capacity_per_slot=max(0, capacity),
            workdays=workdays or frozenset({1, 2, 3, 4, 5}),
            break_start=break_start,
            break_end=break_end,
            break_overrides=_parse_break_overrides(overrides_raw),
            capacity_by_unit=_parse_capacity_by_unit(capacity_by_unit_raw),
        )

    @staticmethod
    def _prorated_capacity(capacity: int, *, minutes: int, slot_minutes: int) -> int:
        """Capacity of a shortened slot, floored — but never silently zero.

        Default 2 arrivals/hour, Jumat 11:00-11:30 -> 1. An odd capacity
        rounds down (3/hour -> 1 for a half slot) per the business decision.
        """
        if capacity <= 0 or minutes <= 0:
            return 0
        if minutes >= slot_minutes:
            return capacity
        return max(1, capacity * minutes // slot_minutes)

    @staticmethod
    def _generate_slots(config: ScheduleConfig, weekday: int) -> list[SlotSpec]:
        day_start = _minutes(config.start)
        day_end = _minutes(config.end)
        window = config.break_for(weekday)
        break_lo = break_hi = None
        if window is not None:
            break_lo, break_hi = _minutes(window[0]), _minutes(window[1])
            if break_hi <= break_lo:  # inverted/empty window — ignore it
                break_lo = break_hi = None

        specs: list[SlotSpec] = []
        cursor = day_start
        while cursor + config.slot_minutes <= day_end:
            nxt = cursor + config.slot_minutes
            overlaps = (
                break_lo is not None
                and break_hi is not None
                and cursor < break_hi
                and break_lo < nxt
            )
            if not overlaps:
                specs.append(
                    SlotSpec(
                        start=_from_minutes(cursor),
                        end=_from_minutes(nxt),
                        is_break=False,
                        partial=False,
                        usable_minutes=nxt - cursor,
                    )
                )
            else:
                # Keep whatever minutes fall outside the break as a shortened,
                # still-bookable slot; a slot fully inside the break vanishes
                # into the break block appended below.
                assert break_lo is not None and break_hi is not None
                for lo, hi in ((cursor, break_lo), (break_hi, nxt)):
                    if lo >= hi:
                        continue
                    specs.append(
                        SlotSpec(
                            start=_from_minutes(lo),
                            end=_from_minutes(hi),
                            is_break=False,
                            partial=True,
                            usable_minutes=hi - lo,
                        )
                    )
            cursor = nxt

        if break_lo is not None and break_hi is not None:
            lo, hi = max(break_lo, day_start), min(break_hi, day_end)
            if lo < hi:
                specs.append(
                    SlotSpec(
                        start=_from_minutes(lo),
                        end=_from_minutes(hi),
                        is_break=True,
                        partial=False,
                        usable_minutes=0,
                    )
                )
        specs.sort(key=lambda spec: (spec.start, spec.end))
        return specs

    def _closed_reason(
        self,
        day: date,
        *,
        config: ScheduleConfig,
        holiday_labels: dict[date, str],
    ) -> tuple[bool, str | None, str | None]:
        if day in holiday_labels:
            return True, "HOLIDAY", holiday_labels[day]
        if day.isoweekday() not in config.workdays:
            return True, "WEEKEND", None
        return False, None, None

    def get_availability(
        self,
        *,
        date_from: date,
        date_to: date,
        detail: bool,
    ) -> AvailabilityResponse:
        if date_to < date_from:
            raise ValidationAppError(
                "to must not be before from",
                details={"field": "to"},
            )
        if (date_to - date_from).days > _MAX_RANGE_DAYS:
            raise ValidationAppError(
                f"range must not exceed {_MAX_RANGE_DAYS} days",
                details={"field": "to", "maxDays": _MAX_RANGE_DAYS},
            )

        config = self._load_config()
        # The grid now differs per weekday (Jumat has a longer break), so it is
        # built once per weekday instead of once per range.
        slots_by_weekday: dict[int, list[SlotSpec]] = {}
        holidays = {
            row.holiday_date: row.label
            for row in self._repo.list_holidays(date_from=date_from, date_to=date_to)
        }
        arrivals = self._repo.list_arrivals_in_range(
            date_from=date_from, date_to=date_to
        )
        # Pusat is not one door: CRO schedules the taxpayer into its own
        # counter, Sekretariat or a Suban, and each of those has its own quota.
        units = self._repo.list_pusat_units()
        now = datetime.now(_OPERATOR_TZ)

        days: list[DayAvailability] = []
        cursor = date_from
        while cursor <= date_to:
            closed, reason, label = self._closed_reason(
                cursor, config=config, holiday_labels=holidays
            )
            day_slots: list[SlotAvailability] = []
            if not closed:
                weekday = cursor.isoweekday()
                specs = slots_by_weekday.get(weekday)
                if specs is None:
                    specs = self._generate_slots(config, weekday)
                    slots_by_weekday[weekday] = specs
                day_slots = self._slots_for_day(
                    cursor,
                    specs,
                    arrivals,
                    units,
                    config=config,
                    detail=detail,
                    now=now,
                )
            days.append(
                DayAvailability(
                    date=cursor,
                    weekday=cursor.isoweekday(),
                    closed=closed,
                    closedReason=reason,
                    holidayLabel=label,
                    slots=day_slots,
                )
            )
            cursor += timedelta(days=1)

        return AvailabilityResponse(
            startTime=config.start.strftime("%H:%M"),
            endTime=config.end.strftime("%H:%M"),
            slotMinutes=config.slot_minutes,
            capacityPerSlot=config.capacity_per_slot,
            days=days,
        )

    @classmethod
    def _slots_for_day(
        cls,
        day: date,
        slots: list[SlotSpec],
        arrivals: list[ArrivalRow],
        units: list[PusatUnit],
        *,
        config: ScheduleConfig,
        detail: bool,
        now: datetime,
    ) -> list[SlotAvailability]:
        scheduled_for_day = [
            a for a in arrivals if a.hq_arrival_date == day and a.hq_arrival_time
        ]
        proposed_for_day = [
            a
            for a in arrivals
            if a.proposed_arrival_date == day and a.proposed_arrival_time
        ]

        result: list[SlotAvailability] = []
        for spec in slots:
            slot_start, slot_end = spec.start, spec.end
            lo, hi = _minutes(slot_start), _minutes(slot_end)
            is_break = spec.is_break

            def in_slot(value: str | None, *, lo: int = lo, hi: int = hi) -> bool:
                if not value:
                    return False
                try:
                    t = _parse_hhmm(value)
                except (ValueError, IndexError):
                    return False
                return lo <= _minutes(t) < hi

            scheduled = [a for a in scheduled_for_day if in_slot(a.hq_arrival_time)]
            proposed = [a for a in proposed_for_day if in_slot(a.proposed_arrival_time)]
            # Total occupants — completed visits still count toward the slot's
            # booked ratio; only future bookability (below) cares about "live".
            scheduled_count = len(scheduled)
            completed_count = sum(1 for a in scheduled if a.completed)
            proposed_count = len(proposed)
            slot_start_dt = datetime.combine(day, slot_start, tzinfo=_OPERATOR_TZ)
            future = slot_start_dt > now

            def unit_capacity(
                code: str,
                *,
                closed: bool = is_break,
                minutes: int = spec.usable_minutes,
            ) -> int:
                if closed:
                    return 0
                return cls._prorated_capacity(
                    config.capacity_for_unit(code),
                    minutes=minutes,
                    slot_minutes=config.slot_minutes,
                )

            unit_rows: list[SlotUnitAvailability] = []
            if units:
                capacity = 0
                available = 0
                for unit in units:
                    cap = unit_capacity(unit.code)
                    booked = [
                        a
                        for a in scheduled
                        if _same_unit(a.hq_destination_unit_id, unit.code)
                    ]
                    unit_available = max(0, cap - len(booked))
                    capacity += cap
                    available += unit_available
                    unit_rows.append(
                        SlotUnitAvailability(
                            unitCode=unit.code,
                            unitName=unit.name,
                            capacity=cap,
                            scheduledCount=len(booked),
                            completedCount=sum(1 for a in booked if a.completed),
                            availableCount=unit_available,
                            bookable=not is_break and future and unit_available > 0,
                        )
                    )
            else:
                # No Pusat unit in the org directory (bare lab DB): fall back to
                # one shared pool, exactly the pre-per-unit behaviour.
                capacity = (
                    0
                    if is_break
                    else cls._prorated_capacity(
                        config.capacity_per_slot,
                        minutes=spec.usable_minutes,
                        slot_minutes=config.slot_minutes,
                    )
                )
                available = max(0, capacity - scheduled_count)
            # Arrivals scheduled before the destination column existed occupy no
            # unit's quota — they stay listed, but must not close a unit's slot.
            bookable = not is_break and future and available > 0
            bookable_count = available if bookable else 0
            pending: list[ProposalSummary] = []
            if detail:
                pending = [
                    ProposalSummary(
                        complaintId=a.complaint_id,
                        complaintNumber=a.complaint_number,
                        owningUnitId=a.owning_unit_id,
                        unitCode=resolve_unit_code(a.owning_unit_id),
                        proposedBy=a.proposed_by,
                        proposedAt=a.proposed_at,
                    )
                    for a in proposed
                ]
            # Case numbers are visible to every caller (Pusat and all Cabang) so the
            # board reads correctly; only the frontend's canOpenCase gates the link
            # to the complaint (own unit or Pusat) — see HqScheduleView.canOpenCase.
            scheduled_cases = [
                ProposalSummary(
                    complaintId=a.complaint_id,
                    complaintNumber=a.complaint_number,
                    owningUnitId=a.owning_unit_id,
                    unitCode=resolve_unit_code(a.owning_unit_id),
                    caseNumbers=list(a.case_numbers),
                    completed=a.completed,
                    # Where the taxpayer reports — set by CRO Pusat together
                    # with the final time; unitCode above is the origin branch.
                    destinationUnitCode=a.hq_destination_unit_id,
                )
                for a in scheduled
            ]
            result.append(
                SlotAvailability(
                    startTime=slot_start.strftime("%H:%M"),
                    endTime=slot_end.strftime("%H:%M"),
                    capacity=capacity,
                    isBreak=is_break,
                    partial=spec.partial,
                    # Pusat-internal structure is detail-only: a branch never
                    # picks the destination unit, it only proposes a time.
                    units=unit_rows if detail else [],
                    scheduledCount=scheduled_count,
                    completedCount=completed_count,
                    proposedCount=proposed_count,
                    availableCount=available,
                    bookable=bookable,
                    bookableCount=bookable_count,
                    pendingProposals=pending,
                    scheduledCases=scheduled_cases,
                )
            )
        return result

    # -- Holidays -----------------------------------------------------------

    def list_holidays(self, *, date_from: date, date_to: date) -> list[HolidayResponse]:
        return [
            HolidayResponse.model_validate(row)
            for row in self._repo.list_holidays(date_from=date_from, date_to=date_to)
        ]

    def create_holiday(
        self, body: HolidayCreateRequest, *, actor_id: str | None
    ) -> HolidayResponse:
        label = body.label.strip()
        if not label:
            raise ValidationAppError(
                "label is required", details={"field": "label"}
            )
        existing = self._repo.get_holiday(body.holiday_date)
        if existing is not None:
            existing.label = label
            existing.created_by = actor_id
            self._repo.commit()
            return HolidayResponse.model_validate(existing)
        row = self._repo.create_holiday(
            holiday_date=body.holiday_date, label=label, created_by=actor_id
        )
        self._repo.commit()
        return HolidayResponse.model_validate(row)

    def delete_holiday(self, holiday_date: date) -> None:
        deleted = self._repo.delete_holiday(holiday_date)
        if not deleted:
            raise NotFoundError("Holiday not found")
        self._repo.commit()
