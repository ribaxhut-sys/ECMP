"""Role Management HTTP routes (API-338–342 / TASK-033)."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_permissions
from app.core.enums import AuditAction
from app.core.schemas import DataResponse
from app.db.session import get_db_session
from app.modules.audit.hooks import write_audit
from app.modules.iam.role.permissions import (
    ROLE_CREATE,
    ROLE_DELETE,
    ROLE_READ,
    ROLE_UPDATE,
)
from app.modules.iam.role.repository import RoleRepository
from app.modules.iam.role.schemas import (
    RoleCreateRequest,
    RoleResponse,
    RoleUpdateRequest,
)
from app.modules.iam.role.service import RoleService

router = APIRouter(prefix="/api/v1/roles", tags=["Roles"])


def get_role_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> RoleService:
    return RoleService(RoleRepository(session))


def _role_snapshot(row: RoleResponse) -> dict:
    return {
        "id": str(row.id),
        "code": row.code,
        "name": row.name,
        "description": row.description,
        "isSystem": row.is_system,
        "isActive": row.is_active,
    }


@router.get(
    "",
    response_model=DataResponse[list[RoleResponse]],
    status_code=status.HTTP_200_OK,
    summary="List roles",
)
def list_roles(
    service: Annotated[RoleService, Depends(get_role_service)],
    principal: Annotated[Principal, Depends(require_permissions(ROLE_READ))],
    active_only: Annotated[
        bool, Query(alias="activeOnly", description="Return active roles only")
    ] = False,
    include_system: Annotated[
        bool,
        Query(alias="includeSystem", description="Include system (seed) roles"),
    ] = True,
) -> DataResponse[list[RoleResponse]]:
    """API-338 — list role master records."""
    _ = principal
    return DataResponse(
        data=service.list(active_only=active_only, include_system=include_system)
    )


@router.post(
    "",
    response_model=DataResponse[RoleResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create role",
)
def create_role(
    payload: RoleCreateRequest,
    request: Request,
    session: Annotated[Session, Depends(get_db_session)],
    service: Annotated[RoleService, Depends(get_role_service)],
    principal: Annotated[Principal, Depends(require_permissions(ROLE_CREATE))],
) -> DataResponse[RoleResponse]:
    """API-339 — create a non-system role."""
    result = service.create(payload)
    write_audit(
        session,
        request=request,
        principal=principal,
        event_type="role.created",
        entity_type="Role",
        action=AuditAction.CREATE,
        entity_id=result.id,
        new_values=_role_snapshot(result),
    )
    return DataResponse(data=result)


@router.get(
    "/{role_id}",
    response_model=DataResponse[RoleResponse],
    status_code=status.HTTP_200_OK,
    summary="Get role",
)
def get_role(
    role_id: uuid.UUID,
    service: Annotated[RoleService, Depends(get_role_service)],
    principal: Annotated[Principal, Depends(require_permissions(ROLE_READ))],
) -> DataResponse[RoleResponse]:
    """API-340 — get role by id."""
    _ = principal
    return DataResponse(data=service.get(role_id))


@router.put(
    "/{role_id}",
    response_model=DataResponse[RoleResponse],
    status_code=status.HTTP_200_OK,
    summary="Update role",
)
def update_role(
    role_id: uuid.UUID,
    payload: RoleUpdateRequest,
    request: Request,
    session: Annotated[Session, Depends(get_db_session)],
    service: Annotated[RoleService, Depends(get_role_service)],
    principal: Annotated[Principal, Depends(require_permissions(ROLE_UPDATE))],
) -> DataResponse[RoleResponse]:
    """API-341 — update role name / description / isActive (code immutable)."""
    before = service.get(role_id)
    result = service.update(role_id, payload)
    write_audit(
        session,
        request=request,
        principal=principal,
        event_type="role.updated",
        entity_type="Role",
        action=AuditAction.UPDATE,
        entity_id=result.id,
        old_values=_role_snapshot(before),
        new_values=_role_snapshot(result),
    )
    return DataResponse(data=result)


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete role",
    response_class=Response,
)
def delete_role(
    role_id: uuid.UUID,
    request: Request,
    session: Annotated[Session, Depends(get_db_session)],
    service: Annotated[RoleService, Depends(get_role_service)],
    principal: Annotated[Principal, Depends(require_permissions(ROLE_DELETE))],
) -> Response:
    """API-342 — soft-delete role. System roles (is_system) are rejected."""
    before = service.get(role_id)
    service.delete(role_id)
    write_audit(
        session,
        request=request,
        principal=principal,
        event_type="role.deleted",
        entity_type="Role",
        action=AuditAction.DELETE,
        entity_id=role_id,
        old_values=_role_snapshot(before),
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
