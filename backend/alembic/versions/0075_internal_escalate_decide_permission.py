"""Seed internal:escalate-decide — Agent transfer-request gate decider.

Revision ID: 0075_internal_escalate_decide
Revises: 0074_admin_no_complaint_create
Create Date: 2026-08-14

Pengaduan Internal: Agent-family may create locally but never transfers
Handling to the opposite unit (Cabang <-> Pusat) directly — that now requires
a request + reason, decided by Supervisor, Manager, or Admin. This is a
distinct gate from ``complaints:escalate`` (WP intake-escalation decision,
CAP-008) and from ``complaints:assign`` (direct transfer, still held by
Supervisor/Manager for their own create-time transfers). Granted directly to
role codes, not copied from an existing grant — Agent must never hold it.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0075_internal_escalate_decide"
down_revision: Union[str, None] = "0074_admin_no_complaint_create"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_PERM_CODE = "internal:escalate-decide"
_PERM_NAME = "Internal Complaint Escalate Decide"
_PERM_MODULE = "internal_complaint"
_PERM_DESCRIPTION = (
    "Decide (approve/reject) an Agent-family Pengaduan Internal transfer "
    "request to the opposite unit (Cabang <-> Pusat)."
)

_GRANT_ROLE_CODES: tuple[str, ...] = (
    "SUPERVISOR",
    "BRANCH_SUPERVISOR",
    "MANAGER",
    "ADMIN",
    "ADMINISTRATOR",
    "SUPER_ADMIN",
)


def upgrade() -> None:
    conn = op.get_bind()

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
            "code": _PERM_CODE,
            "name": _PERM_NAME,
            "module": _PERM_MODULE,
            "description": _PERM_DESCRIPTION,
        },
    )

    for role_code in _GRANT_ROLE_CODES:
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
            {"role_code": role_code, "perm_code": _PERM_CODE},
        )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            DELETE FROM role_permissions rp
            USING permissions p
            WHERE rp.permission_id = p.id
              AND p.code = :perm_code
            """
        ),
        {"perm_code": _PERM_CODE},
    )
    conn.execute(
        sa.text("DELETE FROM permissions WHERE code = :perm_code"),
        {"perm_code": _PERM_CODE},
    )
