"""HQ arrival schedule availability + holiday calendar (advisory, read-mostly).

Pusat remains the sole authority over ``hq_arrival_date`` / ``hq_arrival_time``
(see cm_batch1.service.accept_and_schedule_at_hq / schedule_hq_arrival). This
service only answers "what does the grid look like" — it never writes a
complaint's schedule.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time, timedelta

from app.core.errors import NotFoundError, ValidationAppError
from app.modules.cm_batch1.complaint_number import resolve_unit_code
from app.modules.hq_schedule.repository import ArrivalRow, HqScheduleRepository
from app.modules.hq_schedule.schemas import (
    AvailabilityResponse,
    DayAvailability,
    HolidayCreateRequest,
    HolidayResponse,
    ProposalSummary,
    SlotAvailability,
)
from app.modules.settings.registry import SettingsKey
from app.modules.settings.service import SettingsService

_MAX_RANGE_DAYS = 62


def _parse_hhmm(value: str) -> time:
    hour_s, _, minute_s = value.partition(":")
    return time(hour=int(hour_s), minute=int(minute_s))


def _minutes(t: time) -> int:
    return t.hour * 60 + t.minute


@dataclass(frozen=True, slots=True)
class ScheduleConfig:
    start: time
    end: time
    slot_minutes: int
    capacity_per_slot: int
    workdays: frozenset[int]
    break_start: time | None
    break_end: time | None


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
        return ScheduleConfig(
            start=_parse_hhmm(start_raw),
            end=_parse_hhmm(end_raw),
            slot_minutes=max(1, slot_minutes),
            capacity_per_slot=max(0, capacity),
            workdays=workdays or frozenset({1, 2, 3, 4, 5}),
            break_start=break_start,
            break_end=break_end,
        )

    @staticmethod
    def _generate_slots(config: ScheduleConfig) -> list[tuple[time, time]]:
        slots: list[tuple[time, time]] = []
        cursor = _minutes(config.start)
        end = _minutes(config.end)
        while cursor + config.slot_minutes <= end:
            slot_start = time(hour=cursor // 60, minute=cursor % 60)
            nxt = cursor + config.slot_minutes
            slot_end = time(hour=nxt // 60, minute=nxt % 60)
            slots.append((slot_start, slot_end))
            cursor = nxt
        return slots

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
        caller_unit_id: str | None = None,
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
        slots = self._generate_slots(config)
        holidays = {
            row.holiday_date: row.label
            for row in self._repo.list_holidays(date_from=date_from, date_to=date_to)
        }
        arrivals = self._repo.list_arrivals_in_range(
            date_from=date_from, date_to=date_to
        )

        days: list[DayAvailability] = []
        cursor = date_from
        while cursor <= date_to:
            closed, reason, label = self._closed_reason(
                cursor, config=config, holiday_labels=holidays
            )
            day_slots: list[SlotAvailability] = []
            if not closed:
                day_slots = self._slots_for_day(
                    cursor,
                    slots,
                    arrivals,
                    config=config,
                    detail=detail,
                    caller_unit_id=caller_unit_id,
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

    @staticmethod
    def _slots_for_day(
        day: date,
        slots: list[tuple[time, time]],
        arrivals: list[ArrivalRow],
        *,
        config: ScheduleConfig,
        detail: bool,
        caller_unit_id: str | None,
    ) -> list[SlotAvailability]:
        scheduled_for_day = [
            a for a in arrivals if a.hq_arrival_date == day and a.hq_arrival_time
        ]
        proposed_for_day = [
            a
            for a in arrivals
            if a.proposed_arrival_date == day and a.proposed_arrival_time
        ]

        break_lo = _minutes(config.break_start) if config.break_start else None
        break_hi = _minutes(config.break_end) if config.break_end else None

        result: list[SlotAvailability] = []
        for slot_start, slot_end in slots:
            lo, hi = _minutes(slot_start), _minutes(slot_end)
            is_break = (
                break_lo is not None
                and break_hi is not None
                and lo < break_hi
                and break_lo < hi
            )

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
            scheduled_count = len(scheduled)
            proposed_count = len(proposed)
            available = max(0, config.capacity_per_slot - scheduled_count)
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
            # Pusat (detail=True) sees every branch's scheduled cases; a Cabang
            # caller only ever gets its own — never another branch's case
            # identity, not even to filter client-side.
            caller_code = (
                None if caller_unit_id is None else resolve_unit_code(caller_unit_id)
            )
            visible_scheduled = (
                scheduled
                if detail
                else [
                    a
                    for a in scheduled
                    if caller_code is not None
                    and resolve_unit_code(a.owning_unit_id) == caller_code
                ]
            )
            scheduled_cases = [
                ProposalSummary(
                    complaintId=a.complaint_id,
                    complaintNumber=a.complaint_number,
                    owningUnitId=a.owning_unit_id,
                    unitCode=resolve_unit_code(a.owning_unit_id),
                )
                for a in visible_scheduled
            ]
            result.append(
                SlotAvailability(
                    startTime=slot_start.strftime("%H:%M"),
                    endTime=slot_end.strftime("%H:%M"),
                    capacity=config.capacity_per_slot,
                    isBreak=is_break,
                    scheduledCount=scheduled_count,
                    proposedCount=proposed_count,
                    availableCount=available,
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
