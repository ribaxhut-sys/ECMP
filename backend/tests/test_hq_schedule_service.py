"""HQ arrival schedule availability — slot grid, weekend/holiday, capacity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

import pytest

from app.core.errors import NotFoundError, ValidationAppError
from app.modules.hq_schedule.repository import ArrivalRow
from app.modules.hq_schedule.schemas import HolidayCreateRequest
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
    created_by: str | None = None
    created_at: datetime = datetime(2026, 8, 17, tzinfo=UTC)


class _FakeHqScheduleRepository:
    def __init__(
        self,
        *,
        holidays: list[_FakeHoliday] | None = None,
        arrivals: list[ArrivalRow] | None = None,
    ) -> None:
        self._holidays = holidays or []
        self._arrivals = arrivals or []
        self.committed = False

    def list_holidays(self, *, date_from: date, date_to: date) -> list[_FakeHoliday]:
        return [h for h in self._holidays if date_from <= h.holiday_date <= date_to]

    def get_holiday(self, holiday_date: date) -> _FakeHoliday | None:
        return next((h for h in self._holidays if h.holiday_date == holiday_date), None)

    def create_holiday(
        self, *, holiday_date: date, label: str, created_by: str | None
    ) -> _FakeHoliday:
        row = _FakeHoliday(
            holiday_date=holiday_date,
            label=label,
            created_by=created_by,
            created_at=datetime.now(UTC),
        )
        self._holidays.append(row)
        return row

    def delete_holiday(self, holiday_date: date) -> bool:
        before = len(self._holidays)
        self._holidays = [h for h in self._holidays if h.holiday_date != holiday_date]
        return len(self._holidays) < before

    def commit(self) -> None:
        self.committed = True

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


def test_scheduled_cases_visible_to_every_caller_on_aggregate_view() -> None:
    """Case numbers are visible branch-wide; only the frontend gates the click
    to a complaint (own unit or Pusat) via canOpenCase."""
    monday = _next_monday(date.today())
    arrivals = [
        ArrivalRow(
            complaint_id="c1",
            complaint_number="TAB-2608-0001",
            owning_unit_id="UPPPD-TANAH-ABANG",
            hq_arrival_date=monday,
            hq_arrival_time="08:00",
            proposed_arrival_date=None,
            proposed_arrival_time=None,
            proposed_by=None,
            proposed_at=None,
            case_numbers=("CASE-2026-000001", "CASE-2026-000002"),
        ),
        ArrivalRow(
            complaint_id="c2",
            complaint_number="GAM-2608-0001",
            owning_unit_id="UPPPD-GAMBIR",
            hq_arrival_date=monday,
            hq_arrival_time="08:15",
            proposed_arrival_date=None,
            proposed_arrival_time=None,
            proposed_by=None,
            proposed_at=None,
        ),
    ]
    repo = _FakeHqScheduleRepository(arrivals=arrivals)
    service = HqScheduleService(repo, _settings_service())

    branch_view = service.get_availability(
        date_from=monday, date_to=monday, detail=False
    )
    branch_slot = branch_view.days[0].slots[0]
    assert sorted(c.complaint_number for c in branch_slot.scheduled_cases) == [
        "GAM-2608-0001",
        "TAB-2608-0001",
    ]
    tab_case = next(
        c for c in branch_slot.scheduled_cases if c.complaint_number == "TAB-2608-0001"
    )
    assert tab_case.case_numbers == ["CASE-2026-000001", "CASE-2026-000002"]

    pusat_view = service.get_availability(
        date_from=monday, date_to=monday, detail=True
    )
    pusat_slot = pusat_view.days[0].slots[0]
    assert sorted(c.complaint_number for c in pusat_slot.scheduled_cases) == [
        "GAM-2608-0001",
        "TAB-2608-0001",
    ]
    assert pusat_slot.scheduled_cases[0].unit_code in {"TAB", "GAM"}


def test_break_slot_tagged_and_excluded_from_open_capacity() -> None:
    monday = _next_monday(date.today())
    service = HqScheduleService(
        _FakeHqScheduleRepository(),
        _settings_service(
            **{
                SettingsKey.HQ_SCHEDULE_END.value: "11:00",
                SettingsKey.HQ_SCHEDULE_BREAK_START.value: "09:00",
                SettingsKey.HQ_SCHEDULE_BREAK_END.value: "10:00",
            }
        ),
    )
    resp = service.get_availability(date_from=monday, date_to=monday, detail=False)
    slots_by_start = {s.start_time: s for s in resp.days[0].slots}
    assert slots_by_start["08:00"].is_break is False
    assert slots_by_start["09:00"].is_break is True
    assert slots_by_start["10:00"].is_break is False


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


def test_invalid_workdays_setting_falls_back_to_weekdays() -> None:
    monday = _next_monday(date.today())
    service = HqScheduleService(
        _FakeHqScheduleRepository(),
        _settings_service(**{SettingsKey.HQ_SCHEDULE_WORKDAYS.value: "1,x,3"}),
    )
    resp = service.get_availability(date_from=monday, date_to=monday, detail=False)
    assert not resp.days[0].closed


def test_completed_visit_stays_listed_without_occupying_capacity() -> None:
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
            case_numbers=("CASE-1",),
            completed=True,
        ),
        ArrivalRow(
            complaint_id="c2",
            complaint_number="CMP-2",
            owning_unit_id="PUSAT",
            hq_arrival_date=monday,
            hq_arrival_time="08:45",
            proposed_arrival_date=None,
            proposed_arrival_time=None,
            proposed_by=None,
            proposed_at=None,
            case_numbers=("CASE-2",),
            completed=False,
        ),
    ]
    slot = HqScheduleService(
        _FakeHqScheduleRepository(arrivals=arrivals), _settings_service()
    ).get_availability(date_from=monday, date_to=monday, detail=True).days[0].slots[0]
    assert slot.scheduled_count == 1
    assert slot.available_count == 1
    assert len(slot.scheduled_cases) == 2
    by_id = {case.complaint_id: case for case in slot.scheduled_cases}
    assert by_id["c1"].completed is True
    assert by_id["c2"].completed is False


def test_malformed_arrival_times_are_ignored() -> None:
    monday = _next_monday(date.today())
    arrivals = [
        ArrivalRow(
            complaint_id="c1",
            complaint_number="CMP-1",
            owning_unit_id="PUSAT",
            hq_arrival_date=monday,
            hq_arrival_time="xx:yy",
            proposed_arrival_date=monday,
            proposed_arrival_time="",
            proposed_by=None,
            proposed_at=None,
        )
    ]
    service = HqScheduleService(
        _FakeHqScheduleRepository(arrivals=arrivals), _settings_service()
    )
    slot = service.get_availability(
        date_from=monday, date_to=monday, detail=True
    ).days[0].slots[0]
    assert slot.scheduled_count == 0
    assert slot.proposed_count == 0


def test_holiday_crud_relabels_creates_and_deletes() -> None:
    monday = _next_monday(date.today())
    repo = _FakeHqScheduleRepository(
        holidays=[_FakeHoliday(holiday_date=monday, label="Lama")]
    )
    service = HqScheduleService(repo, _settings_service())
    listed = service.list_holidays(date_from=monday, date_to=monday)
    assert listed[0].label == "Lama"

    updated = service.create_holiday(
        HolidayCreateRequest.model_validate(
            {"holidayDate": monday.isoformat(), "label": "Baru"}
        ),
        actor_id="hq-1",
    )
    assert updated.label == "Baru"
    assert repo.committed is True

    with pytest.raises(ValidationAppError):
        service.create_holiday(
            HolidayCreateRequest.model_validate(
                {"holidayDate": monday.isoformat(), "label": "   "}
            ),
            actor_id="hq-1",
        )

    tuesday = monday + timedelta(days=1)
    created = service.create_holiday(
        HolidayCreateRequest.model_validate(
            {"holidayDate": tuesday.isoformat(), "label": "Cuti"}
        ),
        actor_id="hq-1",
    )
    assert created.label == "Cuti"

    service.delete_holiday(tuesday)
    with pytest.raises(NotFoundError):
        service.delete_holiday(tuesday + timedelta(days=1))
