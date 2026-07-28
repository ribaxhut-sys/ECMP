"""Authentication application service (no FastAPI imports)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING
from urllib.parse import urlencode

from sqlalchemy import select

from app.core.config import Settings
from app.core.errors import UnauthenticatedError, ValidationAppError
from app.core.i18n_messages import get_message, normalize_language, parse_accept_language
from app.core.password_policy import get_password_policy
from app.core.security import (
    create_access_token,
    generate_password_reset_token,
    generate_refresh_token,
    hash_password,
    hash_password_reset_token,
    hash_refresh_token,
    verify_password,
)
from app.models import PasswordResetToken, RefreshToken, User
from app.modules.auth.password_helpers import (
    revoke_all_refresh_tokens,
    set_user_password,
    write_password_audit,
)
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import (
    AuthMeResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    ResetPasswordRequest,
    ResetPasswordResponse,
    TokenResponse,
)
from app.modules.iam.permission_resolver import PermissionResolver
from app.modules.iam.role.models import Role
from app.modules.iam.user_role.models import UserRole

if TYPE_CHECKING:
    from fastapi import Request

    from app.modules.email import EmailService


FORGOT_PASSWORD_MESSAGE = get_message("forgot_password", "id")


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
            "preferred_language": getattr(user, "preferred_language", None) or "id",
        }
    )


class AuthService:
    def __init__(
        self,
        repository: AuthRepository,
        settings: Settings,
        email_service: EmailService | None = None,
    ) -> None:
        self._repo = repository
        self._settings = settings
        self._email = email_service

    def _policy(self):
        return get_password_policy(min_length=self._settings.password_min_length)

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

    def forgot_password(
        self,
        payload: ForgotPasswordRequest,
        *,
        request: Request | None = None,
    ) -> ForgotPasswordResponse:
        """Always return the same message — never reveal whether the email exists.

        The response message is localized from the request's ``Accept-Language``
        header only (never from the target user's stored preference), so the
        wording cannot be used to infer whether the account exists.
        """
        accept_language = None
        if request is not None:
            accept_language = parse_accept_language(
                request.headers.get("accept-language")
            )
        response_language = normalize_language(accept_language)
        response = ForgotPasswordResponse(
            message=get_message("forgot_password", response_language)
        )
        user = self._repo.get_user_by_email(payload.email)
        if user is None or not user.is_active:
            return response

        raw_token = generate_password_reset_token()
        now = datetime.now(UTC)
        expires_at = now + timedelta(
            minutes=self._settings.password_reset_token_expire_minutes
        )
        row = PasswordResetToken(
            user_id=user.id,
            token_hash=hash_password_reset_token(raw_token),
            expires_at=expires_at,
            used_at=None,
            created_at=now,
        )
        self._repo.add_password_reset_token(row)

        base = self._settings.password_reset_frontend_base_url.rstrip("/")
        reset_url = f"{base}/reset-password?{urlencode({'token': raw_token})}"

        email_language = getattr(user, "preferred_language", None) or accept_language or "id"
        if self._email is not None:
            self._email.send_password_reset(
                to_email=user.email,
                reset_url=reset_url,
                expires_at=expires_at,
                language=email_language,
            )

        write_password_audit(
            self._repo.session,
            request=request,
            event_type="password.reset_requested",
            entity_id=user.id,
            actor_id=user.id,
            new_values={"expiresAt": expires_at.isoformat()},
            commit=False,
        )
        self._repo.commit()
        return response

    def reset_password(
        self,
        payload: ResetPasswordRequest,
        *,
        request: Request | None = None,
    ) -> ResetPasswordResponse:
        token_hash = hash_password_reset_token(payload.token)
        row = self._repo.get_password_reset_by_hash(token_hash)
        now = datetime.now(UTC)

        if row is None:
            write_password_audit(
                self._repo.session,
                request=request,
                event_type="password.reset_failed",
                entity_id=None,
                actor_id=None,
                new_values={"reason": "invalid_token"},
                commit=True,
            )
            raise ValidationAppError(
                "Invalid or expired reset token",
                details={"field": "token"},
            )

        if row.used_at is not None:
            write_password_audit(
                self._repo.session,
                request=request,
                event_type="password.reset_token_reused",
                entity_id=row.user_id,
                actor_id=row.user_id,
                new_values={"tokenId": str(row.id)},
                commit=True,
            )
            raise ValidationAppError(
                "Invalid or expired reset token",
                details={"field": "token"},
            )

        expires = row.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=UTC)
        if expires <= now:
            write_password_audit(
                self._repo.session,
                request=request,
                event_type="password.reset_token_expired",
                entity_id=row.user_id,
                actor_id=row.user_id,
                new_values={"tokenId": str(row.id)},
                commit=True,
            )
            raise ValidationAppError(
                "Invalid or expired reset token",
                details={"field": "token"},
            )

        user = self._repo.get_user_by_id(row.user_id)
        if user is None or not user.is_active:
            raise ValidationAppError(
                "Invalid or expired reset token",
                details={"field": "token"},
            )

        self._policy().validate(payload.password, current_hash=user.password_hash)

        set_user_password(
            user,
            password_hash=hash_password(payload.password),
            actor_user_id=user.id,
            force_password_change=False,
        )
        row.used_at = now
        revoked = revoke_all_refresh_tokens(self._repo.session, user.id)
        write_password_audit(
            self._repo.session,
            request=request,
            event_type="password.reset_completed",
            entity_id=user.id,
            actor_id=user.id,
            new_values={
                "tokenId": str(row.id),
                "refreshTokensRevoked": revoked,
            },
            commit=False,
        )
        self._repo.commit()
        return ResetPasswordResponse()
