"""Grant dashboard:read to MANAGER role (BC-8.4 branch-scoped dashboard).

Revision ID: 0055_manager_dashboard_read
Revises: 0054_manager_role
Create Date: 2026-08-08

Product decision: branch Manager may view the dashboard, scoped to their own
branch (see dashboard/router.py own-branch locking added alongside this
migration), in addition to the users:read/users:update granted in
0054_manager_role. Still no operational complaint permissions
(assign/escalate/close) — those remain out of scope for Manager.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0055_manager_dashboard_read"
down_revision: Union[str, None] = "0054_manager_role"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_PERM_CODE = "dashboard:read"


def upgrade() -> None:
    conn = op.get_bind()
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
        {"perm_code": _PERM_CODE},
    )


def downgrade() -> None:
    # Non-destructive — do not strip a grant that may be in use.
    pass
