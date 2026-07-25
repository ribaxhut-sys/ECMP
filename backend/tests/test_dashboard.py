"""Dashboard composition unit tests (TASK-027 / API-319 overview)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.core.enums import TimelineEvent
from app.modules.dashboard.providers.complaint_provider import (
    ComplaintDashboardProvider,
)
from app.modules.dashboard.providers.notification_provider import (
    NotificationDashboardProvider,
)
from app.modules.dashboard.providers.queue_provider import QueueDashboardProvider
from app.modules.dashboard.providers.sla_provider import SlaDashboardProvider
from app.modules.dashboard.service import DashboardService
from app.modules.kpi.schemas import (
    ComplaintKpiCounts,
    KpiSummaryResponse,
    SlaStageKpiCounts,
)
from app.modules.settings.registry import SettingsKey


def _kpi(
    *,
    total: int = 0,
    open_count: int = 0,
    closed: int = 0,
    assignment: tuple[int, int] = (0, 0),
    appointment: tuple[int, int] = (0, 0),
    resolution: tuple[int, int] = (0, 0),
    escalation: tuple[int, int] = (0, 0),
    overall: tuple[int, int] = (0, 0),
) -> KpiSummaryResponse:
    return KpiSummaryResponse(
        complaints=ComplaintKpiCounts(total=total, open=open_count, closed=closed),
        assignment=SlaStageKpiCounts(completed=assignment[0], breached=assignment[1]),
        appointment=SlaStageKpiCounts(
            completed=appointment[0], breached=appointment[1]
        ),
        resolution=SlaStageKpiCounts(completed=resolution[0], breached=resolution[1]),
        escalation=SlaStageKpiCounts(completed=escalation[0], breached=escalation[1]),
        overall=SlaStageKpiCounts(completed=overall[0], breached=overall[1]),
    )


def _service(
    *,
    kpi: MagicMock | None = None,
    timeline: MagicMock | None = None,
    complaints: MagicMock | None = None,
    settings: MagicMock | None = None,
) -> DashboardService:
    return DashboardService(
        complaint_provider=MagicMock(spec=ComplaintDashboardProvider),
        queue_provider=MagicMock(spec=QueueDashboardProvider),
        sla_provider=MagicMock(spec=SlaDashboardProvider),
        notification_provider=MagicMock(spec=NotificationDashboardProvider),
        kpi_service=kpi or MagicMock(),
        timeline_service=timeline or MagicMock(),
        complaint_service=complaints or MagicMock(),
        settings_service=settings or MagicMock(),
    )


def test_dashboard_composes_kpi_header_and_sla() -> None:
    kpi = MagicMock()
    kpi.summary.return_value = _kpi(
        total=40,
        open_count=38,
        closed=2,
        assignment=(10, 3),
        appointment=(2, 1),
        resolution=(1, 0),
        escalation=(0, 2),
        overall=(1, 4),
    )
    timeline = MagicMock()
    timeline.list_recent.return_value = []
    settings = MagicMock()
    settings.get_int.return_value = 10

    result = _service(kpi=kpi, timeline=timeline, settings=settings).overview()

    assert result.header.total_complaints == 40
    assert result.header.open_complaints == 38
    assert result.header.closed_complaints == 2
    assert result.sla.assignment.completed == 10
    assert result.sla.assignment.breached == 3
    assert result.sla.overall.breached == 4
    assert result.recent_activity == []


def test_dashboard_reuses_kpi_service() -> None:
    kpi = MagicMock()
    kpi.summary.return_value = _kpi()
    timeline = MagicMock()
    timeline.list_recent.return_value = []
    settings = MagicMock()
    settings.get_int.return_value = 10

    _service(kpi=kpi, timeline=timeline, settings=settings).overview()
    kpi.summary.assert_called_once_with()


def test_dashboard_reuses_timeline_and_complaint_for_recent() -> None:
    now = datetime.now(UTC)
    cid = uuid.uuid4()
    row = SimpleNamespace(
        complaint_id=cid,
        event_type=TimelineEvent.CREATED,
        event_at=now,
        metadata_json=None,
        actor=SimpleNamespace(full_name="golive_admin"),
    )
    timeline = MagicMock()
    timeline.list_recent.return_value = [row]
    complaints = MagicMock()
    complaints.get.return_value = SimpleNamespace(complaint_number="CMP-ABC1234567")
    kpi = MagicMock()
    kpi.summary.return_value = _kpi()
    settings = MagicMock()
    settings.get_int.return_value = 10

    result = _service(
        kpi=kpi, timeline=timeline, complaints=complaints, settings=settings
    ).overview()

    assert len(result.recent_activity) == 1
    assert result.recent_activity[0].complaint_number == "CMP-ABC1234567"
    assert result.recent_activity[0].actor == "golive_admin"
    complaints.get.assert_called_once_with(cid)


def test_dashboard_empty_activity_and_zero_counts() -> None:
    kpi = MagicMock()
    kpi.summary.return_value = _kpi()
    timeline = MagicMock()
    timeline.list_recent.return_value = []
    settings = MagicMock()
    settings.get_int.return_value = 10

    result = _service(kpi=kpi, timeline=timeline, settings=settings).overview()
    assert result.header.total_complaints == 0
    assert result.recent_activity == []


def test_dashboard_system_actor_fallback() -> None:
    now = datetime.now(UTC)
    row = SimpleNamespace(
        complaint_id=uuid.uuid4(),
        event_type=TimelineEvent.CREATED,
        event_at=now,
        metadata_json=None,
        actor=None,
    )
    timeline = MagicMock()
    timeline.list_recent.return_value = [row]
    complaints = MagicMock()
    complaints.get.return_value = SimpleNamespace(complaint_number="CMP-1")
    kpi = MagicMock()
    kpi.summary.return_value = _kpi()
    settings = MagicMock()
    settings.get_int.return_value = 10

    result = _service(
        kpi=kpi, timeline=timeline, complaints=complaints, settings=settings
    ).overview()
    assert result.recent_activity[0].actor == "SYSTEM"


def test_dashboard_recent_limit_forwarded() -> None:
    kpi = MagicMock()
    kpi.summary.return_value = _kpi()
    timeline = MagicMock()
    timeline.list_recent.return_value = []
    settings = MagicMock()
    settings.get_int.return_value = 5

    _service(kpi=kpi, timeline=timeline, settings=settings).overview()
    settings.get_int.assert_called_once_with(
        SettingsKey.DASHBOARD_RECENT_LIMIT, default=10
    )
    timeline.list_recent.assert_called_once_with(limit=5)


def test_dashboard_recent_limit_from_settings() -> None:
    kpi = MagicMock()
    kpi.summary.return_value = _kpi()
    timeline = MagicMock()
    timeline.list_recent.return_value = []
    settings = MagicMock()
    settings.get_int.return_value = 0  # invalid → default 10

    _service(kpi=kpi, timeline=timeline, settings=settings).overview()
    timeline.list_recent.assert_called_once_with(limit=10)
