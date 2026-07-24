"""Add Complaint Domain Foundation table (CAPABILITY-004).

Revision ID: 0028_complaint_domain_foundation
Revises: 0027_queue_persistence
Create Date: 2026-07-24

Creates complaint_cases (independent of legacy ``complaints`` table).
No FK to Queue tables — queue_ticket_id is a cross-BC reference only.
Migration only — no seed data.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0028_complaint_domain_foundation"
down_revision: Union[str, None] = "0027_queue_persistence"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "complaint_cases",
        sa.Column("complaint_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("queue_ticket_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("priority", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("complaint_id", name="pk_complaint_cases"),
    )
    op.create_index(
        "ix_complaint_cases_organization_id",
        "complaint_cases",
        ["organization_id"],
    )
    op.create_index(
        "ix_complaint_cases_branch_id",
        "complaint_cases",
        ["branch_id"],
    )
    op.create_index(
        "ix_complaint_cases_queue_ticket_id",
        "complaint_cases",
        ["queue_ticket_id"],
    )
    op.create_index("ix_complaint_cases_status", "complaint_cases", ["status"])
    op.create_index("ix_complaint_cases_priority", "complaint_cases", ["priority"])
    op.create_index(
        "ix_complaint_cases_org_status",
        "complaint_cases",
        ["organization_id", "status"],
    )


def downgrade() -> None:
    op.drop_index("ix_complaint_cases_org_status", table_name="complaint_cases")
    op.drop_index("ix_complaint_cases_priority", table_name="complaint_cases")
    op.drop_index("ix_complaint_cases_status", table_name="complaint_cases")
    op.drop_index("ix_complaint_cases_queue_ticket_id", table_name="complaint_cases")
    op.drop_index("ix_complaint_cases_branch_id", table_name="complaint_cases")
    op.drop_index("ix_complaint_cases_organization_id", table_name="complaint_cases")
    op.drop_table("complaint_cases")
