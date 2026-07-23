"""User application service (no FastAPI imports)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.core.errors import ConflictError, NotFoundError, ValidationAppError
from app.core.security import hash_password
from app.models import User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import (
    UserCreateRequest,
    UserResponse,
    UserStatusUpdateRequest,
    UserUpdateRequest,
)


def _to_response(user: User) -> UserResponse:
    # Prefer already-loaded role; avoid lazy-load in unit tests / detached instances.
    role = user.__dict__.get("role")
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        fullName=user.full_name,
        roleId=user.role_id,
        roleCode=getattr(role, "code", None) if role is not None else None,
        roleName=getattr(role, "name", None) if role is not None else None,
        branchId=user.branch_id,
        isActive=user.is_active,
        lastLoginAt=user.last_login_at,
        createdAt=user.created_at,
        updatedAt=user.updated_at,
    )


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repo = repository

    def _ensure_role(self, role_id: uuid.UUID) -> None:
        if not self._repo.role_exists(role_id):
            raise ValidationAppError(
                "Role not found or inactive",
                details={"roleId": str(role_id)},
            )

    def _ensure_branch(self, branch_id: uuid.UUID | None) -> None:
        if branch_id is None:
            return
        if not self._repo.branch_exists(branch_id):
            raise ValidationAppError(
                "Branch not found or inactive",
                details={"branchId": str(branch_id)},
            )

    def _ensure_unique_username(
        self, username: str, *, exclude_user_id: uuid.UUID | None = None
    ) -> None:
        if self._repo.username_exists(username, exclude_user_id=exclude_user_id):
            raise ConflictError(
                "Username already exists",
                details={"username": username},
            )

    def _ensure_unique_email(
        self, email: str, *, exclude_user_id: uuid.UUID | None = None
    ) -> None:
        if self._repo.email_exists(email, exclude_user_id=exclude_user_id):
            raise ConflictError(
                "Email already exists",
                details={"email": email},
            )

    def create(
        self,
        payload: UserCreateRequest,
        *,
        actor_user_id: uuid.UUID,
    ) -> UserResponse:
        self._ensure_unique_username(payload.username)
        self._ensure_unique_email(payload.email)
        self._ensure_role(payload.role_id)
        self._ensure_branch(payload.branch_id)

        now = datetime.now(UTC)
        user = User(
            username=payload.username,
            email=payload.email,
            full_name=payload.full_name,
            password_hash=hash_password(payload.password),
            role_id=payload.role_id,
            branch_id=payload.branch_id,
            is_active=payload.is_active,
            created_at=now,
            updated_at=now,
            created_by=actor_user_id,
            updated_by=actor_user_id,
        )
        self._repo.add(user)
        self._repo.commit()
        self._repo.refresh(user)
        return _to_response(user)

    def get(self, user_id: uuid.UUID) -> UserResponse:
        user = self._repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found")
        return _to_response(user)

    def list(
        self,
        *,
        page: int,
        page_size: int,
        is_active: bool | None = None,
        role_id: uuid.UUID | None = None,
        branch_id: uuid.UUID | None = None,
    ) -> tuple[list[UserResponse], int]:
        if page < 1:
            raise ValidationAppError("page must be >= 1", details={"page": page})
        if page_size < 1 or page_size > 100:
            raise ValidationAppError(
                "pageSize must be between 1 and 100",
                details={"pageSize": page_size},
            )
        items, total = self._repo.list_page(
            page=page,
            page_size=page_size,
            is_active=is_active,
            role_id=role_id,
            branch_id=branch_id,
        )
        return [_to_response(item) for item in items], total

    def update(
        self,
        user_id: uuid.UUID,
        payload: UserUpdateRequest,
        *,
        actor_user_id: uuid.UUID,
    ) -> UserResponse:
        user = self._repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found")

        changes = payload.model_dump(exclude_unset=True)

        if "username" in changes:
            self._ensure_unique_username(changes["username"], exclude_user_id=user.id)
        if "email" in changes:
            self._ensure_unique_email(changes["email"], exclude_user_id=user.id)
        if "role_id" in changes and changes["role_id"] is not None:
            self._ensure_role(changes["role_id"])
        if "branch_id" in changes:
            self._ensure_branch(changes["branch_id"])

        password = changes.pop("password", None)
        for field_name, value in changes.items():
            setattr(user, field_name, value)
        if password is not None:
            user.password_hash = hash_password(password)

        now = datetime.now(UTC)
        user.updated_at = now
        user.updated_by = actor_user_id

        self._repo.commit()
        self._repo.refresh(user)
        return _to_response(user)

    def update_status(
        self,
        user_id: uuid.UUID,
        payload: UserStatusUpdateRequest,
        *,
        actor_user_id: uuid.UUID,
    ) -> UserResponse:
        """Soft activate/deactivate via is_active — never hard-deletes."""
        user = self._repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found")

        now = datetime.now(UTC)
        user.is_active = payload.is_active
        user.updated_at = now
        user.updated_by = actor_user_id

        self._repo.commit()
        self._repo.refresh(user)
        return _to_response(user)
