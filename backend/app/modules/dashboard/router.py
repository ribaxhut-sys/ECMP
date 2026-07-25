"""CAPABILITY-013 Dashboard & KPI HTTP routes + API-319 overview."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_permissions
from app.core.schemas import DataResponse
from app.db.session import get_db_session
from app.modules.dashboard.domain.dto import DashboardFilters, TrendPeriod
from app.modules.dashboard.permissions import DASHBOARD_READ
from app.modules.dashboard.registration import build_dashboard_service
from app.modules.dashboard.schemas import (
    DashboardComplaintSummaryResponse,
    DashboardKpiResponse,
    DashboardNotificationsResponse,
    DashboardOverviewResponse,
    DashboardQueueResponse,
    DashboardSlaResponse,
    DashboardTrendsResponse,
)
from app.modules.dashboard.service import DashboardService

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])


def get_dashboard_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> DashboardService:
    return build_dashboard_service(session)


def _filters(
    *,
    branch_id: uuid.UUID | None,
    date_from: datetime | None,
    date_to: datetime | None,
) -> DashboardFilters:
    return DashboardFilters(
        branch_id=branch_id,
        date_from=date_from,
        date_to=date_to,
    )


@router.get(
    "/summary",
    response_model=DataResponse[DashboardComplaintSummaryResponse],
    status_code=status.HTTP_200_OK,
    summary="Dashboard complaint summary",
)
def get_dashboard_summary(
    service: Annotated[DashboardService, Depends(get_dashboard_service)],
    principal: Annotated[Principal, Depends(require_permissions(DASHBOARD_READ))],
    branch_id: Annotated[uuid.UUID | None, Query(alias="branchId")] = None,
    date_from: Annotated[datetime | None, Query(alias="dateFrom")] = None,
    date_to: Annotated[datetime | None, Query(alias="dateTo")] = None,
) -> DataResponse[DashboardComplaintSummaryResponse]:
    """API-389 — CAPABILITY-013 complaint KPI summary (read-only SQL aggregates)."""
    _ = principal
    return DataResponse(
        data=service.summary(
            _filters(branch_id=branch_id, date_from=date_from, date_to=date_to)
        )
    )


@router.get(
    "/queue",
    response_model=DataResponse[DashboardQueueResponse],
    status_code=status.HTTP_200_OK,
    summary="Dashboard queue summary",
)
def get_dashboard_queue(
    service: Annotated[DashboardService, Depends(get_dashboard_service)],
    principal: Annotated[Principal, Depends(require_permissions(DASHBOARD_READ))],
    branch_id: Annotated[uuid.UUID | None, Query(alias="branchId")] = None,
    date_from: Annotated[datetime | None, Query(alias="dateFrom")] = None,
    date_to: Annotated[datetime | None, Query(alias="dateTo")] = None,
) -> DataResponse[DashboardQueueResponse]:
    """API-390 — CAPABILITY-013 queue ticket aggregates."""
    _ = principal
    return DataResponse(
        data=service.queue(
            _filters(branch_id=branch_id, date_from=date_from, date_to=date_to)
        )
    )


@router.get(
    "/sla",
    response_model=DataResponse[DashboardSlaResponse],
    status_code=status.HTTP_200_OK,
    summary="Dashboard SLA summary",
)
def get_dashboard_sla(
    service: Annotated[DashboardService, Depends(get_dashboard_service)],
    principal: Annotated[Principal, Depends(require_permissions(DASHBOARD_READ))],
    branch_id: Annotated[uuid.UUID | None, Query(alias="branchId")] = None,
    date_from: Annotated[datetime | None, Query(alias="dateFrom")] = None,
    date_to: Annotated[datetime | None, Query(alias="dateTo")] = None,
) -> DataResponse[DashboardSlaResponse]:
    """API-391 — CAPABILITY-013 SLA compliance aggregates."""
    _ = principal
    return DataResponse(
        data=service.sla(
            _filters(branch_id=branch_id, date_from=date_from, date_to=date_to)
        )
    )


@router.get(
    "/notifications",
    response_model=DataResponse[DashboardNotificationsResponse],
    status_code=status.HTTP_200_OK,
    summary="Dashboard notification summary",
)
def get_dashboard_notifications(
    service: Annotated[DashboardService, Depends(get_dashboard_service)],
    principal: Annotated[Principal, Depends(require_permissions(DASHBOARD_READ))],
    date_from: Annotated[datetime | None, Query(alias="dateFrom")] = None,
    date_to: Annotated[datetime | None, Query(alias="dateTo")] = None,
) -> DataResponse[DashboardNotificationsResponse]:
    """API-392 — CAPABILITY-013 notification queue counts."""
    _ = principal
    return DataResponse(
        data=service.notifications(
            _filters(branch_id=None, date_from=date_from, date_to=date_to)
        )
    )


@router.get(
    "/trends",
    response_model=DataResponse[DashboardTrendsResponse],
    status_code=status.HTTP_200_OK,
    summary="Dashboard complaint trends",
)
def get_dashboard_trends(
    service: Annotated[DashboardService, Depends(get_dashboard_service)],
    principal: Annotated[Principal, Depends(require_permissions(DASHBOARD_READ))],
    period: Annotated[TrendPeriod, Query()] = TrendPeriod.SEVEN_D,
    branch_id: Annotated[uuid.UUID | None, Query(alias="branchId")] = None,
    date_from: Annotated[datetime | None, Query(alias="dateFrom")] = None,
    date_to: Annotated[datetime | None, Query(alias="dateTo")] = None,
) -> DataResponse[DashboardTrendsResponse]:
    """API-393 — CAPABILITY-013 daily complaint counts (today / 7d / 30d)."""
    _ = principal
    return DataResponse(
        data=service.trends(
            period=period,
            filters=_filters(
                branch_id=branch_id, date_from=date_from, date_to=date_to
            ),
        )
    )


@router.get(
    "/kpi",
    response_model=DataResponse[DashboardKpiResponse],
    status_code=status.HTTP_200_OK,
    summary="Dashboard KPI rates",
)
def get_dashboard_kpi(
    service: Annotated[DashboardService, Depends(get_dashboard_service)],
    principal: Annotated[Principal, Depends(require_permissions(DASHBOARD_READ))],
    branch_id: Annotated[uuid.UUID | None, Query(alias="branchId")] = None,
    date_from: Annotated[datetime | None, Query(alias="dateFrom")] = None,
    date_to: Annotated[datetime | None, Query(alias="dateTo")] = None,
) -> DataResponse[DashboardKpiResponse]:
    """API-394 — CAPABILITY-013 numeric KPI rates (no charts)."""
    _ = principal
    return DataResponse(
        data=service.kpi(
            _filters(branch_id=branch_id, date_from=date_from, date_to=date_to)
        )
    )


@router.get(
    "/overview",
    response_model=DataResponse[DashboardOverviewResponse],
    status_code=status.HTTP_200_OK,
    summary="Dashboard overview composition",
)
def get_dashboard_overview(
    service: Annotated[DashboardService, Depends(get_dashboard_service)],
    principal: Annotated[Principal, Depends(require_permissions(DASHBOARD_READ))],
) -> DataResponse[DashboardOverviewResponse]:
    """API-319 — compose KPI + timeline + complaint (TASK-027 / DEC-016)."""
    _ = principal
    return DataResponse(data=service.overview())
