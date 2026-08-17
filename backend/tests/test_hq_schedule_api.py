"""HQ schedule HTTP routes — dependency-override smoke tests (no DB upgrade).

Follows the fake-repository pattern from test_hq_schedule_service.py; the
FastAPI dependency `get_hq_schedule_service` is overridden directly so these
tests never touch a real database or require an alembic upgrade.
"""

from __future__ import annotations

import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Iterator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.authorization.authentication import get_current_principal
from app.core.authorization.principal import Principal
from app.db.base import Base
from app.db.session import get_db_session
from app.main import create_app
from app.models import Branch, User
from app.modules.cm_batch1.models import CmBatch1ComplaintORM, CmBatch1OutboxORM
from app.modules.cm_case.infrastructure.orm import CmCaseORM
from app.modules.hq_schedule.router import get_hq_schedule_service
from app.modules.hq_schedule.service import HqScheduleService
from app.modules.settings.registry import SettingsKey
from app.modules.settings.service import SettingsService

# require_hq_intake_action may fall back to OrgUnitResolver.resolve_principal_membership
# (a User lookup) for AGENT-family roles without a declared org_unit_id — give it an
# empty in-memory schema instead of touching the real (unmigrated-here) test database.
_ORG_RESOLVER_TABLES = [
    User.__table__,
    Branch.__table__,
    CmBatch1ComplaintORM.__table__,
    CmBatch1OutboxORM.__table__,
    CmCaseORM.__table__,
]


@dataclass
class _FakeSettingRow:
    value: str


class _FakeSettingsRepository:
    def get_by_key(self, key: str) -> _FakeSettingRow | None:
        values = {
            SettingsKey.HQ_SCHEDULE_START.value: "08:00",
            SettingsKey.HQ_SCHEDULE_END.value: "10:00",
            SettingsKey.HQ_SCHEDULE_SLOT_MINUTES.value: "60",
            SettingsKey.HQ_SCHEDULE_CAPACITY_PER_SLOT.value: "2",
            SettingsKey.HQ_SCHEDULE_WORKDAYS.value: "1,2,3,4,5",
        }
        if key not in values:
            return None
        return _FakeSettingRow(value=values[key])


class _FakeHoliday:
    def __init__(self, holiday_date: date, label: str) -> None:
        self.holiday_date = holiday_date
        self.label = label
        self.created_by = "hq-1"
        self.created_at = datetime(2026, 8, 17, tzinfo=UTC)


class _FakeHqScheduleRepository:
    def __init__(self) -> None:
        self._holidays: list[_FakeHoliday] = []

    def list_holidays(self, *, date_from: date, date_to: date) -> list:
        return [h for h in self._holidays if date_from <= h.holiday_date <= date_to]

    def list_arrivals_in_range(self, *, date_from: date, date_to: date) -> list:
        return []

    def get_holiday(self, holiday_date: date) -> _FakeHoliday | None:
        return next((h for h in self._holidays if h.holiday_date == holiday_date), None)

    def create_holiday(
        self, *, holiday_date: date, label: str, created_by: str | None
    ) -> _FakeHoliday:
        row = _FakeHoliday(holiday_date, label)
        row.created_by = created_by or "hq-1"
        self._holidays.append(row)
        return row

    def delete_holiday(self, holiday_date: date) -> bool:
        before = len(self._holidays)
        self._holidays = [h for h in self._holidays if h.holiday_date != holiday_date]
        return len(self._holidays) < before

    def commit(self) -> None:
        return None


def _service() -> HqScheduleService:
    return HqScheduleService(
        _FakeHqScheduleRepository(), SettingsService(_FakeSettingsRepository())
    )


def _principal(
    *, roles: tuple[str, ...], permissions: frozenset[str], org_unit_id: str | None = None
) -> Principal:
    return Principal(
        user_id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
        roles=roles,
        permissions=permissions,
        org_unit_id=org_unit_id,
    )


@contextmanager
def _client_for(principal: Principal) -> Iterator[TestClient]:
    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine, tables=_ORG_RESOLVER_TABLES)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session: Session = factory()

    app = create_app()
    service = _service()
    app.dependency_overrides[get_hq_schedule_service] = lambda: service
    app.dependency_overrides[get_current_principal] = lambda: principal
    app.dependency_overrides[get_db_session] = lambda: session
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        session.close()
        engine.dispose()


def test_availability_200_with_complaints_read_no_hq_role() -> None:
    principal = _principal(
        roles=("AGENT",), permissions=frozenset({"complaints:read"})
    )
    with _client_for(principal) as client:
        resp = client.get("/api/v1/hq-schedule/availability")
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["days"]


def test_availability_detail_403_without_hq_gate() -> None:
    principal = _principal(
        roles=("AGENT",), permissions=frozenset({"complaints:read"})
    )
    with _client_for(principal) as client:
        resp = client.get("/api/v1/hq-schedule/availability/detail")
    assert resp.status_code == 403, resp.text


def test_availability_detail_200_for_hq_eligible_actor() -> None:
    principal = _principal(
        roles=("HO_SCHEDULER",), permissions=frozenset({"escalations:review"})
    )
    with _client_for(principal) as client:
        resp = client.get("/api/v1/hq-schedule/availability/detail")
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["days"]


def test_availability_detail_200_for_pusat_unit_agent() -> None:
    principal = _principal(
        roles=("AGENT",),
        permissions=frozenset({"complaints:read"}),
        org_unit_id="PUSAT",
    )
    with _client_for(principal) as client:
        resp = client.get("/api/v1/hq-schedule/availability/detail")
    assert resp.status_code == 200, resp.text


def test_get_hq_schedule_service_wires_dependencies() -> None:
    from unittest.mock import MagicMock

    svc = get_hq_schedule_service(MagicMock())
    assert isinstance(svc, HqScheduleService)


def test_holiday_routes_require_settings_permissions() -> None:
    reader = _principal(
        roles=("ADMIN",), permissions=frozenset({"settings:read"})
    )
    writer = _principal(
        roles=("ADMIN",), permissions=frozenset({"settings:read", "settings:update"})
    )
    day = date.today().isoformat()
    with _client_for(reader) as client:
        listed = client.get("/api/v1/hq-schedule/holidays")
        assert listed.status_code == 200, listed.text
        denied = client.post(
            "/api/v1/hq-schedule/holidays",
            json={"holidayDate": day, "label": "Cuti"},
        )
        assert denied.status_code == 403
    with _client_for(writer) as client:
        created = client.post(
            "/api/v1/hq-schedule/holidays",
            json={"holidayDate": day, "label": "Cuti"},
        )
        assert created.status_code == 200, created.text
        assert created.json()["data"]["label"] == "Cuti"
        deleted = client.delete(f"/api/v1/hq-schedule/holidays/{day}")
        assert deleted.status_code == 204
