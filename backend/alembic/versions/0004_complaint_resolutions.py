"""Add complaint_resolutions table (TASK-010).

Revision ID: 0004_complaint_resolutions
Revises: 0003_refresh_tokens
Create Date: 2026-07-23
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004_complaint_resolutions"
down_revision: Union[str, None] = "0003_refresh_tokens"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "complaint_resolutions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("complaint_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("resolution_category", sa.String(length=32), nullable=False),
        sa.Column("root_cause", sa.String(length=500), nullable=False),
        sa.Column("resolution_notes", sa.Text(), nullable=False),
        sa.Column("resolved_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "is_current",
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
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["complaint_id"],
            ["complaints.id"],
            name="fk_complaint_resolutions_complaint_id_complaints",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["resolved_by"],
            ["users.id"],
            name="fk_complaint_resolutions_resolved_by_users",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_complaint_resolutions"),
    )
    op.create_index(
        "ix_complaint_resolutions_complaint_id",
        "complaint_resolutions",
        ["complaint_id"],
    )
    op.create_index(
        "ix_complaint_resolutions_resolved_by",
        "complaint_resolutions",
        ["resolved_by"],
    )
    op.create_index(
        "ix_complaint_resolutions_resolved_at",
        "complaint_resolutions",
        ["resolved_at"],
    )
    op.create_index(
        "ix_complaint_resolutions_complaint_current",
        "complaint_resolutions",
        ["complaint_id", "is_current"],
    )
    op.create_index(
        "ix_complaint_resolutions_deleted_at",
        "complaint_resolutions",
        ["deleted_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_complaint_resolutions_deleted_at", table_name="complaint_resolutions"
    )
    op.drop_index(
        "ix_complaint_resolutions_complaint_current",
        table_name="complaint_resolutions",
    )
    op.drop_index(
        "ix_complaint_resolutions_resolved_at", table_name="complaint_resolutions"
    )
    op.drop_index(
        "ix_complaint_resolutions_resolved_by", table_name="complaint_resolutions"
    )
    op.drop_index(
        "ix_complaint_resolutions_complaint_id", table_name="complaint_resolutions"
    )
    op.drop_table("complaint_resolutions")
