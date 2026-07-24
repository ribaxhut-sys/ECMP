"""Permission Management HTTP routes (API-343–347 / TASK-034)."""

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
from app.modules.iam.permission.permissions import (
    PERMISSION_CREATE,
    PERMISSION_DELETE,
    PERMISSION_READ,
    PERMISSION_UPDATE,
)
from app.modules.iam.permission.repository import PermissionRepository
from app.modules.iam.permission.schemas import (
    PermissionCreateRequest,
    PermissionResponse,
    PermissionUpdateRequest,
)
from app.modules.iam.permission.service import PermissionService

router = APIRouter(prefix="/api/v1/permissions", tags=["Permissions"])


def get_permission_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> PermissionService:
    return PermissionService(PermissionRepository(session))


def _permission_snapshot(row: PermissionResponse) -> dict:
    return {
        "id": str(row.id),
        "code": row.code,
        "name": row.name,
        "module": row.module,
        "description": row.description,
        "isSystem": row.is_system,
        "isActive": row.is_active,
    }


@router.get(
    "",
    response_model=DataResponse[list[PermissionResponse]],
    status_code=status.HTTP_200_OK,
    summary="List permissions",
)
def list_permissions(
    service: Annotated[PermissionService, Depends(get_permission_service)],
    principal: Annotated[Principal, Depends(require_permissions(PERMISSION_READ))],
    active_only: Annotated[
        bool, Query(alias="activeOnly", description="Return active permissions only")
    ] = False,
    include_system: Annotated[
        bool,
        Query(alias="includeSystem", description="Include system (seed) permissions"),
    ] = True,
    module: Annotated[
        str | None,
        Query(description="Filter by module (e.g. complaint)"),
    ] = None,
) -> DataResponse[list[PermissionResponse]]:
    """API-343 — list permission master records."""
    _ = principal
    return DataResponse(
        data=service.list(
            active_only=active_only,
            include_system=include_system,
            module=module.strip().lower() if module else None,
        )
    )


@router.post(
    "",
    response_model=DataResponse[PermissionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create permission",
)
def create_permission(
    payload: PermissionCreateRequest,
    request: Request,
    session: Annotated[Session, Depends(get_db_session)],
    service: Annotated[PermissionService, Depends(get_permission_service)],
    principal: Annotated[Principal, Depends(require_permissions(PERMISSION_CREATE))],
) -> DataResponse[PermissionResponse]:
    """API-344 — create a non-system permission."""
    result = service.create(payload)
    write_audit(
        session,
        request=request,
        principal=principal,
        event_type="permission.created",
        entity_type="Permission",
        action=AuditAction.CREATE,
        entity_id=result.id,
        new_values=_permission_snapshot(result),
    )
    return DataResponse(data=result)


@router.get(
    "/{permission_id}",
    response_model=DataResponse[PermissionResponse],
    status_code=status.HTTP_200_OK,
    summary="Get permission",
)
def get_permission(
    permission_id: uuid.UUID,
    service: Annotated[PermissionService, Depends(get_permission_service)],
    principal: Annotated[Principal, Depends(require_permissions(PERMISSION_READ))],
) -> DataResponse[PermissionResponse]:
    """API-345 — get permission by id."""
    _ = principal
    return DataResponse(data=service.get(permission_id))


@router.put(
    "/{permission_id}",
    response_model=DataResponse[PermissionResponse],
    status_code=status.HTTP_200_OK,
    summary="Update permission",
)
def update_permission(
    permission_id: uuid.UUID,
    payload: PermissionUpdateRequest,
    request: Request,
    session: Annotated[Session, Depends(get_db_session)],
    service: Annotated[PermissionService, Depends(get_permission_service)],
    principal: Annotated[Principal, Depends(require_permissions(PERMISSION_UPDATE))],
) -> DataResponse[PermissionResponse]:
    """API-346 — update name / description / isActive (code immutable)."""
    before = service.get(permission_id)
    result = service.update(permission_id, payload)
    write_audit(
        session,
        request=request,
        principal=principal,
        event_type="permission.updated",
        entity_type="Permission",
        action=AuditAction.UPDATE,
        entity_id=result.id,
        old_values=_permission_snapshot(before),
        new_values=_permission_snapshot(result),
    )
    return DataResponse(data=result)


@router.delete(
    "/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete permission",
    response_class=Response,
)
def delete_permission(
    permission_id: uuid.UUID,
    request: Request,
    session: Annotated[Session, Depends(get_db_session)],
    service: Annotated[PermissionService, Depends(get_permission_service)],
    principal: Annotated[Principal, Depends(require_permissions(PERMISSION_DELETE))],
) -> Response:
    """API-347 — soft-delete permission. System permissions rejected."""
    before = service.get(permission_id)
    service.delete(permission_id)
    write_audit(
        session,
        request=request,
        principal=principal,
        event_type="permission.deleted",
        entity_type="Permission",
        action=AuditAction.DELETE,
        entity_id=permission_id,
        old_values=_permission_snapshot(before),
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
