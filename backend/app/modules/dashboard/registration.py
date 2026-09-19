"""Wire DashboardService dependencies (CAPABILITY-013 + API-319 overview)."""

from __future__ import annotations

from sqlalchemy.orm import Session

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
from app.modules.dashboard.service import DashboardService
from app.modules.kpi.repository import KpiRepository
from app.modules.kpi.service import KpiService
from app.modules.settings.repository import SettingsRepository
from app.modules.settings.service import SettingsService


def build_dashboard_service(session: Session) -> DashboardService:
    return DashboardService(
        complaint_provider=ComplaintDashboardProvider(session),
        queue_provider=QueueDashboardProvider(session),
        sla_provider=SlaDashboardProvider(session),
        notification_provider=NotificationDashboardProvider(session),
        kpi_service=KpiService(KpiRepository(session)),
        activity_provider=CmBatch1ActivityDashboardProvider(session),
        settings_service=SettingsService(SettingsRepository(session)),
    )
