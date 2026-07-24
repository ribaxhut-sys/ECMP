"""Add Complaint Escalation table (CAPABILITY-007).

Revision ID: 0031_complaint_escalation
Revises: 0030_complaint_assignment
Create Date: 2026-07-24

Creates ``complaint_case_escalations`` for the Clean Architecture Complaint BC
(``complaint_cases``). Legacy ECMF ``complaint_escalations`` is unchanged.
Partial unique index enforces at most one current escalation per complaint.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0031_complaint_escalation"
down_revision: Union[str, None] = "0030_complaint_assignment"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "complaint_case_escalations",
        sa.Column("escalation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("complaint_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("level", sa.String(length=32), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("escalated_by", sa.String(length=200), nullable=False),
        sa.Column("escalated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("released_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_current", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["complaint_id"],
            ["complaint_cases.complaint_id"],
            name="fk_complaint_case_escalations_complaint_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "escalation_id", name="pk_complaint_case_escalations"
        ),
    )
    op.create_index(
        "ix_complaint_case_escalations_complaint_id",
        "complaint_case_escalations",
        ["complaint_id"],
        unique=False,
    )
    op.create_index(
        "ix_complaint_case_escalations_complaint_current",
        "complaint_case_escalations",
        ["complaint_id"],
        unique=True,
        postgresql_where=sa.text("is_current = true"),
    )
    op.create_index(
        "ix_complaint_case_escalations_level",
        "complaint_case_escalations",
        ["level"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_complaint_case_escalations_level",
        table_name="complaint_case_escalations",
    )
    op.drop_index(
        "ix_complaint_case_escalations_complaint_current",
        table_name="complaint_case_escalations",
    )
    op.drop_index(
        "ix_complaint_case_escalations_complaint_id",
        table_name="complaint_case_escalations",
    )
    op.drop_table("complaint_case_escalations")
