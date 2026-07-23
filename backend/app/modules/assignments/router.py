"""Assignment HTTP routes."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_permissions, require_supervisor_assign
from app.core.schemas import DataResponse
from app.db.session import get_db_session
from app.modules.assignments.repository import AssignmentRepository
from app.modules.assignments.schemas import (
    AssignComplaintRequest,
    AssignComplaintResult,
    AssignmentResponse,
)
from app.modules.assignments.service import AssignmentService

router = APIRouter(prefix="/api/v1/complaints", tags=["Assignments"])


def get_assignment_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> AssignmentService:
    return AssignmentService(AssignmentRepository(session))


@router.post(
    "/{id}/assign",
    response_model=DataResponse[AssignComplaintResult],
    status_code=status.HTTP_200_OK,
    summary="Assign or reassign complaint",
)
def assign_complaint(
    id: uuid.UUID,
    payload: AssignComplaintRequest,
    service: Annotated[AssignmentService, Depends(get_assignment_service)],
    principal: Annotated[Principal, Depends(require_supervisor_assign)],
) -> DataResponse[AssignComplaintResult]:
    result = service.assign(id, payload, actor_user_id=principal.user_id)
    return DataResponse(data=result)


@router.get(
    "/{id}/assignments",
    response_model=DataResponse[list[AssignmentResponse]],
    status_code=status.HTTP_200_OK,
    summary="List assignment history",
)
def list_assignments(
    id: uuid.UUID,
    service: Annotated[AssignmentService, Depends(get_assignment_service)],
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
) -> DataResponse[list[AssignmentResponse]]:
    _ = principal
    return DataResponse(data=service.list_assignments(id))
