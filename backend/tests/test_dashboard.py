"""Dashboard composition unit tests (TASK-027 / API-319)."""



from __future__ import annotations



import uuid

from datetime import UTC, datetime

from types import SimpleNamespace

from unittest.mock import MagicMock



from app.core.enums import TimelineEvent

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





def _settings(*, recent_limit: int = 10) -> MagicMock:

    settings = MagicMock()

    settings.get_int.return_value = recent_limit

    return settings





def test_dashboard_composes_kpi_header_and_sla() -> None:

    kpi = MagicMock()

    kpi.summary.return_value = _kpi(

        total=10,

        open_count=7,

        closed=3,

        assignment=(4, 1),

        appointment=(2, 0),

        resolution=(1, 2),

        escalation=(0, 1),

        overall=(3, 2),

    )

    timeline = MagicMock()

    timeline.list_recent.return_value = []

    complaints = MagicMock()



    result = DashboardService(

        kpi_service=kpi,

        timeline_service=timeline,

        complaint_service=complaints,

        settings_service=_settings(),

    ).summary()



    assert result.header.total_complaints == 10

    assert result.header.open_complaints == 7

    assert result.header.closed_complaints == 3

    assert result.sla.assignment.completed == 4

    assert result.sla.assignment.breached == 1

    assert result.sla.overall.completed == 3

    assert result.sla.overall.breached == 2

    kpi.summary.assert_called_once_with()

    complaints.get.assert_not_called()





def test_dashboard_reuses_kpi_service() -> None:

    kpi = MagicMock()

    kpi.summary.return_value = _kpi()

    timeline = MagicMock()

    timeline.list_recent.return_value = []



    DashboardService(

        kpi_service=kpi,

        timeline_service=timeline,

        complaint_service=MagicMock(),

        settings_service=_settings(),

    ).summary()



    kpi.summary.assert_called_once()





def test_dashboard_reuses_timeline_and_complaint_for_recent() -> None:

    complaint_id = uuid.uuid4()

    t0 = datetime(2026, 7, 23, 12, 0, tzinfo=UTC)

    row = SimpleNamespace(

        complaint_id=complaint_id,

        event_type=TimelineEvent.CREATED,

        event_at=t0,

        metadata_json=None,

        actor=SimpleNamespace(full_name="golive_admin"),

    )

    kpi = MagicMock()

    kpi.summary.return_value = _kpi(total=1, open_count=1)

    timeline = MagicMock()

    timeline.list_recent.return_value = [row]

    complaints = MagicMock()

    complaints.get.return_value = SimpleNamespace(complaint_number="CMP-ABC123")



    result = DashboardService(

        kpi_service=kpi,

        timeline_service=timeline,

        complaint_service=complaints,

        settings_service=_settings(),

    ).summary()



    timeline.list_recent.assert_called_once_with(limit=10)

    complaints.get.assert_called_once_with(complaint_id)

    assert len(result.recent_activity) == 1

    item = result.recent_activity[0]

    assert item.event_type == TimelineEvent.CREATED.value or item.event_type == str(

        TimelineEvent.CREATED

    )

    assert item.complaint_number == "CMP-ABC123"

    assert item.timestamp == t0

    assert item.actor == "golive_admin"





def test_dashboard_empty_activity_and_zero_counts() -> None:

    kpi = MagicMock()

    kpi.summary.return_value = _kpi()

    timeline = MagicMock()

    timeline.list_recent.return_value = []



    result = DashboardService(

        kpi_service=kpi,

        timeline_service=timeline,

        complaint_service=MagicMock(),

        settings_service=_settings(),

    ).summary()



    assert result.header.total_complaints == 0

    assert result.recent_activity == []

    assert result.sla.appointment.completed == 0

    assert result.sla.appointment.breached == 0





def test_dashboard_system_actor_fallback() -> None:

    complaint_id = uuid.uuid4()

    row = SimpleNamespace(

        complaint_id=complaint_id,

        event_type="sla.assignment.breached",

        event_at=datetime.now(UTC),

        metadata_json={"actor": "SYSTEM"},

        actor=None,

    )

    kpi = MagicMock()

    kpi.summary.return_value = _kpi()

    timeline = MagicMock()

    timeline.list_recent.return_value = [row]

    complaints = MagicMock()

    complaints.get.return_value = SimpleNamespace(complaint_number="CMP-SYS")



    result = DashboardService(

        kpi_service=kpi,

        timeline_service=timeline,

        complaint_service=complaints,

        settings_service=_settings(),

    ).summary()



    assert result.recent_activity[0].actor == "SYSTEM"





def test_dashboard_recent_limit_forwarded() -> None:

    kpi = MagicMock()

    kpi.summary.return_value = _kpi()

    timeline = MagicMock()

    timeline.list_recent.return_value = []

    settings = _settings(recent_limit=10)



    DashboardService(

        kpi_service=kpi,

        timeline_service=timeline,

        complaint_service=MagicMock(),

        settings_service=settings,

    ).summary()



    settings.get_int.assert_called_once_with(

        SettingsKey.DASHBOARD_RECENT_LIMIT,

        default=10,

    )

    timeline.list_recent.assert_called_once_with(limit=10)





def test_dashboard_recent_limit_from_settings() -> None:

    kpi = MagicMock()

    kpi.summary.return_value = _kpi()

    timeline = MagicMock()

    timeline.list_recent.return_value = []



    DashboardService(

        kpi_service=kpi,

        timeline_service=timeline,

        complaint_service=MagicMock(),

        settings_service=_settings(recent_limit=5),

    ).summary()



    timeline.list_recent.assert_called_once_with(limit=5)


