"""Repair ADMIN role_permissions matrix (TD-OPS-003).

Revision ID: 0044_admin_rbac_repair
Revises: 0043_cm_batch1_foundation
Create Date: 2026-07-29

Root cause observed in local Docker: role code ADMIN had 0 grants while
aliases ADMINISTRATOR / SUPER_ADMIN retained the 0039 matrix. golive_admin
uses primary role ADMIN → /me permissions=[] → CM APIs 403.

Non-destructive: inserts missing ADMIN (and alias) role_permission links
from the canonical seed matrix. Does not delete live custom grants.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0044_admin_rbac_repair"
down_revision: Union[str, None] = "0043_cm_batch1_foundation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Canonical ADMIN matrix (aligned with 0039_admin_rbac_repair).
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
