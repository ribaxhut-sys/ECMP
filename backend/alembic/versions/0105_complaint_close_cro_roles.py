"""Grant complaints:close to CRO; revoke from Admin (SoD A).

Revision ID: 0105_complaint_close_cro_roles
Revises: 0104_knowledge_user_pins
Create Date: 2026-08-24

Close Aggregate (API-312) is limited to CRO / Staff KaSatPel / KaSatPel.
Admin keeps ``*`` and other ops grants but must not close WP complaints;
wildcard exclusion for ``complaints:close`` lives in Principal / FE
``hasPermission`` (same pattern as 0074 for create).
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0105_complaint_close_cro_roles"
down_revision: Union[str, None] = "0104_knowledge_user_pins"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_PERM = "complaints:close"
_CRO_ROLE_CODES: tuple[str, ...] = (
    "AGENT",
    "CS_AGENT",
    "HANDLER",
    "BRANCH_OFFICER",
)
_ADMIN_ROLE_CODES: tuple[str, ...] = ("ADMIN", "ADMINISTRATOR", "SUPER_ADMIN")


def upgrade() -> None:
    conn = op.get_bind()
    for role_code in _CRO_ROLE_CODES:
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
    for role_code in _CRO_ROLE_CODES:
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
