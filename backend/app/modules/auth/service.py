"""Authentication application service (no FastAPI imports)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.core.config import Settings
from app.core.errors import UnauthenticatedError
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_refresh_token,
    verify_password,
)
from app.models import RefreshToken, User
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import AuthMeResponse, LoginRequest, TokenResponse
from app.modules.iam.permission_resolver import PermissionResolver
from app.modules.iam.role.models import Role
from app.modules.iam.user_role.models import UserRole


@dataclass(frozen=True, slots=True)
class AuthSession:
    """Access-token payload plus opaque refresh token for cookie (never log)."""

    tokens: TokenResponse
    refresh_token: str
    user_id: uuid.UUID


def _legacy_role_code(user: User) -> str | None:
    role = getattr(user, "role", None)
    if role is None:
        return None
    return role.code


def _role_codes_for_user(repository: AuthRepository, user: User) -> list[str]:
    """Prefer user_roles junction; fall back to legacy users.role_id."""
    session = repository.session
    stmt = (
        select(Role.code)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(
            UserRole.user_id == user.id,
            Role.deleted_at.is_(None),
            Role.is_active.is_(True),
        )
        .order_by(Role.code.asc())
    )
    codes = [str(code) for code in session.scalars(stmt).all()]
    if codes:
        return codes
    legacy = _legacy_role_code(user)
    return [legacy] if legacy else []


def _claims_for_user(repository: AuthRepository, user: User) -> dict:
    # Permissions are resolved per-request via PermissionResolver — not embedded.
    return {
        "roles": _role_codes_for_user(repository, user),
    }


def _to_me(repository: AuthRepository, user: User) -> AuthMeResponse:
    roles = _role_codes_for_user(repository, user)
    permissions = PermissionResolver(repository.session).resolve_sorted(user.id)
    base = AuthMeResponse.model_validate(user)
    return base.model_copy(
        update={
            "roles": roles,
            "permissions": permissions,
        }
    )


class AuthService:
    def __init__(self, repository: AuthRepository, settings: Settings) -> None:
        self._repo = repository
        self._settings = settings

    def _issue_access(self, user: User) -> TokenResponse:
        token = create_access_token(
            subject=str(user.id),
            settings=self._settings,
            claims=_claims_for_user(self._repo, user),
        )
        return TokenResponse(
            accessToken=token,
            tokenType="Bearer",
            expiresIn=self._settings.access_token_expire_seconds,
        )

    def _create_refresh_row(self, user_id: uuid.UUID) -> tuple[RefreshToken, str]:
        raw = generate_refresh_token()
        now = datetime.now(UTC)
        row = RefreshToken(
            user_id=user_id,
            token_hash=hash_refresh_token(raw),
            expires_at=now
            + timedelta(days=self._settings.jwt_refresh_token_expire_days),
            created_at=now,
        )
        self._repo.add_refresh_token(row)
        return row, raw

    def login(self, payload: LoginRequest) -> AuthSession:
        user = self._repo.get_user_by_login(payload.username)
        if user is None or not user.is_active or not user.password_hash:
            raise UnauthenticatedError("Invalid username or password")
        if not verify_password(payload.password, user.password_hash):
            raise UnauthenticatedError("Invalid username or password")

        now = datetime.now(UTC)
        user.last_login_at = now
        user.updated_at = now

        refresh_row, raw_refresh = self._create_refresh_row(user.id)
        tokens = self._issue_access(user)

        self._repo.add_audit_log(
            actor_user_id=user.id,
            action="auth.login",
            entity_id=user.id,
            new_value={
                "event": "auth.login",
                "refreshTokenId": str(refresh_row.id),
            },
            occurred_at=now,
        )
        self._repo.commit()

        return AuthSession(tokens=tokens, refresh_token=raw_refresh, user_id=user.id)

    def refresh(self, raw_refresh: str | None) -> AuthSession:
        if not raw_refresh:
            raise UnauthenticatedError("Refresh token required")

        existing = self._repo.get_refresh_by_hash(hash_refresh_token(raw_refresh))
        now = datetime.now(UTC)

        if existing is None:
            raise UnauthenticatedError("Invalid or expired refresh token")

        if existing.revoked_at is not None:
            # Reuse of a rotated/revoked token — reject (family not cascade-killed here).
            raise UnauthenticatedError("Invalid or expired refresh token")

        expires = existing.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=UTC)
        if expires <= now:
            existing.revoked_at = now
            self._repo.commit()
            raise UnauthenticatedError("Invalid or expired refresh token")

        user = self._repo.get_user_by_id(existing.user_id)
        if user is None or not user.is_active:
            existing.revoked_at = now
            self._repo.commit()
            raise UnauthenticatedError("Invalid or expired refresh token")

        new_row, new_raw = self._create_refresh_row(user.id)
        existing.revoked_at = now
        existing.replaced_by_id = new_row.id

        tokens = self._issue_access(user)
        self._repo.add_audit_log(
            actor_user_id=user.id,
            action="auth.refresh",
            entity_id=user.id,
            new_value={
                "event": "auth.refresh",
                "refreshTokenId": str(new_row.id),
                "replacedTokenId": str(existing.id),
            },
            occurred_at=now,
        )
        self._repo.commit()

        return AuthSession(tokens=tokens, refresh_token=new_raw, user_id=user.id)

    def logout(self, raw_refresh: str | None) -> None:
        if not raw_refresh:
            return

        existing = self._repo.get_refresh_by_hash(hash_refresh_token(raw_refresh))
        if existing is None:
            return

        now = datetime.now(UTC)
        if existing.revoked_at is None:
            existing.revoked_at = now
            self._repo.add_audit_log(
                actor_user_id=existing.user_id,
                action="auth.logout",
                entity_id=existing.user_id,
                new_value={
                    "event": "auth.logout",
                    "refreshTokenId": str(existing.id),
                },
                occurred_at=now,
            )
            self._repo.commit()

    def me(self, user_id: uuid.UUID) -> AuthMeResponse:
        user = self._repo.get_user_by_id(user_id)
        if user is None or not user.is_active:
            raise UnauthenticatedError("Authentication required")
        return _to_me(self._repo, user)
