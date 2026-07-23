"""JWT authentication and RBAC-ready authorization dependencies."""

from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Annotated, Any

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import Settings, get_settings
from app.core.errors import ForbiddenError, UnauthenticatedError
from app.core.security import decode_access_token

_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True, slots=True)
class Principal:
    """Authenticated caller identity (JWT claims)."""

    user_id: uuid.UUID
    roles: tuple[str, ...] = ()
    permissions: frozenset[str] = field(default_factory=frozenset)

    def has_permission(self, permission: str) -> bool:
        return "*" in self.permissions or permission in self.permissions

    def has_any_role(self, *roles: str) -> bool:
        mine = {role.upper() for role in self.roles}
        return bool(mine & {role.upper() for role in roles})


def _as_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    return []


def get_current_principal(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> Principal:
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

    permissions = frozenset(_as_string_list(payload.get("permissions")))
    roles = tuple(_as_string_list(payload.get("roles")))
    return Principal(user_id=user_id, roles=roles, permissions=permissions)


def require_permissions(*required: str) -> Callable[..., Principal]:
    """Dependency factory: JWT + all listed permissions (RBAC-ready)."""

    def _dependency(
        principal: Annotated[Principal, Depends(get_current_principal)],
    ) -> Principal:
        missing = [perm for perm in required if not principal.has_permission(perm)]
        if missing:
            raise ForbiddenError(
                f"Missing permission(s): {', '.join(missing)}",
            )
        return principal

    return _dependency


def require_roles(*roles: str) -> Callable[..., Principal]:
    """Dependency factory: JWT + at least one of the listed roles."""

    def _dependency(
        principal: Annotated[Principal, Depends(get_current_principal)],
    ) -> Principal:
        if not principal.has_any_role(*roles):
            raise ForbiddenError(
                f"Requires one of role(s): {', '.join(roles)}",
            )
        return principal

    return _dependency


def require_supervisor_assign(
    principal: Annotated[
        Principal, Depends(require_permissions("complaints:assign"))
    ],
) -> Principal:
    """Assign endpoint gate: permission complaints:assign + SUPERVISOR role."""
    if not principal.has_any_role("SUPERVISOR"):
        raise ForbiddenError("Only Supervisor can assign complaints")
    return principal


def require_supervisor_escalate(
    principal: Annotated[
        Principal, Depends(require_permissions("complaints:escalate"))
    ],
) -> Principal:
    """Escalate endpoint gate: permission complaints:escalate + SUPERVISOR role."""
    if not principal.has_any_role("SUPERVISOR", "BRANCH_SUPERVISOR"):
        raise ForbiddenError("Only Supervisor can escalate complaints")
    return principal


_ESCALATION_REVIEW_ROLES = (
    "HO_SCHEDULER",
    "HEAD_OFFICE_SCHEDULER",
    "SCHEDULER",
    "ADMIN",
    "ADMINISTRATOR",
)


def require_escalation_review(
    principal: Annotated[
        Principal, Depends(require_permissions("escalations:review"))
    ],
) -> Principal:
    """API-303/304 gate: escalations:review + HO Scheduler or Admin."""
    if not principal.has_any_role(*_ESCALATION_REVIEW_ROLES):
        raise ForbiddenError(
            "Only Head Office Scheduler or Admin can review escalations"
        )
    return principal


_APPOINTMENT_COMPLETE_ROLES = (
    "HO_ENGINEER",
    "HEAD_OFFICE_ENGINEER",
    "ADMIN",
    "ADMINISTRATOR",
)


def require_appointment_complete(
    principal: Annotated[
        Principal, Depends(require_permissions("appointments:complete"))
    ],
) -> Principal:
    """API-308 gate: appointments:complete + HO Engineer or Admin."""
    if not principal.has_any_role(*_APPOINTMENT_COMPLETE_ROLES):
        raise ForbiddenError(
            "Only Head Office Engineer or Admin can complete appointments"
        )
    return principal


def require_final_resolution(
    principal: Annotated[
        Principal, Depends(require_permissions("appointments:complete"))
    ],
) -> Principal:
    """API-310 gate: appointments:complete + HO Engineer or Admin."""
    if not principal.has_any_role(*_APPOINTMENT_COMPLETE_ROLES):
        raise ForbiddenError(
            "Only Head Office Engineer or Admin can submit final resolution"
        )
    return principal


CurrentPrincipal = Annotated[Principal, Depends(get_current_principal)]
