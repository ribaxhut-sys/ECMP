"""User HTTP routes."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import (
    CurrentPrincipal,
    OrgUnitResolver,
    Principal,
    enforce_org_scope,
    require_permissions,
    require_user_status_update,
)
from app.core.authorization.org_unit_guard import org_scope_enforcement_enabled
from app.core.config import Settings, get_settings
from app.core.local_credential_auth import (
    assert_local_credential_auth_enabled,
    require_local_credential_auth,
)
from app.core.schemas import DataResponse, ListResponse, PageMeta
from app.db.session import get_db_session
from app.models import Branch
from app.modules.users.org_scope import (
    assert_declared_branch_in_same_unit,
    assert_target_user_in_same_unit,
)
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
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    _: LocalCredentialAuth,
) -> DataResponse[UserResponse]:
    # UX-CU-002 R2 / SECMIG-P4 reuse: declared Unit must match the administrator's
    # own org-scope claim. No-op unless ECMP_AUTH_MODE=jwt (org_scope_enforcement_enabled).
    declared_org = None
    if payload.branch_id is not None:
        branch = session.get(Branch, payload.branch_id)
        declared_org = OrgUnitResolver.normalize(branch.code if branch else None)
    enforce_org_scope(principal, declared_org, settings)
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
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
    is_active: Annotated[bool | None, Query(alias="isActive")] = None,
    role_id: Annotated[uuid.UUID | None, Query(alias="roleId")] = None,
    branch_id: Annotated[uuid.UUID | None, Query(alias="branchId")] = None,
) -> ListResponse[UserResponse]:
    # UM-SEC-001 TASK 1/2 — same scope predicate as users:create (OrgUnitGuard,
    # SECMIG-P4), applied as a list filter instead of a single-resource raise.
    if org_scope_enforcement_enabled(settings):
        principal_org = OrgUnitResolver.normalize(principal.org_unit_id)
        if principal_org is not None:
            if branch_id is not None:
                branch = session.get(Branch, branch_id)
                requested_org = OrgUnitResolver.normalize(
                    branch.code if branch else None
                )
                # Reuses the exact create-path comparator/error shape — an
                # explicit cross-unit list request is denied, not silently
                # narrowed to the admin's own unit.
                enforce_org_scope(principal, requested_org, settings)
            else:
                own_branch_id = session.scalar(
                    select(Branch.id).where(Branch.code == principal_org)
                )
                branch_id = own_branch_id
        # principal_org is None (head-office-scoped role, or missing claim):
        # left UNRESTRICTED here — see UX-UM-001 §8.1 / Remaining Repository
        # Gaps. Head-office-scoped roles are defined repo-wide (Branch
        # requirement is forbidden for them, users/service.py
        # _ensure_branch_for_role) as operating across all units; a formal
        # "does Head Office get GLOBAL list visibility" business rule has not
        # been written down anywhere, so this is reported as an open gap
        # rather than silently asserted as correct. It is NOT a bypass this
        # change introduces — it is the endpoint's pre-existing behavior,
        # preserved because blocking it would 403 every head-office
        # administrator out of the only membership list ECMP has.
    elif branch_id is None:
        # UM-BUG-005 — Mode A (ECMP_AUTH_MODE=dev) issues no orgUnitId claim,
        # so the JWT-mode narrowing above never fires locally and a branch
        # supervisor saw every branch's users in the lab. The domain rule
        # ("see only your own unit") must hold in both modes (CLAUDE.md §2);
        # only the org-unit source differs — DB membership here instead of
        # an SSO claim.
        principal_org = OrgUnitResolver(session).resolve_principal_membership(
            principal.user_id
        )
        if principal_org is not None:
            branch_id = session.scalar(
                select(Branch.id).where(Branch.code == principal_org)
            )
    else:
        # G4-4 — the other half of UM-BUG-005: an explicit cross-unit
        # ?branchId= was still answered in Mode A because only the jwt path
        # above compared it. Same comparator as users:create / PUT /users/{id};
        # an actor whose own unit cannot be resolved (head-office membership)
        # stays unrestricted, exactly like the no-filter branch above.
        if OrgUnitResolver(session).resolve_principal(principal) is not None:
            assert_declared_branch_in_same_unit(principal, branch_id, session)
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
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[UserResponse]:
    # UM-SEC-002 TASK 1/2/3 — same reused idiom as update_user_status
    # (single-resource compare): OrgUnitResolver + enforce_org_scope
    # (SECMIG-P4). No-op unless ECMP_AUTH_MODE=jwt.
    target_org = OrgUnitResolver(session).resolve_user(id)
    enforce_org_scope(principal, target_org, settings)
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
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[UserResponse]:
    # Password field is Mode A local credential surface (K-3); profile-only updates stay open.
    if payload.password is not None:
        assert_local_credential_auth_enabled(settings)
    # UM-SEC-P0-1 — a branch-scoped administrator must not edit another unit's
    # member; same comparison PATCH /{id}/status already enforces.
    assert_target_user_in_same_unit(principal, id, session)
    if payload.branch_id is not None:
        assert_declared_branch_in_same_unit(principal, payload.branch_id, session)
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
    principal: Annotated[Principal, Depends(require_user_status_update)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[UserResponse]:
    # UM-BUG-007 — Manager (BC-8.4) is branch-scoped, unlike Head Office
    # Admin/Administrator/Super Admin (unrestricted, unchanged). Behavior
    # unchanged; the comparison now lives in the shared helper above.
    assert_target_user_in_same_unit(principal, id, session)
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
    session: Annotated[Session, Depends(get_db_session)],
    _: LocalCredentialAuth,
) -> DataResponse[AdminResetPasswordResponse]:
    # UM-SEC-P0-2 — endpoint stays available (SEC-PWD-001, Mode A local
    # credential surface); it is only narrowed to the actor's own unit.
    assert_target_user_in_same_unit(principal, id, session)
    result = service.admin_reset_password(
        id, actor_user_id=principal.user_id, request=request
    )
    return DataResponse(data=result)
