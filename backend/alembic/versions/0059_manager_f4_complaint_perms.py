"""Grant MANAGER F4 complaint capabilities (parity with Supervisor ops set).

Revision ID: 0059_manager_f4_complaint_perms
Revises: 0058_cm_case_f4_owner_acceptance
Create Date: 2026-08-08

F4: Manager may create/read/update/assign/escalate/close using existing
permission codes. Permission alone does not bypass unit/party/SoD/state
AuthZ (no wildcard / admin bypass).
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0059_manager_f4_complaint_perms"
down_revision: Union[str, None] = "0058_cm_case_f4_owner_acceptance"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_MANAGER_F4_PERMS: tuple[str, ...] = (
    "complaints:create",
    "complaints:read",
    "complaints:update",
    "complaints:assign",
    "complaints:escalate",
    "complaints:close",
)


def upgrade() -> None:
    conn = op.get_bind()
    for perm_code in _MANAGER_F4_PERMS:
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
    conn = op.get_bind()
    for perm_code in _MANAGER_F4_PERMS:
        conn.execute(
            sa.text(
                """
                DELETE FROM role_permissions
                WHERE role_id IN (
                    SELECT id FROM roles WHERE code = 'MANAGER' AND deleted_at IS NULL
                )
                AND permission_id IN (
                    SELECT id FROM permissions
                    WHERE code = :perm_code AND deleted_at IS NULL
                )
                """
            ),
            {"perm_code": perm_code},
        )
