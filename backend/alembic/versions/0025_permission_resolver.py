"""Seed runtime permission matrix + backfill user_roles (TASK-038).

Revision ID: 0025_permission_resolver
Revises: 0024_data_scopes
Create Date: 2026-07-24

Seeds Authorization Engine permission codes (aligned with former static
ROLE_PERMISSIONS), role↔permission matrix rows, additional operational
roles, and backfills user_roles from users.role_id.

Does not implement Data Scope filtering.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0025_permission_resolver"
down_revision: Union[str, None] = "0024_data_scopes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Extra roles used by JWT/role gates (beyond TASK-033 baseline five).
_EXTRA_ROLES: tuple[tuple[str, str, str], ...] = (
    ("CS_AGENT", "CS Agent", "Alias of Agent"),
    ("HANDLER", "Handler", "Alias of Agent"),
    ("BRANCH_OFFICER", "Branch Officer", "Alias of Agent"),
    ("BRANCH_SUPERVISOR", "Branch Supervisor", "Alias of Supervisor"),
    ("HO_SCHEDULER", "HO Scheduler", "Head Office Scheduler"),
    ("HEAD_OFFICE_SCHEDULER", "Head Office Scheduler", "Alias of HO Scheduler"),
    ("SCHEDULER", "Scheduler", "Alias of HO Scheduler"),
    ("HO_ENGINEER", "HO Engineer", "Head Office Engineer"),
    ("HEAD_OFFICE_ENGINEER", "Head Office Engineer", "Alias of HO Engineer"),
    ("ADMINISTRATOR", "Administrator alias", "Alias of Admin"),
)

_AGENT_PERMS: tuple[str, ...] = (
    "complaints:create",
    "complaints:read",
    "complaints:update",
    "escalations:read",
    "reports:read",
    "kpi:read",
    "dashboard:read",
    "attachment:create",
    "attachment:read",
    "attachment:delete",
)

_SUPERVISOR_PERMS: tuple[str, ...] = (
    *_AGENT_PERMS,
    "complaints:assign",
    "complaints:escalate",
    "complaints:close",
    "users:read",
    "users:create",
    "users:update",
)

_HO_SCHEDULER_PERMS: tuple[str, ...] = (
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
)

_HO_ENGINEER_PERMS: tuple[str, ...] = (
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
)

_ADMIN_PERMS: tuple[str, ...] = (
    *_SUPERVISOR_PERMS,
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
)

_VIEWER_PERMS: tuple[str, ...] = (
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
)

# role_code → permission codes
_ROLE_MATRIX: dict[str, tuple[str, ...]] = {
    "AGENT": _AGENT_PERMS,
    "CS_AGENT": _AGENT_PERMS,
    "HANDLER": _AGENT_PERMS,
    "BRANCH_OFFICER": _AGENT_PERMS,
    "SUPERVISOR": _SUPERVISOR_PERMS,
    "BRANCH_SUPERVISOR": _SUPERVISOR_PERMS,
    "HO_SCHEDULER": _HO_SCHEDULER_PERMS,
    "HEAD_OFFICE_SCHEDULER": _HO_SCHEDULER_PERMS,
    "SCHEDULER": _HO_SCHEDULER_PERMS,
    "HO_ENGINEER": _HO_ENGINEER_PERMS,
    "HEAD_OFFICE_ENGINEER": _HO_ENGINEER_PERMS,
    "ADMIN": _ADMIN_PERMS,
    "ADMINISTRATOR": _ADMIN_PERMS,
    "SUPER_ADMIN": _ADMIN_PERMS,
    "VIEWER": _VIEWER_PERMS,
}

_PERMISSION_META: dict[str, tuple[str, str, str]] = {
    "complaints:create": ("Complaints Create", "complaints", "Create complaints"),
    "complaints:read": ("Complaints Read", "complaints", "Read complaints"),
    "complaints:update": ("Complaints Update", "complaints", "Update complaints"),
    "complaints:assign": ("Complaints Assign", "complaints", "Assign complaints"),
    "complaints:escalate": ("Complaints Escalate", "complaints", "Escalate complaints"),
    "complaints:close": ("Complaints Close", "complaints", "Close complaints"),
    "escalations:read": ("Escalations Read", "escalations", "Read escalations"),
    "escalations:review": ("Escalations Review", "escalations", "Review escalations"),
    "escalations:close": ("Escalations Close", "escalations", "Close escalations"),
    "appointments:complete": (
        "Appointments Complete",
        "appointments",
        "Complete appointments / final resolution",
    ),
    "reports:read": ("Reports Read", "reports", "Read reports"),
    "kpi:read": ("KPI Read", "kpi", "Read KPI summary"),
    "dashboard:read": ("Dashboard Read", "dashboard", "Read dashboard summary"),
    "users:read": ("Users Read", "users", "Read users"),
    "users:create": ("Users Create", "users", "Create users"),
    "users:update": ("Users Update", "users", "Update users"),
    "sla:read": ("SLA Read", "sla", "Read SLA policies/records"),
    "sla:manage": ("SLA Manage", "sla", "Manage SLA policies"),
    "settings:read": ("Settings Read", "settings", "Read settings"),
    "settings:update": ("Settings Update", "settings", "Update settings"),
    "attachment:create": ("Attachment Create", "attachment", "Upload attachments"),
    "attachment:read": ("Attachment Read", "attachment", "Read attachments"),
    "attachment:delete": ("Attachment Delete", "attachment", "Delete attachments"),
    "notification:read": ("Notification Read", "notification", "Read notifications"),
    "notification:create": (
        "Notification Create",
        "notification",
        "Create notifications",
    ),
    "notification:update": (
        "Notification Update",
        "notification",
        "Update notifications",
    ),
    "notification:delete": (
        "Notification Delete",
        "notification",
        "Delete notifications",
    ),
    "audit:read": ("Audit Read", "audit", "Read audit logs"),
    "role:read": ("Role Read", "role", "Read roles"),
    "role:create": ("Role Create", "role", "Create roles"),
    "role:update": ("Role Update", "role", "Update roles"),
    "role:delete": ("Role Delete", "role", "Delete roles"),
    "permission:read": ("Permission Read", "permission", "Read permissions"),
    "permission:create": ("Permission Create", "permission", "Create permissions"),
    "permission:update": ("Permission Update", "permission", "Update permissions"),
    "permission:delete": ("Permission Delete", "permission", "Delete permissions"),
    "role_permission:read": (
        "Role Permission Read",
        "role_permission",
        "Read role↔permission matrix",
    ),
    "role_permission:update": (
        "Role Permission Update",
        "role_permission",
        "Update role↔permission matrix",
    ),
    "user_role:read": ("User Role Read", "user_role", "Read user↔role assignments"),
    "user_role:update": (
        "User Role Update",
        "user_role",
        "Update user↔role assignments",
    ),
    "data_scope:read": ("Data Scope Read", "data_scope", "Read data scopes"),
    "data_scope:update": ("Data Scope Update", "data_scope", "Update data scopes"),
    "*": ("Wildcard", "system", "All permissions"),
}


def _all_permission_codes() -> list[str]:
    codes: set[str] = set()
    for perms in _ROLE_MATRIX.values():
        codes.update(perms)
    return sorted(codes)


def upgrade() -> None:
    conn = op.get_bind()

    for code, name, description in _EXTRA_ROLES:
        conn.execute(
            sa.text(
                """
                INSERT INTO roles (
                    id, code, name, description,
                    is_system, is_active, created_at, updated_at
                )
                VALUES (
                    gen_random_uuid(), :code, :name, :description,
                    true, true, now(), now()
                )
                ON CONFLICT (code) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = COALESCE(roles.description, EXCLUDED.description),
                    is_system = true,
                    is_active = true,
                    deleted_at = NULL,
                    updated_at = now()
                """
            ),
            {"code": code, "name": name, "description": description},
        )

    for code in _all_permission_codes():
        name, module, description = _PERMISSION_META.get(
            code,
            (code, code.split(":", 1)[0] if ":" in code else "system", code),
        )
        conn.execute(
            sa.text(
                """
                INSERT INTO permissions (
                    id, code, name, module, description,
                    is_system, is_active, created_at, updated_at
                )
                VALUES (
                    gen_random_uuid(), :code, :name, :module, :description,
                    true, true, now(), now()
                )
                ON CONFLICT (code) DO UPDATE SET
                    name = EXCLUDED.name,
                    module = EXCLUDED.module,
                    description = COALESCE(permissions.description, EXCLUDED.description),
                    is_system = true,
                    is_active = true,
                    deleted_at = NULL,
                    updated_at = now()
                """
            ),
            {
                "code": code,
                "name": name,
                "module": module,
                "description": description,
            },
        )

    for role_code, perm_codes in _ROLE_MATRIX.items():
        for perm_code in perm_codes:
            conn.execute(
                sa.text(
                    """
                    INSERT INTO role_permissions (id, role_id, permission_id, created_at)
                    SELECT gen_random_uuid(), r.id, p.id, now()
                    FROM roles r
                    CROSS JOIN permissions p
                    WHERE r.code = :role_code
                      AND r.deleted_at IS NULL
                      AND p.code = :perm_code
                      AND p.deleted_at IS NULL
                      AND NOT EXISTS (
                        SELECT 1 FROM role_permissions rp
                        WHERE rp.role_id = r.id AND rp.permission_id = p.id
                      )
                    """
                ),
                {"role_code": role_code, "perm_code": perm_code},
            )

    conn.execute(
        sa.text(
            """
            INSERT INTO user_roles (id, user_id, role_id, created_at)
            SELECT gen_random_uuid(), u.id, u.role_id, now()
            FROM users u
            WHERE u.deleted_at IS NULL
              AND u.role_id IS NOT NULL
              AND EXISTS (
                SELECT 1 FROM roles r
                WHERE r.id = u.role_id AND r.deleted_at IS NULL
              )
              AND NOT EXISTS (
                SELECT 1 FROM user_roles ur
                WHERE ur.user_id = u.id AND ur.role_id = u.role_id
              )
            """
        )
    )


def downgrade() -> None:
    # Leave seeded permissions/roles/matrix/user_roles — may be live-referenced.
    pass
