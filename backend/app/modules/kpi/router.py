"""KPI Foundation HTTP routes (API-318 / TASK-026)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_permissions
from app.core.schemas import DataResponse
from app.db.session import get_db_session
from app.modules.kpi.repository import KpiRepository
from app.modules.kpi.schemas import KpiSummaryResponse
from app.modules.kpi.service import KpiService

router = APIRouter(prefix="/api/v1/kpi", tags=["KPI"])

PriorityFilter = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def get_kpi_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> KpiService:
    return KpiService(KpiRepository(session))


@router.get(
    "/summary",
    response_model=DataResponse[KpiSummaryResponse],
    status_code=status.HTTP_200_OK,
    summary="KPI foundation summary",
)
def get_kpi_summary(
    service: Annotated[KpiService, Depends(get_kpi_service)],
    principal: Annotated[Principal, Depends(require_permissions("kpi:read"))],
    branch_id: Annotated[uuid.UUID | None, Query(alias="branchId")] = None,
    date_from: Annotated[datetime | None, Query(alias="dateFrom")] = None,
    date_to: Annotated[datetime | None, Query(alias="dateTo")] = None,
    category: Annotated[str | None, Query()] = None,
    priority: Annotated[PriorityFilter | None, Query()] = None,
) -> DataResponse[KpiSummaryResponse]:
    """API-318 — live complaint + SLA KPI aggregates (read-only)."""
    _ = principal
    return DataResponse(
        data=service.summary(
            branch_id=branch_id,
            date_from=date_from,
            date_to=date_to,
            category=category,
            priority=priority,
        )
    )
