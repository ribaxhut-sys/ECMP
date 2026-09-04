"""Grant SUPERVISOR (and BRANCH_SUPERVISOR alias) role:read (UM-BUG-004).

Revision ID: 0052_supervisor_role_read
Revises: 0051_cm_b1_hq_arrival
Create Date: 2026-08-07

Root cause observed in lab: Supervisor's user-directory page loads users,
branches, and the role catalog together; the role catalog fetch requires
role:read, which SUPERVISOR never had, even though SUPERVISOR already
holds users:create / users:update (both need the role catalog to assign
a role). The frontend load was all-or-nothing, so the missing permission
broke the entire directory view for supervisors, not just role
assignment.

This migration closes the gap on the data side: role:read is read-only
reference data (id/code/name/isActive — no permission internals), so
granting it to SUPERVISOR is consistent with the create/update grants it
already has. Non-destructive: only inserts the missing link.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0052_supervisor_role_read"
down_revision: Union[str, None] = "0051_cm_b1_hq_arrival"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_SUPERVISOR_ROLE_CODES: tuple[str, ...] = ("SUPERVISOR", "BRANCH_SUPERVISOR")
_PERM_CODE = "role:read"


def upgrade() -> None:
    conn = op.get_bind()

    for role_code in _SUPERVISOR_ROLE_CODES:
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
    # Non-destructive repair — do not strip permissions on downgrade.
    pass
