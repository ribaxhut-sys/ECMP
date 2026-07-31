"""User HTTP routes."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.auth import CurrentPrincipal, Principal, require_permissions
from app.core.config import Settings, get_settings
from app.core.local_credential_auth import (
    assert_local_credential_auth_enabled,
    require_local_credential_auth,
)
from app.core.schemas import DataResponse, ListResponse, PageMeta
from app.db.session import get_db_session
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import (
    AdminResetPasswordResponse,
    ChangePasswordRequest,
    ChangePasswordResponse,
    PreferredLanguageUpdateRequest,
    PreferredLanguageUpdateResponse,
    UserCreateRequest,
    UserResponse,
    UserStatusUpdateRequest,
    UserUpdateRequest,
)
from app.modules.users.service import UserService

router = APIRouter(prefix="/api/v1/users", tags=["Users"])

LocalCredentialAuth = Annotated[Settings, Depends(require_local_credential_auth)]


def get_user_service(
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UserService:
    return UserService(UserRepository(session), settings)


@router.post(
    "/me/change-password",
    response_model=DataResponse[ChangePasswordResponse],
    status_code=status.HTTP_200_OK,
    summary="Change own password",
)
def change_own_password(
    payload: ChangePasswordRequest,
    request: Request,
    service: Annotated[UserService, Depends(get_user_service)],
    principal: CurrentPrincipal,
    _: LocalCredentialAuth,
) -> DataResponse[ChangePasswordResponse]:
    result = service.change_password(
        principal.user_id, payload, request=request
    )
    return DataResponse(data=result)


@router.patch(
    "/me/preferred-language",
    response_model=DataResponse[PreferredLanguageUpdateResponse],
    status_code=status.HTTP_200_OK,
    summary="Update own preferred language",
)
def update_own_preferred_language(
    payload: PreferredLanguageUpdateRequest,
    service: Annotated[UserService, Depends(get_user_service)],
    principal: CurrentPrincipal,
) -> DataResponse[PreferredLanguageUpdateResponse]:
    result = service.update_preferred_language(
        principal.user_id, payload.preferred_language
    )
    return DataResponse(data=result)


@router.post(
    "",
    response_model=DataResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
)
def create_user(
    payload: UserCreateRequest,
    service: Annotated[UserService, Depends(get_user_service)],
    principal: Annotated[Principal, Depends(require_permissions("users:create"))],
    _: LocalCredentialAuth,
) -> DataResponse[UserResponse]:
    created = service.create(
        payload,
        actor_user_id=principal.user_id,
        actor_roles=principal.roles,
    )
    return DataResponse(data=created)


@router.get(
    "",
    response_model=ListResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="List users",
)
def list_users(
    service: Annotated[UserService, Depends(get_user_service)],
    principal: Annotated[Principal, Depends(require_permissions("users:read"))],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
    is_active: Annotated[bool | None, Query(alias="isActive")] = None,
    role_id: Annotated[uuid.UUID | None, Query(alias="roleId")] = None,
    branch_id: Annotated[uuid.UUID | None, Query(alias="branchId")] = None,
) -> ListResponse[UserResponse]:
    _ = principal
    items, total = service.list(
        page=page,
        page_size=page_size,
        is_active=is_active,
        role_id=role_id,
        branch_id=branch_id,
    )
    return ListResponse(
        data=items,
        meta=PageMeta(page=page, pageSize=page_size, totalItems=total),
    )


@router.get(
    "/{id}",
    response_model=DataResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Get user by id",
)
def get_user(
    id: uuid.UUID,
    service: Annotated[UserService, Depends(get_user_service)],
    principal: Annotated[Principal, Depends(require_permissions("users:read"))],
) -> DataResponse[UserResponse]:
    _ = principal
    return DataResponse(data=service.get(id))


@router.put(
    "/{id}",
    response_model=DataResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Update user",
)
def update_user(
    id: uuid.UUID,
    payload: UserUpdateRequest,
    service: Annotated[UserService, Depends(get_user_service)],
    principal: Annotated[Principal, Depends(require_permissions("users:update"))],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[UserResponse]:
    # Password field is Mode A local credential surface (K-3); profile-only updates stay open.
    if payload.password is not None:
        assert_local_credential_auth_enabled(settings)
    updated = service.update(
        id,
        payload,
        actor_user_id=principal.user_id,
        actor_roles=principal.roles,
    )
    return DataResponse(data=updated)


@router.patch(
    "/{id}/status",
    response_model=DataResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Activate or deactivate user",
)
def update_user_status(
    id: uuid.UUID,
    payload: UserStatusUpdateRequest,
    service: Annotated[UserService, Depends(get_user_service)],
    principal: Annotated[Principal, Depends(require_permissions("users:update"))],
) -> DataResponse[UserResponse]:
    updated = service.update_status(id, payload, actor_user_id=principal.user_id)
    return DataResponse(data=updated)


@router.post(
    "/{id}/reset-password",
    response_model=DataResponse[AdminResetPasswordResponse],
    status_code=status.HTTP_200_OK,
    summary="Admin reset user password",
)
def admin_reset_password(
    id: uuid.UUID,
    request: Request,
    service: Annotated[UserService, Depends(get_user_service)],
    principal: Annotated[
        Principal, Depends(require_permissions("users:reset_password"))
    ],
    _: LocalCredentialAuth,
) -> DataResponse[AdminResetPasswordResponse]:
    result = service.admin_reset_password(
        id, actor_user_id=principal.user_id, request=request
    )
    return DataResponse(data=result)
