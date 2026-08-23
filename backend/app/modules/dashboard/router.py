"""CAPABILITY-013 Dashboard & KPI HTTP routes + API-319 overview."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_any_permission, require_permissions
from app.core.schemas import DataResponse
from app.db.session import get_db_session
from app.models import User
from app.modules.dashboard.domain.dto import DashboardFilters, TrendPeriod
from app.modules.dashboard.permissions import DASHBOARD_READ
from app.modules.dashboard.registration import build_dashboard_service
from app.modules.dashboard.schemas import (
    ComplaintSlaAlertsResponse,
    DashboardAggregateKpiResponse,
    DashboardComplaintSummaryResponse,
    DashboardKpiResponse,
    DashboardNotificationsResponse,
    DashboardOverviewResponse,
    DashboardQueueResponse,
    DashboardRecentActivityItem,
    DashboardSlaResponse,
    DashboardTrendsResponse,
)
from app.modules.dashboard.service import DashboardService

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])
_DEFAULT_ACTIVITY_LIMIT = 10
_DEFAULT_SLA_ALERT_LIMIT = 20


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


def _effective_branch_id(
    session: Session,
    principal: Principal,
    branch_id: uuid.UUID | None,
) -> uuid.UUID | None:
    """Lock branch-scoped principals (e.g. Manager, BC-8.4) to their own
    branch regardless of the requested branchId — same convention as
    recent-activity and users/router.py's Manager status-update gate
    (UM-BUG-007/008/009)."""
    own_branch_id = session.scalar(
        select(User.branch_id).where(User.id == principal.user_id)
    )
    return own_branch_id if own_branch_id is not None else branch_id


@router.get(
    "/summary",
    response_model=DataResponse[DashboardComplaintSummaryResponse],
    status_code=status.HTTP_200_OK,
    summary="Dashboard complaint summary",
)
def get_dashboard_summary(
    service: Annotated[DashboardService, Depends(get_dashboard_service)],
    principal: Annotated[Principal, Depends(require_permissions(DASHBOARD_READ))],
    session: Annotated[Session, Depends(get_db_session)],
    branch_id: Annotated[uuid.UUID | None, Query(alias="branchId")] = None,
    date_from: Annotated[datetime | None, Query(alias="dateFrom")] = None,
    date_to: Annotated[datetime | None, Query(alias="dateTo")] = None,
) -> DataResponse[DashboardComplaintSummaryResponse]:
    """API-389 — CAPABILITY-013 complaint KPI summary (read-only SQL aggregates)."""
    branch_id = _effective_branch_id(session, principal, branch_id)
    return DataResponse(
        data=service.summary(
            _filters(branch_id=branch_id, date_from=date_from, date_to=date_to)
        )
    )


@router.get(
    "/aggregate-kpis",
    response_model=DataResponse[DashboardAggregateKpiResponse],
    status_code=status.HTTP_200_OK,
    summary="Aggregate (CM Batch-1) complaint KPI counts (DEC-020)",
)
def get_dashboard_aggregate_kpis(
    service: Annotated[DashboardService, Depends(get_dashboard_service)],
    principal: Annotated[
        Principal,
        Depends(require_any_permission(DASHBOARD_READ, "reports:read")),
    ],
    session: Annotated[Session, Depends(get_db_session)],
    branch_id: Annotated[uuid.UUID | None, Query(alias="branchId")] = None,
    date_from: Annotated[datetime | None, Query(alias="dateFrom")] = None,
    date_to: Annotated[datetime | None, Query(alias="dateTo")] = None,
) -> DataResponse[DashboardAggregateKpiResponse]:
    """Branch-scoped Aggregate KPI for dashboard cards and reports (one SoT).

    ``reports:read`` may also call this so ``/reports`` shows the same
    Batch-1 numbers as the dashboard without reading foundation API-210.
    Head Office (no own branch) may pick any branch or leave unset for all
    branches. A branch-scoped principal (e.g. Manager, BC-8.4) is always locked
    to their own branch — same ``_effective_branch_id`` convention as
    recent-activity (UM-BUG-009).
    """
    branch_id = _effective_branch_id(session, principal, branch_id)
    return DataResponse(
        data=service.aggregate_kpis(
            branch_id=branch_id, date_from=date_from, date_to=date_to
        )
    )


@router.get(
    "/sla-alerts",
    response_model=DataResponse[ComplaintSlaAlertsResponse],
    status_code=status.HTTP_200_OK,
    summary="Complaints approaching or past the resolution SLA (DEC-031)",
)
def get_dashboard_sla_alerts(
    service: Annotated[DashboardService, Depends(get_dashboard_service)],
    principal: Annotated[Principal, Depends(require_permissions(DASHBOARD_READ))],
    session: Annotated[Session, Depends(get_db_session)],
    branch_id: Annotated[uuid.UUID | None, Query(alias="branchId")] = None,
    limit: Annotated[int, Query(ge=1, le=50)] = _DEFAULT_SLA_ALERT_LIMIT,
) -> DataResponse[ComplaintSlaAlertsResponse]:
    """In-app substitute for a proactive breach notification (DEC-031 §3).

    Computed on request — there is no scheduler and no transport behind it, so
    it reaches an officer when they open the app rather than at the instant a
    threshold is crossed. Branch scoping follows the same
    ``_effective_branch_id`` convention as recent-activity: Head Office may
    pick any branch, a branch-scoped principal is locked to their own.
    """
    branch_id = _effective_branch_id(session, principal, branch_id)
    return DataResponse(data=service.sla_alerts(branch_id=branch_id, limit=limit))


@router.get(
    "/recent-activity",
    response_model=DataResponse[list[DashboardRecentActivityItem]],
    status_code=status.HTTP_200_OK,
    summary="Recent activity feed, optionally filtered by branch (UM-BUG-009)",
)
def get_dashboard_recent_activity(
    service: Annotated[DashboardService, Depends(get_dashboard_service)],
    principal: Annotated[Principal, Depends(require_permissions(DASHBOARD_READ))],
    session: Annotated[Session, Depends(get_db_session)],
    branch_id: Annotated[uuid.UUID | None, Query(alias="branchId")] = None,
    limit: Annotated[int, Query(ge=1, le=50)] = _DEFAULT_ACTIVITY_LIMIT,
) -> DataResponse[list[DashboardRecentActivityItem]]:
    """Head Office (no own branch) may pick any branch or leave it unset for
    all branches. A branch-scoped principal is always locked to their own
    branch regardless of the requested branchId — same convention as
    users/router.py's Manager status-update gate (UM-BUG-007/008)."""
    branch_id = _effective_branch_id(session, principal, branch_id)
    return DataResponse(
        data=service.recent_activity(limit=limit, branch_id=branch_id)
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
    session: Annotated[Session, Depends(get_db_session)],
    branch_id: Annotated[uuid.UUID | None, Query(alias="branchId")] = None,
    date_from: Annotated[datetime | None, Query(alias="dateFrom")] = None,
    date_to: Annotated[datetime | None, Query(alias="dateTo")] = None,
) -> DataResponse[DashboardQueueResponse]:
    """API-390 — CAPABILITY-013 queue ticket aggregates."""
    branch_id = _effective_branch_id(session, principal, branch_id)
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
    session: Annotated[Session, Depends(get_db_session)],
    branch_id: Annotated[uuid.UUID | None, Query(alias="branchId")] = None,
    date_from: Annotated[datetime | None, Query(alias="dateFrom")] = None,
    date_to: Annotated[datetime | None, Query(alias="dateTo")] = None,
) -> DataResponse[DashboardSlaResponse]:
    """API-391 — CAPABILITY-013 SLA compliance aggregates."""
    branch_id = _effective_branch_id(session, principal, branch_id)
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
    session: Annotated[Session, Depends(get_db_session)],
    period: Annotated[TrendPeriod, Query()] = TrendPeriod.SEVEN_D,
    branch_id: Annotated[uuid.UUID | None, Query(alias="branchId")] = None,
    date_from: Annotated[datetime | None, Query(alias="dateFrom")] = None,
    date_to: Annotated[datetime | None, Query(alias="dateTo")] = None,
) -> DataResponse[DashboardTrendsResponse]:
    """API-393 — CAPABILITY-013 daily complaint counts (today / 7d / 30d)."""
    branch_id = _effective_branch_id(session, principal, branch_id)
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
    session: Annotated[Session, Depends(get_db_session)],
    branch_id: Annotated[uuid.UUID | None, Query(alias="branchId")] = None,
    date_from: Annotated[datetime | None, Query(alias="dateFrom")] = None,
    date_to: Annotated[datetime | None, Query(alias="dateTo")] = None,
) -> DataResponse[DashboardKpiResponse]:
    """API-394 — CAPABILITY-013 numeric KPI rates (no charts)."""
    branch_id = _effective_branch_id(session, principal, branch_id)
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
