"""Authentication step of the Authorization Middleware pipeline (TASK-040).

Validates the Bearer JWT and builds a :class:`Principal`. Effective
permissions come from ``PermissionResolver`` (TASK-038) when the token
omits an explicit ``permissions`` claim.

Login / JWT minting is unchanged — this module only consumes tokens.
"""

from __future__ import annotations

import uuid
from typing import Annotated, Any

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.authorization.principal import Principal
from app.core.config import Settings, get_settings
from app.core.errors import UnauthenticatedError
from app.core.security import decode_access_token
from app.db.session import get_db_session
from app.modules.iam.permission_resolver import PermissionResolver

_bearer = HTTPBearer(auto_error=False)


def _as_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    return []


def authenticate_bearer(
    credentials: HTTPAuthorizationCredentials | None,
    settings: Settings,
) -> tuple[uuid.UUID, tuple[str, ...], dict[str, Any]]:
    """Validate Bearer JWT → ``(user_id, roles, payload)``.

    Does not resolve permissions — that is the next pipeline step.
    """
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthenticatedError("Bearer token required")

    try:
        payload = decode_access_token(credentials.credentials, settings)
    except ValueError as exc:
        raise UnauthenticatedError("Invalid or expired token") from exc

    subject = payload.get("sub")
    if not subject:
        raise UnauthenticatedError("Token missing subject")

    try:
        user_id = uuid.UUID(str(subject))
    except ValueError as exc:
        raise UnauthenticatedError("Token subject must be a UUID") from exc

    roles = tuple(_as_string_list(payload.get("roles")))
    return user_id, roles, payload


def resolve_principal_permissions(
    user_id: uuid.UUID,
    payload: dict[str, Any],
    session: Session,
) -> frozenset[str]:
    """Permission Resolver step — uses existing IAM cache (TASK-038).

    Login-issued tokens omit ``permissions``; resolve from DB.
    Explicit claim (tests/tooling) is honored when present.
    """
    if "permissions" in payload:
        return frozenset(_as_string_list(payload.get("permissions")))
    return PermissionResolver(session).resolve(user_id)


def get_current_principal(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    settings: Annotated[Settings, Depends(get_settings)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Principal:
    """Authentication + Permission Resolver → :class:`Principal`."""
    user_id, roles, payload = authenticate_bearer(credentials, settings)
    permissions = resolve_principal_permissions(user_id, payload, session)
    return Principal(user_id=user_id, roles=roles, permissions=permissions)
