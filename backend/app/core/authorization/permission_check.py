"""Permission check step of the Authorization Middleware pipeline (TASK-040).

Runs after Authentication + Permission Resolver. Does not touch
PermissionResolver internals — only evaluates the resolved Principal.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends

from app.core.authorization.authentication import get_current_principal
from app.core.authorization.principal import Principal
from app.core.errors import PermissionDeniedError


def check_permissions(principal: Principal, *required: str) -> None:
    """Raise :class:`PermissionDeniedError` when any required permission is missing."""
    missing = [perm for perm in required if not principal.has_permission(perm)]
    if missing:
        raise PermissionDeniedError(
            "Permission denied",
            details={"missingPermissions": missing},
        )


def check_roles(principal: Principal, *roles: str) -> None:
    """Raise :class:`PermissionDeniedError` when principal has none of the roles."""
    if not principal.has_any_role(*roles):
        raise PermissionDeniedError(
            "Permission denied",
            details={"requiredRoles": list(roles)},
        )


def require_permissions(*required: str) -> Callable[..., Principal]:
    """Dependency factory: Authentication → Permission Resolver → Permission Check."""

    def _dependency(
        principal: Annotated[Principal, Depends(get_current_principal)],
    ) -> Principal:
        check_permissions(principal, *required)
        return principal

    return _dependency


def require_roles(*roles: str) -> Callable[..., Principal]:
    """Dependency factory: Authentication → Permission Resolver → Role Check."""

    def _dependency(
        principal: Annotated[Principal, Depends(get_current_principal)],
    ) -> Principal:
        check_roles(principal, *roles)
        return principal

    return _dependency
