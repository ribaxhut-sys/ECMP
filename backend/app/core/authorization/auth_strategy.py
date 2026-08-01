"""Authentication strategies (TASK-PLATFORM-SECMIG-P2-001).

Mode selection happens once via ``configure_authentication`` at startup.
Request handlers use ``get_authentication_strategy`` — no scattered mode checks.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Any

from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.authorization.jwks_cache import JwksCache
from app.core.authorization.jwt_validator import JwtValidator
from app.core.authorization.principal import Principal
from app.core.authorization.role_mapper import RoleMapper
from app.core.config import Settings
from app.core.errors import ForbiddenError, UnauthenticatedError
from app.core.security import decode_access_token
from app.models import User
from app.modules.iam.permission_resolver import PermissionResolver
from app.core.user_messages import m

# Paths allowed while ``force_password_change`` is true (dev mode only).
_FORCE_PASSWORD_CHANGE_ALLOWED_PATHS = frozenset(
    {
        "/api/v1/auth/me",
        "/api/v1/auth/logout",
        "/api/v1/users/me/change-password",
    }
)

_strategy: AuthenticationStrategy | None = None


def _as_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    return []


class AuthenticationStrategy(ABC):
    """Authenticate a Bearer credential into a :class:`Principal`."""

    @abstractmethod
    def authenticate(
        self,
        credentials: HTTPAuthorizationCredentials | None,
        session: Session,
        *,
        request_path: str | None = None,
    ) -> Principal:
        raise NotImplementedError

    @abstractmethod
    def extract_identity(
        self,
        credentials: HTTPAuthorizationCredentials | None,
    ) -> tuple[uuid.UUID, tuple[str, ...], dict[str, Any]]:
        """Return ``(user_id, roles, payload)`` for low-level callers/tests."""
        raise NotImplementedError


class DevAuthenticationStrategy(AuthenticationStrategy):
    """Existing HS256 foundation JWT path (lab / CI default)."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def extract_identity(
        self,
        credentials: HTTPAuthorizationCredentials | None,
    ) -> tuple[uuid.UUID, tuple[str, ...], dict[str, Any]]:
        if credentials is None or credentials.scheme.lower() != "bearer":
            raise UnauthenticatedError(m("auth.bearer_required"))

        try:
            payload = decode_access_token(credentials.credentials, self._settings)
        except ValueError as exc:
            raise UnauthenticatedError(m("auth.invalid_token")) from exc

        subject = payload.get("sub")
        if not subject:
            raise UnauthenticatedError(m("auth.token_missing_subject"))

        try:
            user_id = uuid.UUID(str(subject))
        except ValueError as exc:
            raise UnauthenticatedError(m("auth.token_subject_must_be_uuid")) from exc

        roles = tuple(_as_string_list(payload.get("roles")))
        return user_id, roles, payload

    def authenticate(
        self,
        credentials: HTTPAuthorizationCredentials | None,
        session: Session,
        *,
        request_path: str | None = None,
    ) -> Principal:
        user_id, roles, payload = self.extract_identity(credentials)
        if "permissions" in payload:
            permissions = frozenset(_as_string_list(payload.get("permissions")))
        else:
            permissions = PermissionResolver(session).resolve(user_id)
        force = _load_force_password_change(session, user_id)
        principal = Principal(
            user_id=user_id,
            roles=roles,
            permissions=permissions,
            force_password_change=force,
            sid=_optional_str(payload.get("sid")),
            org_unit_id=_optional_str(
                payload.get("orgUnitId") or payload.get("org_unit_id")
            ),
        )
        if force and request_path and request_path not in _FORCE_PASSWORD_CHANGE_ALLOWED_PATHS:
            raise ForbiddenError(
                m("auth.password_change_required"),
                code="PASSWORD_CHANGE_REQUIRED",
                details={"forcePasswordChange": True},
            )
        return principal


