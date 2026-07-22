"""AuthN/AuthZ dependency (ADR-007 slice phase).

Known limitation (registered in 10 Security and Access Standards): static tokens
from environment, fixed principals, DEV/CI only. 401 = authentication failure,
403 = authenticated but missing permission.

Sprint-02B (DEC-006 U-2): principals carry orgUnitId / supervisedUnitIds for
BR-002 cross-unit assignment guards.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header

from app import settings
from app.errors import ForbiddenError, UnauthenticatedError


def require_user(authorization: Annotated[str | None, Header()] = None) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UnauthenticatedError("Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    if token == settings.dev_token():
        return {
            "userId": "cs.agent.1",
            "permissions": {"cases:create", "cases:read"},
            "orgUnitId": "UNIT-01",
            "supervisedUnitIds": set(),
        }
    if token == settings.readonly_token():
        return {
            "userId": "viewer.1",
            "permissions": {"cases:read"},
            "orgUnitId": "UNIT-01",
            "supervisedUnitIds": set(),
        }
    if token == settings.noperm_token():
        # Permissionless principal: makes every documented 403 path producible/testable.
        return {
            "userId": "noperm.1",
            "permissions": set(),
            "orgUnitId": "UNIT-01",
            "supervisedUnitIds": set(),
        }
    if token == settings.supervisor_token():
        return {
            "userId": "supervisor.1",
            "permissions": {"cases:assign", "cases:read", "cases:create"},
            "orgUnitId": "UNIT-01",
            "supervisedUnitIds": {"UNIT-01"},
        }
    if token == settings.handler_token():
        return {
            "userId": "USR-2001",
            "permissions": {"cases:status", "cases:read"},
            "orgUnitId": "UNIT-01",
            "supervisedUnitIds": set(),
        }
    if token == settings.foreign_supervisor_token():
        # Supervisor of a different unit — exercises BR-002 cross-unit 403.
        return {
            "userId": "supervisor.other",
            "permissions": {"cases:assign", "cases:read"},
            "orgUnitId": "UNIT-99",
            "supervisedUnitIds": {"UNIT-99"},
        }
    raise UnauthenticatedError("Invalid token")


def require_perm(user: dict, perm: str) -> None:
    if perm not in user.get("permissions", set()):
        raise ForbiddenError(f"Missing permission: {perm}")


def need(perm: str):
    """Dependency factory: authentication + permission in one declaration.

    Structural enforcement (a route cannot forget the check) vs imperative
    require_perm calls inside handlers.
    """

    def dependency(user: Annotated[dict, Depends(require_user)]) -> dict:
        require_perm(user, perm)
        return user

    return dependency
