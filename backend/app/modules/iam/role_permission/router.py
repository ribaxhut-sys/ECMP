"""Role-Permission Matrix HTTP routes (API-348–350 / TASK-035)."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_permissions
from app.core.enums import AuditAction
from app.core.schemas import DataResponse
from app.db.session import get_db_session
from app.modules.audit.hooks import write_audit
from app.modules.iam.permission.schemas import PermissionResponse
from app.modules.iam.role.schemas import RoleResponse
from app.modules.iam.role_permission.permissions import (
    ROLE_PERMISSION_READ,
    ROLE_PERMISSION_UPDATE,
)
from app.modules.iam.role_permission.repository import RolePermissionRepository
from app.modules.iam.role_permission.schemas import RolePermissionsReplaceRequest
from app.modules.iam.role_permission.service import RolePermissionService

roles_matrix_router = APIRouter(prefix="/api/v1/roles", tags=["Role Permissions"])
permissions_matrix_router = APIRouter(
    prefix="/api/v1/permissions", tags=["Role Permissions"]
)


def get_role_permission_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> RolePermissionService:
    return RolePermissionService(RolePermissionRepository(session))


def _snapshot(permissions: list[PermissionResponse]) -> dict:
    return {
        "permissionIds": [str(p.id) for p in permissions],
        "permissionCodes": [p.code for p in permissions],
    }


@roles_matrix_router.get(
    "/{role_id}/permissions",
    response_model=DataResponse[list[PermissionResponse]],
    status_code=status.HTTP_200_OK,
    summary="List role permissions",
)
def get_role_permissions(
    role_id: uuid.UUID,
    service: Annotated[RolePermissionService, Depends(get_role_permission_service)],
    principal: Annotated[
        Principal, Depends(require_permissions(ROLE_PERMISSION_READ))
    ],
) -> DataResponse[list[PermissionResponse]]:
    """API-348 — list permissions assigned to a role."""
    _ = principal
    return DataResponse(data=service.get_role_permissions(role_id))


@roles_matrix_router.put(
    "/{role_id}/permissions",
    response_model=DataResponse[list[PermissionResponse]],
    status_code=status.HTTP_200_OK,
    summary="Replace role permissions",
)
def replace_role_permissions(
    role_id: uuid.UUID,
    payload: RolePermissionsReplaceRequest,
    request: Request,
    session: Annotated[Session, Depends(get_db_session)],
    service: Annotated[RolePermissionService, Depends(get_role_permission_service)],
    principal: Annotated[
        Principal, Depends(require_permissions(ROLE_PERMISSION_UPDATE))
    ],
) -> DataResponse[list[PermissionResponse]]:
    """API-349 — replace full permission set for a role (empty clears)."""
    before = service.get_role_permissions(role_id)
    result = service.replace_permissions(role_id, payload)
    write_audit(
        session,
        request=request,
        principal=principal,
        event_type="role.permissions.updated",
        entity_type="Role",
        action=AuditAction.UPDATE,
        entity_id=role_id,
        old_values=_snapshot(before),
        new_values=_snapshot(result),
        metadata={"permissionCount": len(result)},
    )
    return DataResponse(data=result)


@permissions_matrix_router.get(
    "/{permission_id}/roles",
    response_model=DataResponse[list[RoleResponse]],
    status_code=status.HTTP_200_OK,
    summary="List permission roles",
)
def get_permission_roles(
    permission_id: uuid.UUID,
    service: Annotated[RolePermissionService, Depends(get_role_permission_service)],
    principal: Annotated[
        Principal, Depends(require_permissions(ROLE_PERMISSION_READ))
    ],
) -> DataResponse[list[RoleResponse]]:
    """API-350 — list roles that have a permission."""
    _ = principal
    return DataResponse(data=service.get_permission_roles(permission_id))
