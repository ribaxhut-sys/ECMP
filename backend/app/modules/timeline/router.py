"""CAPABILITY-010 Activity Timeline HTTP routes (API-382–385).

Note: legacy GET /api/v1/complaints/{id}/timeline (API-209) remains on
``timelines`` over ``complaint_timelines``. CAPABILITY-010 complaint view is
GET /api/v1/timeline?aggregateType=Complaint&aggregateId=… and
GET /api/v1/complaints/{id}/activity-timeline.
"""

from __future__ import annotations

import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_permissions
from app.core.schemas import DataResponse, ListResponse
from app.db.session import get_db_session
from app.modules.timeline.permissions import TIMELINE_CREATE, TIMELINE_READ
from app.modules.timeline.repository import TimelineRepository
from app.modules.timeline.schemas import (
    TimelineEntryCreateRequest,
    TimelineEntryResponse,
)
from app.modules.timeline.service import ActivityTimelineService

router = APIRouter(prefix="/api/v1/timeline", tags=["ActivityTimeline"])
complaint_activity_router = APIRouter(
    prefix="/api/v1/complaints", tags=["ActivityTimeline"]
)


def get_activity_timeline_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> ActivityTimelineService:
    return ActivityTimelineService(TimelineRepository(session))


@router.get(
    "",
    response_model=ListResponse[TimelineEntryResponse],
    status_code=status.HTTP_200_OK,
    summary="List timeline entries",
)
def list_timeline_entries(
    service: Annotated[
        ActivityTimelineService, Depends(get_activity_timeline_service)
    ],
    principal: Annotated[Principal, Depends(require_permissions(TIMELINE_READ))],
    aggregate_type: Annotated[
        Literal["Complaint", "Queue", "Notification"] | None,
        Query(alias="aggregateType"),
    ] = None,
    aggregate_id: Annotated[
        uuid.UUID | None, Query(alias="aggregateId")
    ] = None,
    event_type: Annotated[str | None, Query(alias="eventType", max_length=100)] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 50,
) -> ListResponse[TimelineEntryResponse]:
    """API-382 — paginated chronological timeline list."""
    _ = principal
    data, meta = service.list(
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        event_type=event_type,
        page=page,
        page_size=page_size,
    )
    return ListResponse(data=data, meta=meta)


@router.get(
    "/{entry_id}",
    response_model=DataResponse[TimelineEntryResponse],
    status_code=status.HTTP_200_OK,
    summary="Get timeline entry",
)
def get_timeline_entry(
    entry_id: uuid.UUID,
    service: Annotated[
        ActivityTimelineService, Depends(get_activity_timeline_service)
    ],
    principal: Annotated[Principal, Depends(require_permissions(TIMELINE_READ))],
) -> DataResponse[TimelineEntryResponse]:
    """API-383 — single immutable timeline entry."""
    _ = principal
    return DataResponse(data=service.get(entry_id))


@router.post(
    "",
    response_model=DataResponse[TimelineEntryResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create timeline entry (internal/testing)",
)
def create_timeline_entry(
    payload: TimelineEntryCreateRequest,
    service: Annotated[
        ActivityTimelineService, Depends(get_activity_timeline_service)
    ],
    principal: Annotated[Principal, Depends(require_permissions(TIMELINE_CREATE))],
) -> DataResponse[TimelineEntryResponse]:
    """API-384 — manual append; production flow uses EventDispatcher."""
    _ = principal
    return DataResponse(data=service.create(payload))


@complaint_activity_router.get(
    "/{id}/activity-timeline",
    response_model=ListResponse[TimelineEntryResponse],
    status_code=status.HTTP_200_OK,
    summary="List CAPABILITY-010 timeline for a complaint",
)
def list_complaint_activity_timeline(
    id: uuid.UUID,
    service: Annotated[
        ActivityTimelineService, Depends(get_activity_timeline_service)
    ],
    principal: Annotated[Principal, Depends(require_permissions(TIMELINE_READ))],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 100,
) -> ListResponse[TimelineEntryResponse]:
    """API-385 — complaint activity history from timeline_entries.

    Distinct from API-209 GET /complaints/{id}/timeline (complaint_timelines).
    """
    _ = principal
    data, meta = service.list_for_complaint(id, page=page, page_size=page_size)
    return ListResponse(data=data, meta=meta)
