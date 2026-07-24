"""Evolve roles table for Role Management (TASK-033).

Revision ID: 0020_roles
Revises: 0019_audit
Create Date: 2026-07-24

Adds ``is_system``, widens ``code``/``name``, seeds baseline system roles.
Existing ``roles`` table (0001) retained — User/Escalation FKs unchanged.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0020_roles"
down_revision: Union[str, None] = "0019_audit"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_SEED_ROLES: tuple[tuple[str, str, str], ...] = (
    ("SUPER_ADMIN", "Super Administrator", "Platform super administrator (system)"),
    ("ADMIN", "Administrator", "System administrator"),
    ("SUPERVISOR", "Supervisor", "Branch / operations supervisor"),
    ("AGENT", "Agent", "Front-line complaint agent"),
    ("VIEWER", "Viewer", "Read-only viewer"),
)


def upgrade() -> None:
    op.add_column(
        "roles",
        sa.Column(
            "is_system",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )
    op.create_index("ix_roles_is_system", "roles", ["is_system"])

    op.alter_column(
        "roles",
        "code",
        existing_type=sa.String(length=64),
        type_=sa.String(length=100),
        existing_nullable=False,
    )
    op.alter_column(
        "roles",
        "name",
        existing_type=sa.String(length=128),
        type_=sa.String(length=200),
        existing_nullable=False,
    )

    # Upsert baseline system roles (preserve existing ids on conflict).
    conn = op.get_bind()
    for code, name, description in _SEED_ROLES:
        conn.execute(
            sa.text(
                """
                INSERT INTO roles (
                    id, code, name, description,
                    is_system, is_active, created_at, updated_at
                )
                VALUES (
                    gen_random_uuid(), :code, :name, :description,
                    true, true, now(), now()
                )
                ON CONFLICT (code) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = COALESCE(roles.description, EXCLUDED.description),
                    is_system = true,
                    is_active = true,
                    deleted_at = NULL,
                    updated_at = now()
                """
            ),
            {"code": code, "name": name, "description": description},
        )


def downgrade() -> None:
    # Do not delete seeded rows (may be referenced by users).
    op.drop_index("ix_roles_is_system", table_name="roles")
    op.drop_column("roles", "is_system")
    op.alter_column(
        "roles",
        "name",
        existing_type=sa.String(length=200),
        type_=sa.String(length=128),
        existing_nullable=False,
    )
    op.alter_column(
        "roles",
        "code",
        existing_type=sa.String(length=100),
        type_=sa.String(length=64),
        existing_nullable=False,
    )
