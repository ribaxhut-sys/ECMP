"""User-Role Assignment HTTP routes (API-351–353 / TASK-036)."""

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
from app.modules.iam.role.schemas import RoleResponse
from app.modules.iam.user_role.permissions import USER_ROLE_READ, USER_ROLE_UPDATE
from app.modules.iam.user_role.repository import UserRoleRepository
from app.modules.iam.user_role.schemas import UserRolesReplaceRequest
from app.modules.iam.user_role.service import UserRoleService
from app.modules.users.schemas import UserResponse

users_roles_router = APIRouter(prefix="/api/v1/users", tags=["User Roles"])
roles_users_router = APIRouter(prefix="/api/v1/roles", tags=["User Roles"])


def get_user_role_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> UserRoleService:
    return UserRoleService(UserRoleRepository(session))


def _snapshot(roles: list[RoleResponse]) -> dict:
    return {
        "roleIds": [str(r.id) for r in roles],
        "roleCodes": [r.code for r in roles],
    }


@users_roles_router.get(
    "/{user_id}/roles",
    response_model=DataResponse[list[RoleResponse]],
    status_code=status.HTTP_200_OK,
    summary="List user roles",
)
def get_user_roles(
    user_id: uuid.UUID,
    service: Annotated[UserRoleService, Depends(get_user_role_service)],
    principal: Annotated[Principal, Depends(require_permissions(USER_ROLE_READ))],
) -> DataResponse[list[RoleResponse]]:
    """API-351 — list roles assigned to a user (junction table)."""
    _ = principal
    return DataResponse(data=service.get_user_roles(user_id))


@users_roles_router.put(
    "/{user_id}/roles",
    response_model=DataResponse[list[RoleResponse]],
    status_code=status.HTTP_200_OK,
    summary="Replace user roles",
)
def replace_user_roles(
    user_id: uuid.UUID,
    payload: UserRolesReplaceRequest,
    request: Request,
    session: Annotated[Session, Depends(get_db_session)],
    service: Annotated[UserRoleService, Depends(get_user_role_service)],
    principal: Annotated[Principal, Depends(require_permissions(USER_ROLE_UPDATE))],
) -> DataResponse[list[RoleResponse]]:
    """API-352 — replace full role set for a user (empty clears)."""
    before = service.get_user_roles(user_id)
    result = service.replace_roles(user_id, payload)
    write_audit(
        session,
        request=request,
        principal=principal,
        event_type="user.roles.updated",
        entity_type="User",
        action=AuditAction.UPDATE,
        entity_id=user_id,
        old_values=_snapshot(before),
        new_values=_snapshot(result),
        metadata={"roleCount": len(result)},
    )
    return DataResponse(data=result)


@roles_users_router.get(
    "/{role_id}/users",
    response_model=DataResponse[list[UserResponse]],
    status_code=status.HTTP_200_OK,
    summary="List role users",
)
def get_role_users(
    role_id: uuid.UUID,
    service: Annotated[UserRoleService, Depends(get_user_role_service)],
    principal: Annotated[Principal, Depends(require_permissions(USER_ROLE_READ))],
) -> DataResponse[list[UserResponse]]:
    """API-353 — list users that have a role (junction table)."""
    _ = principal
    return DataResponse(data=service.get_role_users(role_id))
