"""Repair ADMIN role_permissions matrix (R6-02 / Task 6).

Revision ID: 0039_admin_rbac_repair
Revises: 0038_preferred_language
Create Date: 2026-07-28

Non-destructive: inserts missing ADMIN (and alias) role_permission links
from the canonical seed matrix. Does not delete live custom grants.
Removes duplicate (role_id, permission_id) rows if any exist.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0039_admin_rbac_repair"
down_revision: Union[str, None] = "0038_preferred_language"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Canonical ADMIN matrix (aligned with 0025_permission_resolver + 0037).
_ADMIN_PERMS: tuple[str, ...] = (
    "complaints:create",
    "complaints:read",
    "complaints:update",
    "complaints:assign",
    "complaints:escalate",
    "complaints:close",
    "escalations:read",
    "reports:read",
    "kpi:read",
    "dashboard:read",
    "attachment:create",
    "attachment:read",
    "attachment:delete",
    "users:read",
    "users:create",
    "users:update",
    "users:reset_password",
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
    "timeline:read",
    "timeline:create",
    "*",
)

_ADMIN_ROLE_CODES: tuple[str, ...] = ("ADMIN", "ADMINISTRATOR", "SUPER_ADMIN")


def upgrade() -> None:
    conn = op.get_bind()

    # Drop exact duplicate role_permission rows (keep lowest id).
    conn.execute(
        sa.text(
            """
            DELETE FROM role_permissions rp
            USING role_permissions rp2
            WHERE rp.role_id = rp2.role_id
              AND rp.permission_id = rp2.permission_id
              AND rp.id > rp2.id
            """
        )
    )

    # Drop orphan mappings whose permission or role no longer exists.
    conn.execute(
        sa.text(
            """
            DELETE FROM role_permissions rp
            WHERE NOT EXISTS (
                SELECT 1 FROM permissions p WHERE p.id = rp.permission_id
            )
            OR NOT EXISTS (
                SELECT 1 FROM roles r WHERE r.id = rp.role_id
            )
            """
        )
    )

    for role_code in _ADMIN_ROLE_CODES:
        for perm_code in _ADMIN_PERMS:
            conn.execute(
                sa.text(
                    """
                    INSERT INTO role_permissions (id, role_id, permission_id, created_at)
                    SELECT gen_random_uuid(), r.id, p.id, now()
                    FROM roles r
                    CROSS JOIN permissions p
                    WHERE r.code = :role_code
                      AND p.code = :perm_code
                      AND r.deleted_at IS NULL
                      AND p.deleted_at IS NULL
                      AND NOT EXISTS (
                        SELECT 1 FROM role_permissions rp
                        WHERE rp.role_id = r.id AND rp.permission_id = p.id
                      )
                    """
                ),
                {"role_code": role_code, "perm_code": perm_code},
            )


def downgrade() -> None:
    # Non-destructive repair — do not strip permissions on downgrade.
    pass
