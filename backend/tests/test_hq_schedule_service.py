"""HQ arrival schedule availability — slot grid, weekend/holiday, capacity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

import pytest

from app.core.errors import NotFoundError, ValidationAppError
from app.modules.hq_schedule.repository import ArrivalRow, CaseRef, PusatUnit
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
        pusat_units: list[PusatUnit] | None = None,
    ) -> None:
        self._holidays = holidays or []
        self._arrivals = arrivals or []
        self._pusat_units = pusat_units or []
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

    def list_pusat_units(self) -> list[PusatUnit]:
        return list(self._pusat_units)


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
            cases=(
                CaseRef(case_id="case-id-1", case_number="CASE-2026-000001"),
                CaseRef(case_id="case-id-2", case_number="CASE-2026-000002"),
            ),
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
    assert [(c.case_id, c.case_number) for c in tab_case.cases] == [
        ("case-id-1", "CASE-2026-000001"),
        ("case-id-2", "CASE-2026-000002"),
    ]

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


def test_completed_visit_still_counts_toward_scheduled_ratio() -> None:
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
            cases=(CaseRef(case_id="case-id-1", case_number="CASE-1"),),
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
            cases=(CaseRef(case_id="case-id-2", case_number="CASE-2"),),
            completed=False,
        ),
    ]
    slot = HqScheduleService(
        _FakeHqScheduleRepository(arrivals=arrivals), _settings_service()
    ).get_availability(date_from=monday, date_to=monday, detail=True).days[0].slots[0]
    assert slot.scheduled_count == 2
    assert slot.completed_count == 1
    assert slot.available_count == 0
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


def test_past_day_slots_are_never_bookable() -> None:
    # A week before the next Monday is always strictly in the past, whatever
    # day the suite runs on.
    past_monday = _next_monday(date.today()) - timedelta(days=7)
    service = HqScheduleService(_FakeHqScheduleRepository(), _settings_service())
    day = service.get_availability(
        date_from=past_monday, date_to=past_monday, detail=False
    ).days[0]
    assert all(not s.bookable and s.bookable_count == 0 for s in day.slots)
    # available_count stays the raw capacity figure — only bookable is time-gated.
    assert day.slots[0].available_count == day.slots[0].capacity


def test_future_day_open_slot_is_bookable() -> None:
    # A week after the next Monday is always strictly in the future.
    future_monday = _next_monday(date.today()) + timedelta(days=7)
    service = HqScheduleService(_FakeHqScheduleRepository(), _settings_service())
    day = service.get_availability(
        date_from=future_monday, date_to=future_monday, detail=False
    ).days[0]
    slot = day.slots[0]
    assert slot.bookable is True
    assert slot.bookable_count == slot.available_count == slot.capacity


def test_full_future_slot_is_not_bookable() -> None:
    future_monday = _next_monday(date.today()) + timedelta(days=7)
    arrivals = [
        ArrivalRow(
            complaint_id=f"c{i}",
            complaint_number=f"CMP-{i}",
            owning_unit_id="PUSAT",
            hq_arrival_date=future_monday,
            hq_arrival_time="08:30",
            proposed_arrival_date=None,
            proposed_arrival_time=None,
            proposed_by=None,
            proposed_at=None,
        )
        for i in range(2)  # capacity_per_slot default is 2
    ]
    service = HqScheduleService(
        _FakeHqScheduleRepository(arrivals=arrivals), _settings_service()
    )
    slot = service.get_availability(
        date_from=future_monday, date_to=future_monday, detail=False
    ).days[0].slots[0]
    assert slot.available_count == 0
    assert slot.bookable is False
    assert slot.bookable_count == 0


def test_break_slot_is_never_bookable() -> None:
    future_monday = _next_monday(date.today()) + timedelta(days=7)
    service = HqScheduleService(
        _FakeHqScheduleRepository(),
        _settings_service(
            **{
                SettingsKey.HQ_SCHEDULE_START.value: "08:00",
                SettingsKey.HQ_SCHEDULE_END.value: "10:00",
                SettingsKey.HQ_SCHEDULE_SLOT_MINUTES.value: "60",
                SettingsKey.HQ_SCHEDULE_BREAK_START.value: "08:00",
                SettingsKey.HQ_SCHEDULE_BREAK_END.value: "09:00",
            }
        ),
    )
    slot = service.get_availability(
        date_from=future_monday, date_to=future_monday, detail=False
    ).days[0].slots[0]
    assert slot.is_break is True
    assert slot.bookable is False


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


def _next_friday(start: date) -> date:
    cursor = start
    while cursor.isoweekday() != 5:
        cursor += timedelta(days=1)
    return cursor


_FRIDAY_OVERRIDE = '{"5": {"start": "11:30", "end": "13:30"}}'


def _full_day_settings(**overrides: str) -> SettingsService:
    values = {
        SettingsKey.HQ_SCHEDULE_START.value: "08:00",
        SettingsKey.HQ_SCHEDULE_END.value: "16:00",
        SettingsKey.HQ_SCHEDULE_BREAK_START.value: "12:00",
        SettingsKey.HQ_SCHEDULE_BREAK_END.value: "13:00",
        SettingsKey.HQ_SCHEDULE_BREAK_OVERRIDES.value: _FRIDAY_OVERRIDE,
    }
    values.update(overrides)
    return _settings_service(**values)


def test_friday_break_override_splits_slots_and_halves_capacity() -> None:
    """Jumat 11:30-13:30: the crossed slots survive as half slots, not as
    two lost hours."""
    friday = _next_friday(date.today() + timedelta(days=7))
    service = HqScheduleService(_FakeHqScheduleRepository(), _full_day_settings())
    day = service.get_availability(
        date_from=friday, date_to=friday, detail=False
    ).days[0]

    assert [(s.start_time, s.end_time) for s in day.slots] == [
        ("08:00", "09:00"),
        ("09:00", "10:00"),
        ("10:00", "11:00"),
        ("11:00", "11:30"),
        ("11:30", "13:30"),
        ("13:30", "14:00"),
        ("14:00", "15:00"),
        ("15:00", "16:00"),
    ]
    by_start = {s.start_time: s for s in day.slots}
    assert by_start["11:30"].is_break is True
    assert by_start["11:30"].bookable is False
    assert by_start["11:30"].capacity == 0
    for start in ("11:00", "13:30"):
        half = by_start[start]
        assert half.is_break is False
        assert half.partial is True
        assert half.capacity == 1  # half of 2 per hour
        assert half.bookable is True
        assert half.bookable_count == 1
    assert by_start["10:00"].capacity == 2
    assert by_start["10:00"].partial is False


def test_break_override_leaves_other_weekdays_on_the_default_window() -> None:
    monday = _next_monday(date.today() + timedelta(days=7))
    service = HqScheduleService(_FakeHqScheduleRepository(), _full_day_settings())
    day = service.get_availability(
        date_from=monday, date_to=monday, detail=False
    ).days[0]

    by_start = {s.start_time: s for s in day.slots}
    assert by_start["12:00"].is_break is True
    assert by_start["12:00"].end_time == "13:00"
    assert by_start["11:00"].partial is False
    assert by_start["11:00"].capacity == 2
    assert by_start["13:00"].capacity == 2


def test_arrival_already_booked_inside_the_break_stays_visible() -> None:
    """A visit scheduled at 11:45 before the Jumat rule existed must not
    disappear from the board — it is bucketed into the break block."""
    friday = _next_friday(date.today() + timedelta(days=7))
    arrivals = [
        ArrivalRow(
            complaint_id="c1",
            complaint_number="TAB-2608-0001",
            owning_unit_id="UPPPD-TANAH-ABANG",
            hq_arrival_date=friday,
            hq_arrival_time="11:45",
            proposed_arrival_date=None,
            proposed_arrival_time=None,
            proposed_by=None,
            proposed_at=None,
            cases=(CaseRef(case_id="case-id-1", case_number="CASE-1"),),
        )
    ]
    service = HqScheduleService(
        _FakeHqScheduleRepository(arrivals=arrivals), _full_day_settings()
    )
    day = service.get_availability(
        date_from=friday, date_to=friday, detail=False
    ).days[0]

    break_slot = next(s for s in day.slots if s.is_break)
    assert break_slot.scheduled_count == 1
    assert [c.complaint_number for c in break_slot.scheduled_cases] == [
        "TAB-2608-0001"
    ]
    assert break_slot.available_count == 0
    assert break_slot.bookable is False


def test_partial_slot_capacity_rounds_down_but_never_to_zero() -> None:
    friday = _next_friday(date.today() + timedelta(days=7))
    service = HqScheduleService(
        _FakeHqScheduleRepository(),
        _full_day_settings(
            **{SettingsKey.HQ_SCHEDULE_CAPACITY_PER_SLOT.value: "3"}
        ),
    )
    by_start = {
        s.start_time: s
        for s in service.get_availability(
            date_from=friday, date_to=friday, detail=False
        ).days[0].slots
    }
    assert by_start["11:00"].capacity == 1  # floor(3 * 30 / 60)
    assert by_start["10:00"].capacity == 3


def test_break_override_null_means_no_break_that_weekday() -> None:
    friday = _next_friday(date.today() + timedelta(days=7))
    service = HqScheduleService(
        _FakeHqScheduleRepository(),
        _full_day_settings(
            **{SettingsKey.HQ_SCHEDULE_BREAK_OVERRIDES.value: '{"5": null}'}
        ),
    )
    day = service.get_availability(
        date_from=friday, date_to=friday, detail=False
    ).days[0]
    assert all(not s.is_break for s in day.slots)
    assert all(s.capacity == 2 for s in day.slots)


def test_malformed_break_overrides_fall_back_to_the_default_break() -> None:
    friday = _next_friday(date.today() + timedelta(days=7))
    service = HqScheduleService(
        _FakeHqScheduleRepository(),
        _full_day_settings(
            **{SettingsKey.HQ_SCHEDULE_BREAK_OVERRIDES.value: "{bukan json"}
        ),
    )
    by_start = {
        s.start_time: s
        for s in service.get_availability(
            date_from=friday, date_to=friday, detail=False
        ).days[0].slots
    }
    assert by_start["12:00"].is_break is True
    assert by_start["12:00"].end_time == "13:00"


_PUSAT_UNITS = (
    PusatUnit(code="PUSAT-CRO", name="CRO"),
    PusatUnit(code="PUSAT-SEKRETARIAT", name="Sekretariat"),
)


def _arrival(
    *,
    complaint_id: str,
    hq_arrival_date: date,
    hq_arrival_time: str,
    hq_destination_unit_id: str | None,
) -> ArrivalRow:
    return ArrivalRow(
        complaint_id=complaint_id,
        complaint_number=f"CMP-{complaint_id}",
        owning_unit_id="UPPPD-A",
        hq_arrival_date=hq_arrival_date,
        hq_arrival_time=hq_arrival_time,
        proposed_arrival_date=None,
        proposed_arrival_time=None,
        proposed_by=None,
        proposed_at=None,
        cases=(
            CaseRef(case_id=f"case-id-{complaint_id}", case_number=f"CASE-{complaint_id}"),
        ),
        hq_destination_unit_id=hq_destination_unit_id,
    )


def test_destination_unit_code_on_scheduled_cases() -> None:
    future_monday = _next_monday(date.today()) + timedelta(days=7)
    arrivals = [
        _arrival(
            complaint_id="c1",
            hq_arrival_date=future_monday,
            hq_arrival_time="08:15",
            hq_destination_unit_id="PUSAT-SEKRETARIAT",
        ),
        _arrival(
            complaint_id="c2",
            hq_arrival_date=future_monday,
            hq_arrival_time="08:30",
            hq_destination_unit_id=None,
        ),
    ]
    slot = HqScheduleService(
        _FakeHqScheduleRepository(arrivals=arrivals, pusat_units=list(_PUSAT_UNITS)),
        _settings_service(),
    ).get_availability(
        date_from=future_monday, date_to=future_monday, detail=True
    ).days[0].slots[0]
    by_id = {case.complaint_id: case for case in slot.scheduled_cases}
    assert by_id["c1"].destination_unit_code == "PUSAT-SEKRETARIAT"
    assert by_id["c2"].destination_unit_code is None


def test_per_unit_quota_does_not_close_other_units() -> None:
    """Two CRO bookings fill CRO; Sekretariat still has room so the slot stays bookable."""
    future_monday = _next_monday(date.today()) + timedelta(days=7)
    arrivals = [
        _arrival(
            complaint_id="c1",
            hq_arrival_date=future_monday,
            hq_arrival_time="08:10",
            hq_destination_unit_id="PUSAT-CRO",
        ),
        _arrival(
            complaint_id="c2",
            hq_arrival_date=future_monday,
            hq_arrival_time="08:20",
            hq_destination_unit_id="PUSAT-CRO",
        ),
    ]
    slot = HqScheduleService(
        _FakeHqScheduleRepository(arrivals=arrivals, pusat_units=list(_PUSAT_UNITS)),
        _settings_service(),
    ).get_availability(
        date_from=future_monday, date_to=future_monday, detail=True
    ).days[0].slots[0]
    assert slot.scheduled_count == 2
    assert slot.capacity == 4
    assert slot.available_count == 2
    assert slot.bookable is True
    by_code = {unit.unit_code: unit for unit in slot.units}
    assert by_code["PUSAT-CRO"].scheduled_count == 2
    assert by_code["PUSAT-CRO"].available_count == 0
    assert by_code["PUSAT-CRO"].bookable is False
    assert by_code["PUSAT-SEKRETARIAT"].scheduled_count == 0
    assert by_code["PUSAT-SEKRETARIAT"].available_count == 2
    assert by_code["PUSAT-SEKRETARIAT"].bookable is True


def test_unassigned_destination_does_not_consume_unit_quota() -> None:
    future_monday = _next_monday(date.today()) + timedelta(days=7)
    arrivals = [
        _arrival(
            complaint_id="legacy",
            hq_arrival_date=future_monday,
            hq_arrival_time="08:15",
            hq_destination_unit_id=None,
        )
    ]
    slot = HqScheduleService(
        _FakeHqScheduleRepository(arrivals=arrivals, pusat_units=list(_PUSAT_UNITS)),
        _settings_service(),
    ).get_availability(
        date_from=future_monday, date_to=future_monday, detail=True
    ).days[0].slots[0]
    assert slot.scheduled_count == 1
    assert all(unit.scheduled_count == 0 for unit in slot.units)
    assert slot.available_count == 4
    assert slot.bookable is True


def test_capacity_by_unit_overrides_default_for_named_units() -> None:
    future_monday = _next_monday(date.today()) + timedelta(days=7)
    slot = HqScheduleService(
        _FakeHqScheduleRepository(pusat_units=list(_PUSAT_UNITS)),
        _settings_service(
            **{
                SettingsKey.HQ_SCHEDULE_CAPACITY_BY_UNIT.value: (
                    '{"PUSAT-SEKRETARIAT": 1}'
                )
            }
        ),
    ).get_availability(
        date_from=future_monday, date_to=future_monday, detail=True
    ).days[0].slots[0]
    by_code = {unit.unit_code: unit for unit in slot.units}
    assert by_code["PUSAT-CRO"].capacity == 2
    assert by_code["PUSAT-SEKRETARIAT"].capacity == 1
    assert slot.capacity == 3


def test_malformed_capacity_by_unit_falls_back_to_capacity_per_slot() -> None:
    future_monday = _next_monday(date.today()) + timedelta(days=7)
    slot = HqScheduleService(
        _FakeHqScheduleRepository(pusat_units=list(_PUSAT_UNITS)),
        _settings_service(
            **{SettingsKey.HQ_SCHEDULE_CAPACITY_BY_UNIT.value: "{bukan json"}
        ),
    ).get_availability(
        date_from=future_monday, date_to=future_monday, detail=True
    ).days[0].slots[0]
    assert all(unit.capacity == 2 for unit in slot.units)
    assert slot.capacity == 4


def test_branch_view_hides_units_but_keeps_summed_remaining() -> None:
    future_monday = _next_monday(date.today()) + timedelta(days=7)
    arrivals = [
        _arrival(
            complaint_id="c1",
            hq_arrival_date=future_monday,
            hq_arrival_time="08:10",
            hq_destination_unit_id="PUSAT-CRO",
        ),
        _arrival(
            complaint_id="c2",
            hq_arrival_date=future_monday,
            hq_arrival_time="08:20",
            hq_destination_unit_id="PUSAT-CRO",
        ),
    ]
    slot = HqScheduleService(
        _FakeHqScheduleRepository(arrivals=arrivals, pusat_units=list(_PUSAT_UNITS)),
        _settings_service(),
    ).get_availability(
        date_from=future_monday, date_to=future_monday, detail=False
    ).days[0].slots[0]
    assert slot.units == []
    assert slot.available_count == 2
    assert slot.bookable is True
    assert slot.scheduled_cases[0].destination_unit_code == "PUSAT-CRO"


def test_customer_display_name_pusat_sees_all_cabang_only_own_unit() -> None:
    """Names are PII: detail (Pusat) sees every occupant; aggregate only own unit."""
    from app.integrations.customer import StubCustomerProvider

    future_monday = _next_monday(date.today()) + timedelta(days=7)
    arrivals = [
        ArrivalRow(
            complaint_id="c1",
            complaint_number="TAB-1",
            owning_unit_id="UPPPD-TANAH-ABANG",
            hq_arrival_date=future_monday,
            hq_arrival_time="08:00",
            proposed_arrival_date=None,
            proposed_arrival_time=None,
            proposed_by=None,
            proposed_at=None,
            customer_id="CUST-10001",
        ),
        ArrivalRow(
            complaint_id="c2",
            complaint_number="GAM-1",
            owning_unit_id="UPPPD-GAMBIR",
            hq_arrival_date=future_monday,
            hq_arrival_time="08:15",
            proposed_arrival_date=None,
            proposed_arrival_time=None,
            proposed_by=None,
            proposed_at=None,
            customer_id="CUST-10002",
        ),
    ]
    service = HqScheduleService(
        _FakeHqScheduleRepository(arrivals=arrivals),
        _settings_service(),
        customers=StubCustomerProvider(),
    )

    pusat = service.get_availability(
        date_from=future_monday, date_to=future_monday, detail=True
    )
    pusat_names = {
        c.complaint_number: c.customer_display_name
        for c in pusat.days[0].slots[0].scheduled_cases
    }
    assert pusat_names == {
        "TAB-1": "Synthetic Customer One",
        "GAM-1": "Synthetic Customer Two",
    }

    cabang = service.get_availability(
        date_from=future_monday,
        date_to=future_monday,
        detail=False,
        viewer_unit_id="UPPPD-TANAH-ABANG",
    )
    cabang_names = {
        c.complaint_number: c.customer_display_name
        for c in cabang.days[0].slots[0].scheduled_cases
    }
    assert cabang_names == {"TAB-1": "Synthetic Customer One", "GAM-1": None}


def test_customer_display_name_omitted_when_lookup_fails() -> None:
    from app.integrations.customer import StubCustomerProvider

    future_monday = _next_monday(date.today()) + timedelta(days=7)
    arrivals = [
        ArrivalRow(
            complaint_id="c1",
            complaint_number="TAB-1",
            owning_unit_id="UPPPD-A",
            hq_arrival_date=future_monday,
            hq_arrival_time="08:00",
            proposed_arrival_date=None,
            proposed_arrival_time=None,
            proposed_by=None,
            proposed_at=None,
            customer_id="CUST-MISSING",
        ),
    ]
    service = HqScheduleService(
        _FakeHqScheduleRepository(arrivals=arrivals),
        _settings_service(),
        customers=StubCustomerProvider(),
    )
    slot = service.get_availability(
        date_from=future_monday, date_to=future_monday, detail=True
    ).days[0].slots[0]
    assert slot.scheduled_cases[0].customer_display_name is None
