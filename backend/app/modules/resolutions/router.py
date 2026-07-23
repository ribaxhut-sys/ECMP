"""Resolution HTTP routes (TASK-010)."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_permissions
from app.core.errors import NotFoundError
from app.core.schemas import DataResponse
from app.db.session import get_db_session
from app.modules.resolutions.repository import ResolutionRepository
from app.modules.resolutions.schemas import (
    ResolutionResponse,
    ResolveComplaintRequest,
    ResolveComplaintResult,
)
from app.modules.resolutions.service import ResolutionService

router = APIRouter(prefix="/api/v1/complaints", tags=["Resolutions"])


def get_resolution_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> ResolutionService:
    return ResolutionService(ResolutionRepository(session))


@router.post(
    "/{id}/resolution",
    response_model=DataResponse[ResolveComplaintResult],
    status_code=status.HTTP_200_OK,
    summary="Resolve complaint",
)
def resolve_complaint(
    id: uuid.UUID,
    payload: ResolveComplaintRequest,
    service: Annotated[ResolutionService, Depends(get_resolution_service)],
    principal: Annotated[Principal, Depends(require_permissions("complaints:update"))],
) -> DataResponse[ResolveComplaintResult]:
    """IN_PROGRESS → RESOLVED with mandatory resolution record (API-225)."""
    result = service.resolve(id, payload, actor_user_id=principal.user_id)
    return DataResponse(data=result)


@router.get(
    "/{id}/resolution",
    response_model=DataResponse[ResolutionResponse],
    status_code=status.HTTP_200_OK,
    summary="Get current complaint resolution",
)
def get_complaint_resolution(
    id: uuid.UUID,
    service: Annotated[ResolutionService, Depends(get_resolution_service)],
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
) -> DataResponse[ResolutionResponse]:
    """Current resolution for display on complaint detail (API-226)."""
    _ = principal
    current = service.get_current(id)
    if current is None:
        raise NotFoundError("Resolution not found")
    return DataResponse(data=current)
