"""Role → permission resolution for access-token claims.

Foundation mapping for complaint-service roles. Role/permission SoT remains
Core Platform (ADR-008); this table bridges until API-062 persistence exists.
"""

from __future__ import annotations

_AGENT_PERMISSIONS: frozenset[str] = frozenset(
    {
        "complaints:create",
        "complaints:read",
        "complaints:update",
        "reports:read",
    }
)

_SUPERVISOR_PERMISSIONS: frozenset[str] = frozenset(
    {
        *_AGENT_PERMISSIONS,
        "complaints:assign",
        "complaints:escalate",
        "users:read",
        "users:create",
        "users:update",
    }
)

_ADMIN_PERMISSIONS: frozenset[str] = frozenset(
    {
        *_SUPERVISOR_PERMISSIONS,
        "*",
    }
)

_VIEWER_PERMISSIONS: frozenset[str] = frozenset(
    {
        "complaints:read",
        "reports:read",
    }
)

ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    "AGENT": _AGENT_PERMISSIONS,
    "CS_AGENT": _AGENT_PERMISSIONS,
    "HANDLER": _AGENT_PERMISSIONS,
    "SUPERVISOR": _SUPERVISOR_PERMISSIONS,
    "ADMIN": _ADMIN_PERMISSIONS,
    "ADMINISTRATOR": _ADMIN_PERMISSIONS,
    "VIEWER": _VIEWER_PERMISSIONS,
}


def permissions_for_role(role_code: str | None) -> list[str]:
    if not role_code:
        return []
    perms = ROLE_PERMISSIONS.get(role_code.upper())
    if perms is None:
        return []
    return sorted(perms)
