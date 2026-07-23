"""Timeline HTTP routes (read-only)."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_permissions
from app.core.schemas import DataResponse
from app.db.session import get_db_session
from app.modules.timelines.repository import TimelineRepository
from app.modules.timelines.schemas import TimelineEntryResponse
from app.modules.timelines.service import TimelineService

router = APIRouter(prefix="/api/v1/complaints", tags=["Timeline"])


def get_timeline_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> TimelineService:
    return TimelineService(TimelineRepository(session))


@router.get(
    "/{id}/timeline",
    response_model=DataResponse[list[TimelineEntryResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get complaint timeline",
)
def get_complaint_timeline(
    id: uuid.UUID,
    service: Annotated[TimelineService, Depends(get_timeline_service)],
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
) -> DataResponse[list[TimelineEntryResponse]]:
    _ = principal
    return DataResponse(data=service.list_timeline(id))
