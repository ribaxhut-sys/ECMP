"""Add Escalation Review fields (TASK-012).

Revision ID: 0006_escalation_review
Revises: 0005_complaint_escalations
Create Date: 2026-07-23
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006_escalation_review"
down_revision: Union[str, None] = "0005_complaint_escalations"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "complaint_escalations",
        sa.Column("reviewed_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "complaint_escalations",
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "complaint_escalations",
        sa.Column("review_notes", sa.Text(), nullable=True),
    )
    op.create_foreign_key(
        "fk_complaint_escalations_reviewed_by_users",
        "complaint_escalations",
        "users",
        ["reviewed_by"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_complaint_escalations_reviewed_by",
        "complaint_escalations",
        ["reviewed_by"],
    )
    op.create_index(
        "ix_complaint_escalations_reviewed_at",
        "complaint_escalations",
        ["reviewed_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_complaint_escalations_reviewed_at", table_name="complaint_escalations"
    )
    op.drop_index(
        "ix_complaint_escalations_reviewed_by", table_name="complaint_escalations"
    )
    op.drop_constraint(
        "fk_complaint_escalations_reviewed_by_users",
        "complaint_escalations",
        type_="foreignkey",
    )
    op.drop_column("complaint_escalations", "review_notes")
    op.drop_column("complaint_escalations", "reviewed_at")
    op.drop_column("complaint_escalations", "reviewed_by")
