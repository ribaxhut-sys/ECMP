"""Create data_scopes table (TASK-037).

Revision ID: 0024_data_scopes
Revises: 0023_user_roles
Create Date: 2026-07-24

Seeds data_scope:read / data_scope:update catalog entries.
Does not integrate with Authorization Engine or endpoint filtering.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0024_data_scopes"
down_revision: Union[str, None] = "0023_user_roles"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_SEED_PERMISSIONS: tuple[tuple[str, str, str, str], ...] = (
    (
        "data_scope:read",
        "Data Scope Read",
        "data_scope",
        "Read role data scopes",
    ),
    (
        "data_scope:update",
        "Data Scope Update",
        "data_scope",
        "Update role data scopes",
    ),
)


def upgrade() -> None:
    op.create_table(
        "data_scopes",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scope_type", sa.String(length=50), nullable=False),
        sa.Column("scope_value", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
            name="fk_data_scopes_role_id_roles",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_data_scopes"),
        sa.UniqueConstraint(
            "role_id",
            "scope_type",
            "scope_value",
            name="uq_data_scopes_role_id_scope_type_scope_value",
        ),
    )
    op.create_index("ix_data_scopes_role_id", "data_scopes", ["role_id"])
    op.create_index("ix_data_scopes_scope_type", "data_scopes", ["scope_type"])

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
    op.drop_index("ix_data_scopes_scope_type", table_name="data_scopes")
    op.drop_index("ix_data_scopes_role_id", table_name="data_scopes")
    op.drop_table("data_scopes")
