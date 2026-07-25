"""Wire DashboardService dependencies (CAPABILITY-013 + API-319 overview)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.dependencies.events import get_event_dispatcher
from app.modules.complaints.repository import ComplaintRepository
from app.modules.complaints.service import ComplaintService
from app.modules.dashboard.providers.complaint_provider import (
    ComplaintDashboardProvider,
)
from app.modules.dashboard.providers.notification_provider import (
    NotificationDashboardProvider,
)
from app.modules.dashboard.providers.queue_provider import QueueDashboardProvider
from app.modules.dashboard.providers.sla_provider import SlaDashboardProvider
from app.modules.dashboard.service import DashboardService
from app.modules.kpi.repository import KpiRepository
from app.modules.kpi.service import KpiService
from app.modules.settings.repository import SettingsRepository
from app.modules.settings.service import SettingsService
from app.modules.sla.repository import SlaRepository
from app.modules.sla.service import SlaService
from app.modules.timelines.repository import TimelineRepository
from app.modules.timelines.service import TimelineService


def build_dashboard_service(session: Session) -> DashboardService:
    return DashboardService(
        complaint_provider=ComplaintDashboardProvider(session),
        queue_provider=QueueDashboardProvider(session),
        sla_provider=SlaDashboardProvider(session),
        notification_provider=NotificationDashboardProvider(session),
        kpi_service=KpiService(KpiRepository(session)),
        timeline_service=TimelineService(TimelineRepository(session)),
        complaint_service=ComplaintService(
            ComplaintRepository(session),
            SlaService(SlaRepository(session)),
            event_dispatcher=get_event_dispatcher(),
        ),
        settings_service=SettingsService(SettingsRepository(session)),
    )
