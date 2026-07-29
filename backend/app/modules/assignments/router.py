"""Assignment HTTP routes."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.auth import (
    OrgUnitResolver,
    Principal,
    enforce_org_scope,
    require_permissions,
    require_supervisor_assign,
)
from app.core.config import Settings, get_settings
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
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[AssignComplaintResult]:
    # Permission (+ supervisor role) already validated; org scope runs next.
    resource_org = OrgUnitResolver(session).resolve_complaint(id)
    enforce_org_scope(principal, resource_org, settings)
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
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[list[AssignmentResponse]]:
    """SECMIG-P4-001R M-1: approved G1 read — org scope after permission."""
    resource_org = OrgUnitResolver(session).resolve_complaint(id)
    enforce_org_scope(principal, resource_org, settings)
    return DataResponse(data=service.list_assignments(id))
