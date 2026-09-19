"""Announcement ↔ Attachment relation + per-file visibility.

Revision ID: 0064_announcement_attachments
Revises: 0063_announcement_permissions
Create Date: 2026-08-10

Reuses the existing generic ``attachments`` table (CAPABILITY-011) for
storage/upload/download/checksum — this migration only adds the join table
that records which platform attachment belongs to which announcement, and
under which of the two visibility options (business decision, LOCKED):

  - IMMEDIATE  — visible as soon as the file exists, even while the
    announcement is still DRAFT.
  - PUBLISHED  — the default (safest) choice — follows the announcement's
    own status; only visible once the announcement is PUBLISHED.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0064_announcement_attachments"
down_revision: Union[str, None] = "0063_announcement_permissions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "announcement_attachments",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "announcement_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "attachment_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "visibility",
            sa.String(20),
            nullable=False,
            server_default="PUBLISHED",
        ),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["announcement_id"],
            ["announcements.id"],
            name="fk_announcement_attachments_announcement_id_announcements",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["attachment_id"],
            ["attachments.id"],
            name="fk_announcement_attachments_attachment_id_attachments",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "announcement_id",
            "attachment_id",
            name="uq_announcement_attachments_pair",
        ),
    )
    op.create_index(
        "ix_announcement_attachments_announcement_id",
        "announcement_attachments",
        ["announcement_id"],
    )
    op.create_index(
        "ix_announcement_attachments_attachment_id",
        "announcement_attachments",
        ["attachment_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_announcement_attachments_attachment_id",
        table_name="announcement_attachments",
    )
    op.drop_index(
        "ix_announcement_attachments_announcement_id",
        table_name="announcement_attachments",
    )
    op.drop_table("announcement_attachments")
