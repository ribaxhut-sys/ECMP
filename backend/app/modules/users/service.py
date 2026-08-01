"""User application service (no FastAPI imports beyond Request for audit)."""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from fastapi import Request

from app.core.authorization.role_assignment_policy import assert_can_assign_role
from app.core.config import Settings, get_settings
from app.core.errors import ConflictError, NotFoundError, ValidationAppError
from app.core.i18n_messages import SUPPORTED_LANGUAGES
from app.core.password_policy import get_password_policy
from app.core.security import (
    generate_temporary_password,
    hash_password,
    verify_password,
)
from app.core.user_messages import m
from app.models import User
from app.modules.auth.password_helpers import (
    revoke_all_refresh_tokens,
    set_user_password,
    write_password_audit,
)
from app.modules.iam.permission_cache import invalidate_iam_user
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import (
    AdminResetPasswordResponse,
    ChangePasswordRequest,
    ChangePasswordResponse,
    PreferredLanguageUpdateResponse,
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
        forcePasswordChange=bool(getattr(user, "force_password_change", False)),
        lastLoginAt=user.last_login_at,
        createdAt=user.created_at,
        updatedAt=user.updated_at,
        preferredLanguage=getattr(user, "preferred_language", None) or "id",
    )


class UserService:
    def __init__(
        self,
        repository: UserRepository,
        settings: Settings | None = None,
    ) -> None:
        self._repo = repository
        self._settings = settings or get_settings()

    def _policy(self):
        return get_password_policy(min_length=self._settings.password_min_length)

    def _ensure_role(self, role_id: uuid.UUID) -> None:
        if not self._repo.role_exists(role_id):
            raise ValidationAppError(
                m("iam.role_not_found_or_inactive"),
                details={"roleId": str(role_id)},
            )

    def _ensure_assignable_role(
        self,
        role_id: uuid.UUID,
        *,
        actor_roles: Sequence[str],
    ) -> None:
        """UAT-020: reject privilege-escalating role assignments (403)."""
        role_code = self._repo.get_role_code(role_id)
        assert_can_assign_role(
            actor_roles,
            role_code,
            target_role_id=str(role_id),
        )

    def _ensure_branch(self, branch_id: uuid.UUID | None) -> None:
        if branch_id is None:
            return
        if not self._repo.branch_exists(branch_id):
            raise ValidationAppError(
                m("branch.not_found_or_inactive"),
                details={"branchId": str(branch_id)},
            )

    def _ensure_unique_username(
        self, username: str, *, exclude_user_id: uuid.UUID | None = None
    ) -> None:
        if self._repo.username_exists(username, exclude_user_id=exclude_user_id):
            raise ConflictError(
                m("user.username_exists"),
                details={"username": username},
            )

    def _ensure_unique_email(
        self, email: str, *, exclude_user_id: uuid.UUID | None = None
    ) -> None:
        if self._repo.email_exists(email, exclude_user_id=exclude_user_id):
            raise ConflictError(
                m("user.email_exists"),
                details={"email": email},
            )

    def create(
        self,
        payload: UserCreateRequest,
        *,
        actor_user_id: uuid.UUID,
        actor_roles: Sequence[str] = (),
    ) -> UserResponse:
        self._ensure_unique_username(payload.username)
        self._ensure_unique_email(payload.email)
        self._ensure_role(payload.role_id)
        self._ensure_assignable_role(payload.role_id, actor_roles=actor_roles)
        self._ensure_branch(payload.branch_id)
        self._policy().validate(payload.password)

        now = datetime.now(UTC)
        user = User(
            username=payload.username,
            email=payload.email,
            full_name=payload.full_name,
            password_hash=hash_password(payload.password),
            role_id=payload.role_id,
            branch_id=payload.branch_id,
            is_active=payload.is_active,
            # UAT-022: admin-assigned passwords are temporary.
            force_password_change=True,
            created_at=now,
            updated_at=now,
            created_by=actor_user_id,
            updated_by=actor_user_id,
        )
        # UAT-018: users.role_id and user_roles must stay synchronized.
        try:
            self._repo.add(user)
            self._repo.ensure_user_role(user.id, payload.role_id)
            self._repo.commit()
        except Exception:
            self._repo.rollback()
            raise
        self._repo.refresh(user)
        return _to_response(user)

    def get(self, user_id: uuid.UUID) -> UserResponse:
        user = self._repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError(m("user.not_found"))
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
            raise ValidationAppError(m("config.page_min"), details={"page": page})
        if page_size < 1 or page_size > 100:
            raise ValidationAppError(
                m("config.page_size_range"),
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
        actor_roles: Sequence[str] = (),
    ) -> UserResponse:
        user = self._repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError(m("user.not_found"))

        changes = payload.model_dump(exclude_unset=True)
        previous_role_id = user.role_id

        if "username" in changes:
            self._ensure_unique_username(changes["username"], exclude_user_id=user.id)
        if "email" in changes:
            self._ensure_unique_email(changes["email"], exclude_user_id=user.id)
        if "role_id" in changes and changes["role_id"] is not None:
            self._ensure_role(changes["role_id"])
            if changes["role_id"] != previous_role_id:
                self._ensure_assignable_role(
                    changes["role_id"], actor_roles=actor_roles
                )
        if "branch_id" in changes:
            self._ensure_branch(changes["branch_id"])

        password = changes.pop("password", None)
        for field_name, value in changes.items():
            setattr(user, field_name, value)
        if password is not None:
            # UAT-022: admin-set passwords are temporary (same as create/reset).
            self._policy().validate(password, current_hash=user.password_hash)
            set_user_password(
                user,
                password_hash=hash_password(password),
                actor_user_id=actor_user_id,
                force_password_change=True,
            )
            revoke_all_refresh_tokens(self._repo.session, user.id)

        now = datetime.now(UTC)
        user.updated_at = now
        user.updated_by = actor_user_id

        # UAT-021: sync user_roles on primary role change (add new, drop old).
        role_changed = (
            "role_id" in changes
            and changes["role_id"] is not None
            and changes["role_id"] != previous_role_id
        )
        try:
            if role_changed:
                self._repo.sync_primary_user_role(
                    user.id,
                    previous_role_id=previous_role_id,
                    new_role_id=user.role_id,
                )
            self._repo.commit()
        except Exception:
            self._repo.rollback()
            raise
        if role_changed:
            invalidate_iam_user(user.id)
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
            raise NotFoundError(m("user.not_found"))

        now = datetime.now(UTC)
        user.is_active = payload.is_active
        user.updated_at = now
        user.updated_by = actor_user_id

        self._repo.commit()
        self._repo.refresh(user)
        return _to_response(user)

    def change_password(
        self,
        user_id: uuid.UUID,
        payload: ChangePasswordRequest,
        *,
        request: Request | None = None,
    ) -> ChangePasswordResponse:
        user = self._repo.get_by_id(user_id)
        if user is None or not user.is_active:
            raise NotFoundError(m("user.not_found"))
        if not user.password_hash:
            write_password_audit(
                self._repo.session,
                request=request,
                event_type="password.change_failed",
                entity_id=user_id,
                actor_id=user_id,
                new_values={"reason": "no_password_set"},
                commit=True,
            )
            raise ValidationAppError(
                m("auth.current_password_incorrect"),
                details={"field": "currentPassword"},
            )

        if not verify_password(payload.current_password, user.password_hash):
            write_password_audit(
                self._repo.session,
                request=request,
                event_type="password.change_failed",
                entity_id=user_id,
                actor_id=user_id,
                new_values={"reason": "invalid_current_password"},
                commit=True,
            )
            raise ValidationAppError(
                m("auth.current_password_incorrect"),
                details={"field": "currentPassword"},
            )

        try:
            self._policy().validate(
                payload.new_password, current_hash=user.password_hash
            )
        except ValidationAppError:
            write_password_audit(
                self._repo.session,
                request=request,
                event_type="password.change_failed",
                entity_id=user_id,
                actor_id=user_id,
                new_values={"reason": "policy_rejected"},
                commit=True,
            )
            raise

        set_user_password(
            user,
            password_hash=hash_password(payload.new_password),
            actor_user_id=user_id,
            force_password_change=False,
        )
        revoked = revoke_all_refresh_tokens(self._repo.session, user.id)
        write_password_audit(
            self._repo.session,
            request=request,
            event_type="password.changed",
            entity_id=user.id,
            actor_id=user_id,
            new_values={"refreshTokensRevoked": revoked},
            commit=False,
        )
        self._repo.commit()
        return ChangePasswordResponse()

    def update_preferred_language(
        self,
        user_id: uuid.UUID,
        language: str,
    ) -> PreferredLanguageUpdateResponse:
        if language not in SUPPORTED_LANGUAGES:
            raise ValidationAppError(
                m("config.preferred_language_values"),
                details={"preferredLanguage": language},
            )

        user = self._repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError(m("user.not_found"))

        user.preferred_language = language
        user.updated_at = datetime.now(UTC)
        user.updated_by = user_id

        self._repo.commit()
        self._repo.refresh(user)
        return PreferredLanguageUpdateResponse(preferredLanguage=user.preferred_language)

    def admin_reset_password(
        self,
        user_id: uuid.UUID,
        *,
        actor_user_id: uuid.UUID,
        request: Request | None = None,
    ) -> AdminResetPasswordResponse:
        user = self._repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError(m("user.not_found"))

        temporary = generate_temporary_password(
            length=max(16, self._settings.password_min_length)
        )
        set_user_password(
            user,
            password_hash=hash_password(temporary),
            actor_user_id=actor_user_id,
            force_password_change=True,
        )
        revoked = revoke_all_refresh_tokens(self._repo.session, user.id)
        write_password_audit(
            self._repo.session,
            request=request,
            event_type="password.admin_reset",
            entity_id=user.id,
            actor_id=actor_user_id,
            new_values={
                "forcePasswordChange": True,
                "refreshTokensRevoked": revoked,
            },
            commit=False,
        )
        self._repo.commit()
        return AdminResetPasswordResponse(
            userId=user.id,
            temporaryPassword=temporary,
            forcePasswordChange=True,
        )
