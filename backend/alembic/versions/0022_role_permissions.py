"""Create role_permissions junction table (TASK-035).

Revision ID: 0022_role_permissions
Revises: 0021_permissions
Create Date: 2026-07-24

Seeds role_permission:read / role_permission:update catalog entries.
Does not seed matrix rows or change Authorization Engine resolution.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0022_role_permissions"
down_revision: Union[str, None] = "0021_permissions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_SEED_PERMISSIONS: tuple[tuple[str, str, str, str], ...] = (
    (
        "role_permission:read",
        "Role Permission Read",
        "role_permission",
        "Read role↔permission matrix",
    ),
    (
        "role_permission:update",
        "Role Permission Update",
        "role_permission",
        "Update role↔permission matrix",
    ),
)


def upgrade() -> None:
    op.create_table(
        "role_permissions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("permission_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
            name="fk_role_permissions_role_id_roles",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["permission_id"],
            ["permissions.id"],
            name="fk_role_permissions_permission_id_permissions",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_role_permissions"),
        sa.UniqueConstraint(
            "role_id",
            "permission_id",
            name="uq_role_permissions_role_id_permission_id",
        ),
    )
    op.create_index(
        "ix_role_permissions_role_id", "role_permissions", ["role_id"]
    )
    op.create_index(
        "ix_role_permissions_permission_id",
        "role_permissions",
        ["permission_id"],
    )

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
            {
                "code": code,
                "name": name,
                "module": module,
                "description": description,
            },
        )


def downgrade() -> None:
    op.drop_index(
        "ix_role_permissions_permission_id", table_name="role_permissions"
    )
    op.drop_index("ix_role_permissions_role_id", table_name="role_permissions")
    op.drop_table("role_permissions")
    # Leave seeded permission catalog rows (may be referenced elsewhere).
