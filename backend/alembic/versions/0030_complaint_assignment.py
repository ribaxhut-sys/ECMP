"""Add Complaint Assignment table (CAPABILITY-006).

Revision ID: 0030_complaint_assignment
Revises: 0029_complaint_processing
Create Date: 2026-07-24

Creates ``complaint_case_assignments`` for the Clean Architecture Complaint BC
(``complaint_cases``). Legacy ECMF ``complaint_assignments`` is unchanged.
Partial unique index enforces at most one active assignment per complaint.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0030_complaint_assignment"
down_revision: Union[str, None] = "0029_complaint_processing"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "complaint_case_assignments",
        sa.Column("assignment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("complaint_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assignee_type", sa.String(length=32), nullable=False),
        sa.Column("assignee_id", sa.String(length=200), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("assigned_by", sa.String(length=200), nullable=False),
        sa.Column("released_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("release_reason", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["complaint_id"],
            ["complaint_cases.complaint_id"],
            name="fk_complaint_case_assignments_complaint_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "assignment_id", name="pk_complaint_case_assignments"
        ),
    )
    op.create_index(
        "ix_complaint_case_assignments_complaint_id",
        "complaint_case_assignments",
        ["complaint_id"],
        unique=False,
    )
    op.create_index(
        "ix_complaint_case_assignments_complaint_active",
        "complaint_case_assignments",
        ["complaint_id"],
        unique=True,
        postgresql_where=sa.text("is_active = true"),
    )
    op.create_index(
        "ix_complaint_case_assignments_assignee",
        "complaint_case_assignments",
        ["assignee_type", "assignee_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_complaint_case_assignments_assignee",
        table_name="complaint_case_assignments",
    )
    op.drop_index(
        "ix_complaint_case_assignments_complaint_active",
        table_name="complaint_case_assignments",
    )
    op.drop_index(
        "ix_complaint_case_assignments_complaint_id",
        table_name="complaint_case_assignments",
    )
    op.drop_table("complaint_case_assignments")
