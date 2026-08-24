"""Authorization helpers — Dynamic Permission Resolver (TASK-038).

Runtime authorization no longer uses a static ROLE_PERMISSIONS map.
Permissions are resolved via IAM:

    User → UserRole → Role → RolePermission → Permission

Legacy ``permissions_for_role`` remains only as a thin compatibility shim
for unit tests that still assert historical role matrices; it is not used
by the Authorization Engine or login path.
"""

from __future__ import annotations

# Historical role → permission matrix (seed source for migration 0025).
# NOT consulted by Authorization Engine at runtime.

_AGENT_PERMISSIONS: frozenset[str] = frozenset(
    {
        "complaints:create",
        "complaints:read",
        "complaints:update",
        "complaints:close",
        "escalations:read",
        "reports:read",
        "kpi:read",
        "dashboard:read",
        "attachment:create",
        "attachment:read",
        "attachment:delete",
    }
)

_SUPERVISOR_PERMISSIONS: frozenset[str] = frozenset(
    {
        *_AGENT_PERMISSIONS,
        "complaints:assign",
        "complaints:escalate",
        "complaints:close",
        "users:read",
        "users:create",
        "users:update",
        "role:read",
    }
)

_HO_SCHEDULER_PERMISSIONS: frozenset[str] = frozenset(
    {
        "complaints:read",
        "complaints:update",
        "escalations:read",
        "escalations:review",
        "reports:read",
        "kpi:read",
        "dashboard:read",
        "users:read",
        "attachment:create",
        "attachment:read",
        "attachment:delete",
    }
)

_HO_ENGINEER_PERMISSIONS: frozenset[str] = frozenset(
    {
        "complaints:read",
        "complaints:update",
        "escalations:read",
        "appointments:complete",
        "reports:read",
        "kpi:read",
        "dashboard:read",
        "attachment:create",
        "attachment:read",
        "attachment:delete",
    }
)

_ADMIN_PERMISSIONS: frozenset[str] = frozenset(
    {
        *(
            p
            for p in _SUPERVISOR_PERMISSIONS
            if p not in ("complaints:create", "complaints:close")
        ),
        "escalations:review",
        "escalations:close",
        "appointments:complete",
        "sla:read",
        "sla:manage",
        "settings:read",
        "settings:update",
        "notification:read",
        "notification:create",
        "notification:update",
        "notification:delete",
        "audit:read",
        "role:read",
        "role:create",
        "role:update",
        "role:delete",
        "permission:read",
        "permission:create",
        "permission:update",
        "permission:delete",
        "role_permission:read",
        "role_permission:update",
        "user_role:read",
        "user_role:update",
        "data_scope:read",
        "data_scope:update",
        "*",
    }
)

_VIEWER_PERMISSIONS: frozenset[str] = frozenset(
    {
        "complaints:read",
        "escalations:read",
        "reports:read",
        "kpi:read",
        "dashboard:read",
        "sla:read",
        "attachment:read",
        "notification:read",
        "audit:read",
        "role:read",
        "permission:read",
        "role_permission:read",
        "user_role:read",
        "data_scope:read",
    }
)

# Distinct business persona (BC-8/BG-018, BC-8.4) — not a Supervisor alias.
# Own-branch user membership + dashboard + F4 complaint ops parity with
# Supervisor for create/read/update/assign/escalate/close. No wildcard;
# unit/party/SoD/state AuthZ still applies at the endpoint layer.
_MANAGER_PERMISSIONS: frozenset[str] = frozenset(
    {
        "users:read",
        "users:update",
        "dashboard:read",
        "complaints:create",
        "complaints:read",
        "complaints:update",
        "complaints:assign",
        "complaints:escalate",
        "complaints:close",
    }
)

# Deprecated: seed/reference only. Authorization Engine must not use this map.
_LEGACY_ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    "AGENT": _AGENT_PERMISSIONS,
    "CS_AGENT": _AGENT_PERMISSIONS,
    "HANDLER": _AGENT_PERMISSIONS,
    "BRANCH_OFFICER": _AGENT_PERMISSIONS,
    "SUPERVISOR": _SUPERVISOR_PERMISSIONS,
    "BRANCH_SUPERVISOR": _SUPERVISOR_PERMISSIONS,
    "MANAGER": _MANAGER_PERMISSIONS,
    "HO_SCHEDULER": _HO_SCHEDULER_PERMISSIONS,
    "HEAD_OFFICE_SCHEDULER": _HO_SCHEDULER_PERMISSIONS,
    "SCHEDULER": _HO_SCHEDULER_PERMISSIONS,
    "HO_ENGINEER": _HO_ENGINEER_PERMISSIONS,
    "HEAD_OFFICE_ENGINEER": _HO_ENGINEER_PERMISSIONS,
    "ADMIN": _ADMIN_PERMISSIONS,
    "ADMINISTRATOR": _ADMIN_PERMISSIONS,
    "SUPER_ADMIN": _ADMIN_PERMISSIONS,
    "VIEWER": _VIEWER_PERMISSIONS,
}


def permissions_for_role(role_code: str | None) -> list[str]:
    """Deprecated compatibility helper — prefer PermissionResolver.

    Returns the historical seed matrix for a role code. Not used by
    Authorization Engine or AuthService at runtime.
    """
    if not role_code:
        return []
    perms = _LEGACY_ROLE_PERMISSIONS.get(role_code.upper())
    if perms is None:
        return []
    return sorted(perms)
