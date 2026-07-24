"""Dashboard HTTP routes (API-319 / TASK-027)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_permissions
from app.core.schemas import DataResponse
from app.db.session import get_db_session
from app.dependencies.events import get_event_dispatcher
from app.modules.complaints.repository import ComplaintRepository
from app.modules.complaints.service import ComplaintService
from app.modules.dashboard.schemas import DashboardSummaryResponse
from app.modules.dashboard.service import DashboardService
from app.modules.kpi.repository import KpiRepository
from app.modules.kpi.service import KpiService
from app.modules.settings.repository import SettingsRepository
from app.modules.settings.service import SettingsService
from app.modules.sla.repository import SlaRepository
from app.modules.sla.service import SlaService
from app.modules.timelines.repository import TimelineRepository
from app.modules.timelines.service import TimelineService

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])


def get_dashboard_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> DashboardService:
    return DashboardService(
        kpi_service=KpiService(KpiRepository(session)),
        timeline_service=TimelineService(TimelineRepository(session)),
        complaint_service=ComplaintService(
            ComplaintRepository(session),
            SlaService(SlaRepository(session)),
            event_dispatcher=get_event_dispatcher(),
        ),
        settings_service=SettingsService(SettingsRepository(session)),
    )


@router.get(
    "/summary",
    response_model=DataResponse[DashboardSummaryResponse],
    status_code=status.HTTP_200_OK,
    summary="Dashboard summary",
)
def get_dashboard_summary(
    service: Annotated[DashboardService, Depends(get_dashboard_service)],
    principal: Annotated[
        Principal, Depends(require_permissions("dashboard:read"))
    ],
) -> DataResponse[DashboardSummaryResponse]:
    """API-319 — compose KPI + timeline + complaint data (orchestration only)."""
    _ = principal
    return DataResponse(data=service.summary())
