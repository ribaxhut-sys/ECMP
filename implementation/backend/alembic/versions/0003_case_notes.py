"""Revision 0003: case_notes (Sprint-06 append-only internal notes).

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-22
"""

import sqlalchemy as sa

from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "case_notes",
        sa.Column("note_id", sa.String(36), primary_key=True),
        sa.Column("case_id", sa.String(32), nullable=False),
        sa.Column("author_user_id", sa.String(64), nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_case_notes_case_id_created_at", "case_notes", ["case_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_case_notes_case_id_created_at", table_name="case_notes")
    op.drop_table("case_notes")
