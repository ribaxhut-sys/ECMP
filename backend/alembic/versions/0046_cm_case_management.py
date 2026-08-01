"""Alembic migration — CAP-008 Case Management Mode A tables.

Revision ID: 0046_cm_case_management
Revises: 0045_cm_b1_lr_complaint_id
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0046_cm_case_management"
down_revision: Union[str, None] = "0045_cm_b1_lr_complaint_id"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cm_cases",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("case_number", sa.String(32), nullable=False),
        sa.Column("complaint_id", sa.String(64), nullable=False),
        sa.Column("customer_id", sa.String(128), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("case_type", sa.String(100), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("subject", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("priority", sa.String(32), nullable=False),
        sa.Column("owning_unit_id", sa.String(128), nullable=True),
        sa.Column("sla_policy_version_id", sa.String(128), nullable=True),
        sa.Column(
            "sla_countdown_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column("cancel_reason", sa.String(64), nullable=True),
        sa.Column("closed_by", sa.String(128), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "supervisor_approved_after_resolved",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column("created_by", sa.String(128), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("case_number", name="uq_cm_cases_case_number"),
    )
    op.create_index("ix_cm_cases_complaint_id", "cm_cases", ["complaint_id"])
    op.create_index("ix_cm_cases_status", "cm_cases", ["status"])
    op.create_index("ix_cm_cases_created_at", "cm_cases", ["created_at"])

    op.create_table(
        "cm_case_resolutions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "case_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cm_cases.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("resolution_code", sa.String(64), nullable=False),
        sa.Column("summary", sa.String(1000), nullable=False),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column("customer_impact", sa.Text(), nullable=True),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("comment", sa.Text(), nullable=False),
        sa.Column("attachment_ids", sa.JSON(), nullable=True),
        sa.Column("proposed_by", sa.String(128), nullable=True),
        sa.Column("proposed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decided_by", sa.String(128), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_cm_case_resolutions_case_id", "cm_case_resolutions", ["case_id"]
    )

    op.create_table(
        "cm_case_number_counters",
        sa.Column("year", sa.Integer(), primary_key=True),
        sa.Column("last_seq", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_table("cm_case_number_counters")
    op.drop_index("ix_cm_case_resolutions_case_id", table_name="cm_case_resolutions")
    op.drop_table("cm_case_resolutions")
    op.drop_index("ix_cm_cases_created_at", table_name="cm_cases")
    op.drop_index("ix_cm_cases_status", table_name="cm_cases")
    op.drop_index("ix_cm_cases_complaint_id", table_name="cm_cases")
    op.drop_table("cm_cases")
