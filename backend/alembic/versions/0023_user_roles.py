"""Create user_roles junction table (TASK-036).

Revision ID: 0023_user_roles
Revises: 0022_role_permissions
Create Date: 2026-07-24

Seeds user_role:read / user_role:update catalog entries.
Does not seed assignment rows, mutate users.role_id, or change
Authorization Engine resolution.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0023_user_roles"
down_revision: Union[str, None] = "0022_role_permissions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_SEED_PERMISSIONS: tuple[tuple[str, str, str, str], ...] = (
    (
        "user_role:read",
        "User Role Read",
        "user_role",
        "Read user↔role assignments",
    ),
    (
        "user_role:update",
        "User Role Update",
        "user_role",
        "Update user↔role assignments",
    ),
)


def upgrade() -> None:
    op.create_table(
        "user_roles",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_user_roles_user_id_users",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
            name="fk_user_roles_role_id_roles",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_user_roles"),
        sa.UniqueConstraint(
            "user_id",
            "role_id",
            name="uq_user_roles_user_id_role_id",
        ),
    )
    op.create_index("ix_user_roles_user_id", "user_roles", ["user_id"])
    op.create_index("ix_user_roles_role_id", "user_roles", ["role_id"])

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
    op.drop_index("ix_user_roles_role_id", table_name="user_roles")
    op.drop_index("ix_user_roles_user_id", table_name="user_roles")
    op.drop_table("user_roles")
