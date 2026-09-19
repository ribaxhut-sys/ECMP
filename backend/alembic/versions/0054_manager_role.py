"""Seed MANAGER role (UM-BUG-007 / BC-8.4 branch manager persona).

Revision ID: 0054_manager_role
Revises: 0053_cm_b1_decided_by
Create Date: 2026-08-07

Manager is a documented, distinct business persona (BR-CM-CAT-001 BC-8/BG-018,
BC-8.4 — operational closed set = Complaint Officer, Supervisor, Manager),
listed in the FRD Administration Role Access Matrix as a target role whose
delivery was deferred (DL-068). This seeds the role and its first concrete
capability: users:read + users:update, scoped to the Manager's own branch by
the application layer (see gates.py require_user_status_update and
users/router.py). Not a Supervisor alias — no operational complaint
permissions (assign/escalate/close) are granted here; those were never
specified for Manager and are out of scope for this change.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0054_manager_role"
down_revision: Union[str, None] = "0053_cm_b1_decided_by"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_MANAGER_PERMS: tuple[str, ...] = (
    "users:read",
    "users:update",
)


def upgrade() -> None:
    conn = op.get_bind()

    conn.execute(
        sa.text(
            """
            INSERT INTO roles (
                id, code, name, description,
                is_system, is_active, created_at, updated_at
            )
            VALUES (
                gen_random_uuid(), 'MANAGER', 'Manager',
                'Branch manager persona (BC-8.4) — manages own-branch user membership',
                true, true, now(), now()
            )
            ON CONFLICT (code) DO UPDATE SET
                name = EXCLUDED.name,
                is_system = true,
                is_active = true,
                deleted_at = NULL,
                updated_at = now()
            """
        )
    )

    for perm_code in _MANAGER_PERMS:
        conn.execute(
            sa.text(
                """
                INSERT INTO role_permissions (id, role_id, permission_id, created_at)
                SELECT gen_random_uuid(), r.id, p.id, now()
                FROM roles r
                CROSS JOIN permissions p
                WHERE r.code = 'MANAGER'
                  AND p.code = :perm_code
                  AND r.deleted_at IS NULL
                  AND p.deleted_at IS NULL
                  AND NOT EXISTS (
                    SELECT 1 FROM role_permissions rp
                    WHERE rp.role_id = r.id AND rp.permission_id = p.id
                  )
                """
            ),
            {"perm_code": perm_code},
        )


def downgrade() -> None:
    # Non-destructive — do not strip a role/grants that may be in use.
    pass
