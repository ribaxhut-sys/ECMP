"""Permission check step of the Authorization Middleware pipeline (TASK-040).

Runs after Authentication + Permission Resolver. Does not touch
PermissionResolver internals — only evaluates the resolved Principal.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.authorization.authentication import get_current_principal
from app.core.authorization.principal import Principal
from app.core.errors import PermissionDeniedError
from app.core.user_messages import m
from app.db.session import get_db_session
from app.modules.audit.security_events import SecurityEventType, write_security_event


def check_permissions(principal: Principal, *required: str) -> None:
    """Raise :class:`PermissionDeniedError` when any required permission is missing."""
    missing = [perm for perm in required if not principal.has_permission(perm)]
    if missing:
        raise PermissionDeniedError(
            m("common.forbidden"),
            details={"missingPermissions": missing},
        )


def check_roles(principal: Principal, *roles: str) -> None:
    """Raise :class:`PermissionDeniedError` when principal has none of the roles."""
    if not principal.has_any_role(*roles):
        raise PermissionDeniedError(
            m("common.forbidden"),
            details={"requiredRoles": list(roles)},
        )


def require_permissions(*required: str) -> Callable[..., Principal]:
    """Dependency factory: Authentication → Permission Resolver → Permission Check."""

    def _dependency(
        request: Request,
        principal: Annotated[Principal, Depends(get_current_principal)],
        session: Annotated[Session, Depends(get_db_session)],
    ) -> Principal:
        try:
            check_permissions(principal, *required)
        except PermissionDeniedError as exc:
            write_security_event(
                session,
                request=request,
                event_type=SecurityEventType.PERMISSION_DENIED,
                actor_id=principal.user_id,
                entity_id=principal.user_id,
                new_values=dict(exc.details or {}),
                metadata_extra={"reasonCode": "FORBIDDEN"},
                commit=True,
            )
            raise
        return principal

    return _dependency


def require_roles(*roles: str) -> Callable[..., Principal]:
    """Dependency factory: Authentication → Permission Resolver → Role Check."""

    def _dependency(
        request: Request,
        principal: Annotated[Principal, Depends(get_current_principal)],
        session: Annotated[Session, Depends(get_db_session)],
    ) -> Principal:
        try:
            check_roles(principal, *roles)
        except PermissionDeniedError as exc:
            write_security_event(
                session,
                request=request,
                event_type=SecurityEventType.PERMISSION_DENIED,
                actor_id=principal.user_id,
                entity_id=principal.user_id,
                new_values=dict(exc.details or {}),
                metadata_extra={"reasonCode": "FORBIDDEN", "check": "roles"},
                commit=True,
            )
            raise
        return principal

    return _dependency
