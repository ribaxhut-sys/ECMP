"""AuthN/AuthZ dependency (ADR-007 slice phase).

Known limitation (registered in 10 Security and Access Standards): static tokens
from environment, fixed principals, DEV/CI only. 401 = failed authentication,
403 = authenticated but missing permission.
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
        return {"userId": "cs.agent.1", "permissions": {"cases:create", "cases:read"}}
    if token == settings.readonly_token():
        return {"userId": "viewer.1", "permissions": {"cases:read"}}
    if token == settings.noperm_token():
        # Permissionless principal: makes every documented 403 path producible/testable.
        return {"userId": "noperm.1", "permissions": set()}
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
