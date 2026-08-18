"""Report HTTP routes (read-only aggregations)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_permissions
from app.core.schemas import DataResponse
from app.db.session import get_db_session
from app.modules.reports.repository import ReportRepository
from app.modules.reports.schemas import (
    BranchCount,
    CycleTimeData,
    ReportSummaryData,
    StatusCount,
)
from app.modules.reports.service import ReportService

router = APIRouter(prefix="/api/v1/reports", tags=["Reports"])


def get_report_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> ReportService:
    return ReportService(ReportRepository(session))


@router.get(
    "/summary",
    response_model=DataResponse[ReportSummaryData],
    status_code=status.HTTP_200_OK,
    summary="Complaint report summary",
)
def get_report_summary(
    service: Annotated[ReportService, Depends(get_report_service)],
    principal: Annotated[Principal, Depends(require_permissions("reports:read"))],
    branch_id: Annotated[uuid.UUID | None, Query(alias="branchId")] = None,
    date_from: Annotated[datetime | None, Query(alias="dateFrom")] = None,
    date_to: Annotated[datetime | None, Query(alias="dateTo")] = None,
) -> DataResponse[ReportSummaryData]:
    _ = principal
    return DataResponse(
        data=service.summary(
            branch_id=branch_id, date_from=date_from, date_to=date_to
        )
    )


@router.get(
    "/by-status",
    response_model=DataResponse[list[StatusCount]],
    status_code=status.HTTP_200_OK,
    summary="Complaint counts by status",
)
def get_report_by_status(
    service: Annotated[ReportService, Depends(get_report_service)],
    principal: Annotated[Principal, Depends(require_permissions("reports:read"))],
    branch_id: Annotated[uuid.UUID | None, Query(alias="branchId")] = None,
    date_from: Annotated[datetime | None, Query(alias="dateFrom")] = None,
    date_to: Annotated[datetime | None, Query(alias="dateTo")] = None,
) -> DataResponse[list[StatusCount]]:
    _ = principal
    return DataResponse(
        data=service.by_status(
            branch_id=branch_id, date_from=date_from, date_to=date_to
        )
    )


@router.get(
    "/by-branch",
    response_model=DataResponse[list[BranchCount]],
    status_code=status.HTTP_200_OK,
    summary="Complaint and case counts by branch",
)
def get_report_by_branch(
    service: Annotated[ReportService, Depends(get_report_service)],
    principal: Annotated[Principal, Depends(require_permissions("reports:read"))],
    branch_id: Annotated[uuid.UUID | None, Query(alias="branchId")] = None,
    date_from: Annotated[datetime | None, Query(alias="dateFrom")] = None,
    date_to: Annotated[datetime | None, Query(alias="dateTo")] = None,
) -> DataResponse[list[BranchCount]]:
    _ = principal
    return DataResponse(
        data=service.by_branch(
            branch_id=branch_id, date_from=date_from, date_to=date_to
        )
    )


@router.get(
    "/cycle-time",
    response_model=DataResponse[CycleTimeData],
    status_code=status.HTTP_200_OK,
    summary="How long closed cases took, over the closure window",
)
def get_report_cycle_time(
    service: Annotated[ReportService, Depends(get_report_service)],
    principal: Annotated[Principal, Depends(require_permissions("reports:read"))],
    branch_id: Annotated[uuid.UUID | None, Query(alias="branchId")] = None,
    date_from: Annotated[datetime | None, Query(alias="dateFrom")] = None,
    date_to: Annotated[datetime | None, Query(alias="dateTo")] = None,
) -> DataResponse[CycleTimeData]:
    _ = principal
    return DataResponse(
        data=service.cycle_time(
            branch_id=branch_id, date_from=date_from, date_to=date_to
        )
    )
