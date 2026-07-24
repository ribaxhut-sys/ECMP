"""Add sla_policies configuration table (TASK-022).

Revision ID: 0015_sla_policy
Revises: 0014_sla_foundation
Create Date: 2026-07-23
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0015_sla_policy"
down_revision: Union[str, None] = "0014_sla_foundation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sla_policies",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("assignment_target_minutes", sa.Integer(), nullable=False),
        sa.Column("appointment_target_minutes", sa.Integer(), nullable=False),
        sa.Column("resolution_target_minutes", sa.Integer(), nullable=False),
        sa.Column("escalation_target_minutes", sa.Integer(), nullable=False),
        sa.Column("overall_target_minutes", sa.Integer(), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
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
        sa.PrimaryKeyConstraint("id", name="pk_sla_policies"),
    )
    op.create_index("ix_sla_policies_is_active", "sla_policies", ["is_active"])
    op.create_index("ix_sla_policies_name", "sla_policies", ["name"])
    # Enforce at most one active policy (TASK-022 business rule).
    op.create_index(
        "uq_sla_policies_one_active",
        "sla_policies",
        ["is_active"],
        unique=True,
        postgresql_where=sa.text("is_active IS TRUE"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_sla_policies_one_active",
        table_name="sla_policies",
        postgresql_where=sa.text("is_active IS TRUE"),
    )
    op.drop_index("ix_sla_policies_name", table_name="sla_policies")
    op.drop_index("ix_sla_policies_is_active", table_name="sla_policies")
    op.drop_table("sla_policies")
