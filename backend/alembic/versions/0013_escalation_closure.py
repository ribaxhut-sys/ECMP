"""Add escalation closure fields (TASK-020).

Revision ID: 0013_escalation_closure
Revises: 0012_complaint_closure
Create Date: 2026-07-23
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0013_escalation_closure"
down_revision: Union[str, None] = "0012_complaint_closure"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "complaint_escalations",
        sa.Column(
            "closed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.add_column(
        "complaint_escalations",
        sa.Column(
            "closed_by",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )
    op.add_column(
        "complaint_escalations",
        sa.Column("closure_notes", sa.Text(), nullable=True),
    )
    op.create_foreign_key(
        "fk_complaint_escalations_closed_by_users",
        "complaint_escalations",
        "users",
        ["closed_by"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_complaint_escalations_closed_by",
        "complaint_escalations",
        ["closed_by"],
    )
    op.create_index(
        "ix_complaint_escalations_closed_at",
        "complaint_escalations",
        ["closed_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_complaint_escalations_closed_at",
        table_name="complaint_escalations",
    )
    op.drop_index(
        "ix_complaint_escalations_closed_by",
        table_name="complaint_escalations",
    )
    op.drop_constraint(
        "fk_complaint_escalations_closed_by_users",
        "complaint_escalations",
        type_="foreignkey",
    )
    op.drop_column("complaint_escalations", "closure_notes")
    op.drop_column("complaint_escalations", "closed_by")
    op.drop_column("complaint_escalations", "closed_at")
