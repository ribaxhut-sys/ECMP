"""HQ arrival schedule HTTP routes — availability (Wajib Pajak sidebar, Pusat)."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_permissions
from app.core.authorization.gates import require_hq_intake_action
from app.core.config import Settings, get_settings
from app.core.schemas import DataResponse
from app.db.session import get_db_session
from app.integrations.customer import build_customer_provider
from app.modules.hq_schedule.repository import HqScheduleRepository
from app.modules.hq_schedule.schemas import (
    AvailabilityResponse,
    HolidayCreateRequest,
    HolidayResponse,
)
from app.modules.hq_schedule.service import HqScheduleService
from app.modules.settings.repository import SettingsRepository
from app.modules.settings.service import SettingsService

router = APIRouter(prefix="/api/v1/hq-schedule", tags=["HQ Schedule"])

_DEFAULT_RANGE_DAYS = 6


def get_hq_schedule_service(
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> HqScheduleService:
    return HqScheduleService(
        HqScheduleRepository(session),
        SettingsService(SettingsRepository(session)),
        customers=build_customer_provider(
            settings.customer_provider,
            enterprise_base_url=settings.customer_provider_enterprise_base_url,
            session=session,
        ),
    )


def _default_range(
    date_from: date | None, date_to: date | None
) -> tuple[date, date]:
    start = date_from or date.today()
    end = date_to or (start + timedelta(days=_DEFAULT_RANGE_DAYS))
    return start, end


@router.get(
    "/availability",
    response_model=DataResponse[AvailabilityResponse],
    status_code=status.HTTP_200_OK,
    summary="Branch-facing aggregate HQ arrival slot availability",
)
def get_availability(
    service: Annotated[HqScheduleService, Depends(get_hq_schedule_service)],
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
    date_from: Annotated[date | None, Query(alias="from")] = None,
    date_to: Annotated[date | None, Query(alias="to")] = None,
) -> DataResponse[AvailabilityResponse]:
    """Cabang view — used inline in the escalation slot picker.

    Case numbers for every branch are visible (so the board reads correctly);
    only the frontend gates the link to a complaint to the owning branch or
    Pusat (see HqScheduleView.canOpenCase). Taxpayer names are PII — this
    aggregate returns ``customerDisplayName`` only for the caller's own unit.
    """
    start, end = _default_range(date_from, date_to)
    return DataResponse(
        data=service.get_availability(
            date_from=start,
            date_to=end,
            detail=False,
            viewer_unit_id=principal.org_unit_id,
        )
    )


@router.get(
    "/availability/detail",
    response_model=DataResponse[AvailabilityResponse],
    status_code=status.HTTP_200_OK,
    summary="Pusat detail HQ arrival slot availability (with pending proposals)",
)
def get_availability_detail(
    service: Annotated[HqScheduleService, Depends(get_hq_schedule_service)],
    principal: Annotated[Principal, Depends(require_hq_intake_action)],
    date_from: Annotated[date | None, Query(alias="from")] = None,
    date_to: Annotated[date | None, Query(alias="to")] = None,
) -> DataResponse[AvailabilityResponse]:
    """Pusat-only — same grid, plus per-slot branch proposals awaiting decision."""
    _ = principal
    start, end = _default_range(date_from, date_to)
    return DataResponse(
        data=service.get_availability(date_from=start, date_to=end, detail=True)
    )


@router.get(
    "/holidays",
    response_model=DataResponse[list[HolidayResponse]],
    status_code=status.HTTP_200_OK,
    summary="List HQ schedule holidays in range",
)
def list_holidays(
    service: Annotated[HqScheduleService, Depends(get_hq_schedule_service)],
    principal: Annotated[Principal, Depends(require_permissions("settings:read"))],
    date_from: Annotated[date | None, Query(alias="from")] = None,
    date_to: Annotated[date | None, Query(alias="to")] = None,
) -> DataResponse[list[HolidayResponse]]:
    _ = principal
    start, end = _default_range(date_from, date_to)
    return DataResponse(data=service.list_holidays(date_from=start, date_to=end))


@router.post(
    "/holidays",
    response_model=DataResponse[HolidayResponse],
    status_code=status.HTTP_200_OK,
    summary="Create or relabel an HQ schedule holiday",
)
def create_holiday(
    payload: HolidayCreateRequest,
    service: Annotated[HqScheduleService, Depends(get_hq_schedule_service)],
    principal: Annotated[Principal, Depends(require_permissions("settings:update"))],
) -> DataResponse[HolidayResponse]:
    return DataResponse(
        data=service.create_holiday(payload, actor_id=str(principal.user_id))
    )


@router.delete(
    "/holidays/{holiday_date}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove an HQ schedule holiday",
)
def delete_holiday(
    holiday_date: date,
    service: Annotated[HqScheduleService, Depends(get_hq_schedule_service)],
    principal: Annotated[Principal, Depends(require_permissions("settings:update"))],
) -> None:
    _ = principal
    service.delete_holiday(holiday_date)
