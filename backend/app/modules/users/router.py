"""User HTTP routes."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_permissions
from app.core.schemas import DataResponse, ListResponse, PageMeta
from app.db.session import get_db_session
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import (
    UserCreateRequest,
    UserResponse,
    UserStatusUpdateRequest,
    UserUpdateRequest,
)
from app.modules.users.service import UserService

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


def get_user_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> UserService:
    return UserService(UserRepository(session))


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
) -> DataResponse[UserResponse]:
    created = service.create(payload, actor_user_id=principal.user_id)
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
) -> DataResponse[UserResponse]:
    updated = service.update(id, payload, actor_user_id=principal.user_id)
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
