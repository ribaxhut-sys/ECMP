"""Revoke complaints:create from ADMIN aliases (owner: Admin may not create).

Revision ID: 0074_admin_no_complaint_create
Revises: 0073_queue_customers_perms
Create Date: 2026-08-13

Admin keeps every other operational grant (including ``*`` and
``complaints:escalate``) but must not register WP or internal complaints.
Wildcard ``*`` is separately excluded from granting ``complaints:create`` in
``Principal.has_permission`` / FE ``hasPermission`` — deleting the row alone
would not be enough.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0074_admin_no_complaint_create"
down_revision: Union[str, None] = "0073_queue_customers_perms"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_ADMIN_ROLE_CODES: tuple[str, ...] = ("ADMIN", "ADMINISTRATOR", "SUPER_ADMIN")
_PERM = "complaints:create"


def upgrade() -> None:
    conn = op.get_bind()
    for role_code in _ADMIN_ROLE_CODES:
        conn.execute(
            sa.text(
                """
                DELETE FROM role_permissions rp
                USING roles r, permissions p
                WHERE rp.role_id = r.id
                  AND rp.permission_id = p.id
                  AND r.code = :role_code
                  AND p.code = :perm_code
                """
            ),
            {"role_code": role_code, "perm_code": _PERM},
        )


def downgrade() -> None:
    conn = op.get_bind()
    for role_code in _ADMIN_ROLE_CODES:
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
            {"role_code": role_code, "perm_code": _PERM},
        )
