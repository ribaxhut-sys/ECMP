"""HQ arrival schedule availability — slot grid, weekend/holiday, capacity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

import pytest

from app.core.errors import ValidationAppError
from app.modules.hq_schedule.repository import ArrivalRow
from app.modules.hq_schedule.service import HqScheduleService
from app.modules.settings.registry import SettingsKey
from app.modules.settings.service import SettingsService


@dataclass
class _FakeSettingRow:
    value: str


class _FakeSettingsRepository:
    def __init__(self, values: dict[str, str]) -> None:
        self._values = values

    def get_by_key(self, key: str) -> _FakeSettingRow | None:
        if key not in self._values:
            return None
        return _FakeSettingRow(value=self._values[key])


@dataclass
class _FakeHoliday:
    holiday_date: date
    label: str


class _FakeHqScheduleRepository:
    def __init__(
        self,
        *,
        holidays: list[_FakeHoliday] | None = None,
        arrivals: list[ArrivalRow] | None = None,
    ) -> None:
        self._holidays = holidays or []
        self._arrivals = arrivals or []

    def list_holidays(self, *, date_from: date, date_to: date) -> list[_FakeHoliday]:
        return [h for h in self._holidays if date_from <= h.holiday_date <= date_to]

    def list_arrivals_in_range(
        self, *, date_from: date, date_to: date
    ) -> list[ArrivalRow]:
        return list(self._arrivals)


def _settings_service(**overrides: str) -> SettingsService:
    values = {
        SettingsKey.HQ_SCHEDULE_START.value: "08:00",
        SettingsKey.HQ_SCHEDULE_END.value: "10:00",
        SettingsKey.HQ_SCHEDULE_SLOT_MINUTES.value: "60",
        SettingsKey.HQ_SCHEDULE_CAPACITY_PER_SLOT.value: "2",
        SettingsKey.HQ_SCHEDULE_WORKDAYS.value: "1,2,3,4,5",
    }
    values.update(overrides)
    return SettingsService(_FakeSettingsRepository(values))


def _next_monday(start: date) -> date:
    cursor = start
    while cursor.isoweekday() != 1:
        cursor += timedelta(days=1)
    return cursor


def test_slots_generated_from_settings() -> None:
    monday = _next_monday(date.today())
    service = HqScheduleService(_FakeHqScheduleRepository(), _settings_service())
    resp = service.get_availability(date_from=monday, date_to=monday, detail=False)
    day = resp.days[0]
    assert not day.closed
    assert [s.start_time for s in day.slots] == ["08:00", "09:00"]
    assert day.slots[0].capacity == 2
    assert day.slots[0].available_count == 2


def test_weekend_marked_closed() -> None:
    monday = _next_monday(date.today())
    saturday = monday + timedelta(days=5)
    service = HqScheduleService(_FakeHqScheduleRepository(), _settings_service())
    resp = service.get_availability(
        date_from=saturday, date_to=saturday, detail=False
    )
    day = resp.days[0]
    assert day.closed
    assert day.closed_reason == "WEEKEND"
    assert day.slots == []


def test_holiday_marked_closed_with_label() -> None:
    monday = _next_monday(date.today())
    repo = _FakeHqScheduleRepository(
        holidays=[_FakeHoliday(holiday_date=monday, label="Cuti bersama")]
    )
    service = HqScheduleService(repo, _settings_service())
    resp = service.get_availability(date_from=monday, date_to=monday, detail=False)
    day = resp.days[0]
    assert day.closed
    assert day.closed_reason == "HOLIDAY"
    assert day.holiday_label == "Cuti bersama"


def test_scheduled_and_proposed_counted_separately() -> None:
    monday = _next_monday(date.today())
    arrivals = [
        ArrivalRow(
            complaint_id="c1",
            complaint_number="CMP-1",
            owning_unit_id="PUSAT",
            hq_arrival_date=monday,
            hq_arrival_time="08:30",
            proposed_arrival_date=None,
            proposed_arrival_time=None,
            proposed_by=None,
            proposed_at=None,
        ),
        ArrivalRow(
            complaint_id="c2",
            complaint_number="CMP-2",
            owning_unit_id="UPPPD-A",
            hq_arrival_date=None,
            hq_arrival_time=None,
            proposed_arrival_date=monday,
            proposed_arrival_time="08:45",
            proposed_by="agent-1",
            proposed_at=None,
        ),
    ]
    repo = _FakeHqScheduleRepository(arrivals=arrivals)
    service = HqScheduleService(repo, _settings_service())

    branch_resp = service.get_availability(
        date_from=monday, date_to=monday, detail=False
    )
    slot = branch_resp.days[0].slots[0]
    assert slot.scheduled_count == 1
    assert slot.proposed_count == 1
    assert slot.available_count == 1  # capacity 2 - 1 scheduled
    assert slot.pending_proposals == []  # branch view never exposes detail

    pusat_resp = service.get_availability(
        date_from=monday, date_to=monday, detail=True
    )
    pusat_slot = pusat_resp.days[0].slots[0]
    assert len(pusat_slot.pending_proposals) == 1
    assert pusat_slot.pending_proposals[0].complaint_number == "CMP-2"


def test_range_too_large_rejected() -> None:
    service = HqScheduleService(_FakeHqScheduleRepository(), _settings_service())
    with pytest.raises(ValidationAppError):
        service.get_availability(
            date_from=date.today(),
            date_to=date.today() + timedelta(days=90),
            detail=False,
        )


def test_to_before_from_rejected() -> None:
    service = HqScheduleService(_FakeHqScheduleRepository(), _settings_service())
    with pytest.raises(ValidationAppError):
        service.get_availability(
            date_from=date.today(),
            date_to=date.today() - timedelta(days=1),
            detail=False,
        )
