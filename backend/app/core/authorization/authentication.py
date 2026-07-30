"""Authentication step of the Authorization Middleware pipeline (TASK-040).

Validates the Bearer credential via the process-wide
:class:`~app.core.authorization.auth_strategy.AuthenticationStrategy`
(TASK-PLATFORM-SECMIG-P2-001) and builds a :class:`Principal`.

Login / JWT minting for ``ECMP_AUTH_MODE=dev`` is unchanged.
"""

from __future__ import annotations

import uuid
from typing import Annotated, Any

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.authorization.auth_strategy import (
    build_authentication_strategy,
    get_authentication_strategy,
)
from app.core.authorization.principal import Principal
from app.core.config import Settings, get_settings
from app.core.errors import UnauthenticatedError
from app.db.session import get_db_session
from app.modules.audit.security_events import SecurityEventType, write_security_event
from app.modules.iam.permission_resolver import PermissionResolver

_bearer = HTTPBearer(auto_error=False)


def authenticate_bearer(
    credentials: HTTPAuthorizationCredentials | None,
    settings: Settings,
) -> tuple[uuid.UUID, tuple[str, ...], dict[str, Any]]:
    """Validate Bearer → ``(user_id, roles, payload)``.

    Builds a strategy from the supplied ``settings`` so unit tests can
    supply isolated config without touching the process singleton.
    """
    strategy = build_authentication_strategy(settings)
    return strategy.extract_identity(credentials)


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
        value = payload.get("permissions")
        if value is None:
            return frozenset()
        if isinstance(value, str):
            return frozenset({value})
        if isinstance(value, list):
            return frozenset(str(item) for item in value if item is not None)
        return frozenset()
    return PermissionResolver(session).resolve(user_id)


def get_current_principal(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    settings: Annotated[Settings, Depends(get_settings)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Principal:
    """Authentication + Permission Resolver → :class:`Principal`.

    Uses the startup-selected authentication strategy. ``settings`` is
    retained for FastAPI DI compatibility with existing overrides.
    """
    del settings  # mode selected once at startup via configure_authentication
    strategy = get_authentication_strategy()
    try:
        return strategy.authenticate(
            credentials,
            session,
            request_path=request.url.path,
        )
    except UnauthenticatedError as exc:
        write_security_event(
            session,
            request=request,
            event_type=SecurityEventType.TOKEN_REJECTED,
            new_values={"reason": exc.message},
            metadata_extra={"reasonCode": "UNAUTHENTICATED"},
            commit=True,
        )
        raise
