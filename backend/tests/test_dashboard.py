"""Dashboard composition unit tests (TASK-027 / API-319 overview, UM-BUG-008)."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import MagicMock

from app.modules.dashboard.providers.cm_batch1_activity_provider import (
    CmBatch1ActivityDashboardProvider,
)
from app.modules.dashboard.providers.complaint_provider import (
    ComplaintDashboardProvider,
)
from app.modules.dashboard.providers.notification_provider import (
    NotificationDashboardProvider,
)
from app.modules.dashboard.providers.queue_provider import QueueDashboardProvider
from app.modules.dashboard.providers.sla_provider import SlaDashboardProvider
from app.modules.dashboard.schemas import DashboardRecentActivityItem
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
    activity: MagicMock | None = None,
    settings: MagicMock | None = None,
) -> DashboardService:
    return DashboardService(
        complaint_provider=MagicMock(spec=ComplaintDashboardProvider),
        queue_provider=MagicMock(spec=QueueDashboardProvider),
        sla_provider=MagicMock(spec=SlaDashboardProvider),
        notification_provider=MagicMock(spec=NotificationDashboardProvider),
        kpi_service=kpi or MagicMock(),
        activity_provider=activity
        or MagicMock(spec=CmBatch1ActivityDashboardProvider),
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
    activity = MagicMock()
    activity.list_recent.return_value = []
    settings = MagicMock()
    settings.get_int.return_value = 10

    result = _service(kpi=kpi, activity=activity, settings=settings).overview()

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
    activity = MagicMock()
    activity.list_recent.return_value = []
    settings = MagicMock()
    settings.get_int.return_value = 10

    _service(kpi=kpi, activity=activity, settings=settings).overview()
    kpi.summary.assert_called_once_with()


def test_dashboard_reuses_activity_provider_for_recent() -> None:
    """UM-BUG-008 — recent activity is sourced from CM Batch 1 (not legacy)."""
    now = datetime.now(UTC)
    activity = MagicMock()
    activity.list_recent.return_value = [
        DashboardRecentActivityItem(
            eventType="complaint.created",
            complaintNumber="CM-00000001",
            timestamp=now,
            actor="golive_admin",
        )
    ]
    kpi = MagicMock()
    kpi.summary.return_value = _kpi()
    settings = MagicMock()
    settings.get_int.return_value = 10

    result = _service(kpi=kpi, activity=activity, settings=settings).overview()

    assert len(result.recent_activity) == 1
    assert result.recent_activity[0].complaint_number == "CM-00000001"
    assert result.recent_activity[0].actor == "golive_admin"


def test_dashboard_empty_activity_and_zero_counts() -> None:
    kpi = MagicMock()
    kpi.summary.return_value = _kpi()
    activity = MagicMock()
    activity.list_recent.return_value = []
    settings = MagicMock()
    settings.get_int.return_value = 10

    result = _service(kpi=kpi, activity=activity, settings=settings).overview()
    assert result.header.total_complaints == 0
    assert result.recent_activity == []


def test_dashboard_recent_limit_forwarded() -> None:
    kpi = MagicMock()
    kpi.summary.return_value = _kpi()
    activity = MagicMock()
    activity.list_recent.return_value = []
    settings = MagicMock()
    settings.get_int.return_value = 5

    _service(kpi=kpi, activity=activity, settings=settings).overview()
    settings.get_int.assert_called_once_with(
        SettingsKey.DASHBOARD_RECENT_LIMIT, default=10
    )
    activity.list_recent.assert_called_once_with(limit=5)


def test_dashboard_recent_limit_from_settings() -> None:
    kpi = MagicMock()
    kpi.summary.return_value = _kpi()
    activity = MagicMock()
    activity.list_recent.return_value = []
    settings = MagicMock()
    settings.get_int.return_value = 0  # invalid → default 10

    _service(kpi=kpi, activity=activity, settings=settings).overview()
    activity.list_recent.assert_called_once_with(limit=10)
