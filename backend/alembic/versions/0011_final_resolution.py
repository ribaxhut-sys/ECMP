"""Add final resolution fields to complaint_resolutions (TASK-018).

Revision ID: 0011_final_resolution
Revises: 0010_appointment_no_show
Create Date: 2026-07-23
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0011_final_resolution"
down_revision: Union[str, None] = "0010_appointment_no_show"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "complaint_resolutions",
        sa.Column(
            "final_resolution_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.add_column(
        "complaint_resolutions",
        sa.Column(
            "final_resolution_by",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )
    op.add_column(
        "complaint_resolutions",
        sa.Column("final_resolution_notes", sa.Text(), nullable=True),
    )
    op.add_column(
        "complaint_resolutions",
        sa.Column("final_resolution_summary", sa.Text(), nullable=True),
    )
    op.add_column(
        "complaint_resolutions",
        sa.Column(
            "follow_up_required",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )
    op.create_foreign_key(
        "fk_complaint_resolutions_final_resolution_by_users",
        "complaint_resolutions",
        "users",
        ["final_resolution_by"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(
        "ix_complaint_resolutions_final_resolution_at",
        "complaint_resolutions",
        ["final_resolution_at"],
    )
    op.create_index(
        "ix_complaint_resolutions_final_resolution_by",
        "complaint_resolutions",
        ["final_resolution_by"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_complaint_resolutions_final_resolution_by",
        table_name="complaint_resolutions",
    )
    op.drop_index(
        "ix_complaint_resolutions_final_resolution_at",
        table_name="complaint_resolutions",
    )
    op.drop_constraint(
        "fk_complaint_resolutions_final_resolution_by_users",
        "complaint_resolutions",
        type_="foreignkey",
    )
    op.drop_column("complaint_resolutions", "follow_up_required")
    op.drop_column("complaint_resolutions", "final_resolution_summary")
    op.drop_column("complaint_resolutions", "final_resolution_notes")
    op.drop_column("complaint_resolutions", "final_resolution_by")
    op.drop_column("complaint_resolutions", "final_resolution_at")