class JwtAuthenticationStrategy(AuthenticationStrategy):
    """IdP RS256 access-token path (SEC-AUTH-001 / SEC-MIG Phase 2)."""

    def __init__(
        self,
        settings: Settings,
        *,
        validator: JwtValidator | None = None,
        role_mapper: RoleMapper | None = None,
        jwks_cache: JwksCache | None = None,
    ) -> None:
        self._settings = settings
        self._role_mapper = role_mapper or RoleMapper()
        if validator is not None:
            self._validator = validator
        else:
            issuer = (settings.oidc_issuer or "").strip()
            audience = (settings.oidc_audience or "").strip()
            jwks_url = (settings.oidc_jwks_url or "").strip()
            cache = jwks_cache or JwksCache(
                jwks_url,
                ttl_seconds=settings.oidc_jwks_cache_ttl_seconds,
            )
            self._validator = JwtValidator(
                issuer=issuer,
                audience=audience,
                jwks_cache=cache,
            )

    def extract_identity(
        self,
        credentials: HTTPAuthorizationCredentials | None,
    ) -> tuple[uuid.UUID, tuple[str, ...], dict[str, Any]]:
        if credentials is None or credentials.scheme.lower() != "bearer":
            raise UnauthenticatedError(m("auth.bearer_required"))

        try:
            payload = self._validator.validate(credentials.credentials)
        except ValueError as exc:
            raise UnauthenticatedError(m("auth.invalid_token")) from exc

        subject = payload.get("sub")
        if not subject:
            raise UnauthenticatedError(m("auth.token_missing_subject"))

        try:
            user_id = uuid.UUID(str(subject))
        except ValueError as exc:
            raise UnauthenticatedError(m("auth.token_subject_must_be_uuid")) from exc

        idp_roles = _as_string_list(payload.get("roles"))
        roles = self._role_mapper.map_many(idp_roles)
        return user_id, roles, payload

    def authenticate(
        self,
        credentials: HTTPAuthorizationCredentials | None,
        session: Session,
        *,
        request_path: str | None = None,
    ) -> Principal:
        del request_path  # no force-password gate for IdP principals
        user_id, roles, payload = self.extract_identity(credentials)
        # Permissions never from JWT — Core Platform matrix only (ADR-008).
        permissions = PermissionResolver(session).resolve_for_role_codes(roles)
        return Principal(
            user_id=user_id,
            roles=roles,
            permissions=permissions,
            force_password_change=False,
            sid=_optional_str(payload.get("sid")),
            org_unit_id=_optional_str(
                payload.get("orgUnitId") or payload.get("org_unit_id")
            ),
        )


def build_authentication_strategy(settings: Settings) -> AuthenticationStrategy:
    """Single place that branches on ``ECMP_AUTH_MODE``."""
    mode = (settings.ecmp_auth_mode or "dev").strip().lower()
    if mode == "jwt":
        return JwtAuthenticationStrategy(settings)
    if mode == "dev":
        return DevAuthenticationStrategy(settings)
    raise ValueError(f"Unsupported ECMP_AUTH_MODE '{settings.ecmp_auth_mode}'")


def configure_authentication(settings: Settings) -> AuthenticationStrategy:
    """Select and store the process-wide strategy (call once at startup)."""
    global _strategy
    _strategy = build_authentication_strategy(settings)
    return _strategy


def get_authentication_strategy() -> AuthenticationStrategy:
    """Return the strategy configured at startup (lazy-init from settings if needed)."""
    global _strategy
    if _strategy is None:
        from app.core.config import get_settings

        _strategy = build_authentication_strategy(get_settings())
    return _strategy


def reset_authentication_strategy(
    strategy: AuthenticationStrategy | None = None,
) -> None:
    """Test helper — clear or replace the process-wide strategy."""
    global _strategy
    _strategy = strategy


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _load_force_password_change(session: Session, user_id: uuid.UUID) -> bool:
    value = session.scalar(
        select(User.force_password_change).where(
            User.id == user_id,
            User.deleted_at.is_(None),
        )
    )
    return bool(value)
