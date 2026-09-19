"""Seed queue:manage / customers:update and stop gating them on complaints:create.

Revision ID: 0073_queue_customers_perms
Revises: 0072_drop_foundation_tables
Create Date: 2026-08-13

``complaints:create`` had become a de-facto "front-office staff may act"
catch-all: holding it also allowed creating service queues, creating physical
counters (API-370), issuing queue tickets (API-365/376), and editing a
customer's phone number in the Mode A cache — none of which create a
Complaint. The queue ticket endpoint's own summary says so outright ("Does
not create Complaints (separate lifecycle)").

Grant strategy: every role that already holds ``complaints:create`` receives
both new permissions, so no operator loses access on deploy. This separates
the vocabulary now; narrowing *who* holds queue/customer write rights is a
business decision left to the Board.

Scope note: the rest of the queue and customers modules still ride
``complaints:read`` / ``complaints:update`` (15 more gates). Moving those is
the wider per-bounded-context namespace work, deliberately not bundled here.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0073_queue_customers_perms"
down_revision: Union[str, None] = "0072_drop_foundation_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_SEED_PERMISSIONS: tuple[tuple[str, str, str, str], ...] = (
    (
        "queue:manage",
        "Queue Manage",
        "queue",
        "Create service queues and counters, and issue queue tickets",
    ),
    (
        "customers:update",
        "Customers Update",
        "customers",
        "Update the Mode A local customer reference cache",
    ),
)

_GRANT_LIKE_COMPLAINTS_CREATE_SQL = """
    INSERT INTO role_permissions (id, role_id, permission_id, created_at)
    SELECT gen_random_uuid(), rp_src.role_id, p.id, now()
    FROM role_permissions rp_src
    JOIN permissions p_src ON p_src.id = rp_src.permission_id
    CROSS JOIN permissions p
    WHERE p_src.code = 'complaints:create'
      AND p_src.deleted_at IS NULL
      AND p.code = :perm_code
      AND p.deleted_at IS NULL
      AND NOT EXISTS (
        SELECT 1 FROM role_permissions rp
        WHERE rp.role_id = rp_src.role_id AND rp.permission_id = p.id
      )
"""


def upgrade() -> None:
    conn = op.get_bind()

    for code, name, module, description in _SEED_PERMISSIONS:
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
            {"code": code, "name": name, "module": module, "description": description},
        )
        conn.execute(
            sa.text(_GRANT_LIKE_COMPLAINTS_CREATE_SQL), {"perm_code": code}
        )


def downgrade() -> None:
    # Non-destructive — do not strip grants that may be in use.
    pass
