"""Announcement per-user read receipts (post-login unread-redirect milestone).

Revision ID: 0065_announcement_reads
Revises: 0064_announcement_attachments
Create Date: 2026-08-10

Minimal read-state table — not a notification system. One row per
(announcement, user); ``read_at`` set once on first mark-read. No FK on
``user_id`` (actor reference, same convention as AuditUserMixin /
``announcements.published_by`` — read history must survive user
soft-delete and a JWT principal is not guaranteed to have a backing
``users`` row).
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0065_announcement_reads"
down_revision: Union[str, None] = "0064_announcement_attachments"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "announcement_reads",
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
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "read_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["announcement_id"],
            ["announcements.id"],
            name="fk_announcement_reads_announcement_id_announcements",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "announcement_id",
            "user_id",
            name="uq_announcement_reads_pair",
        ),
    )
    op.create_index(
        "ix_announcement_reads_announcement_id",
        "announcement_reads",
        ["announcement_id"],
    )
    op.create_index(
        "ix_announcement_reads_user_id",
        "announcement_reads",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_announcement_reads_user_id",
        table_name="announcement_reads",
    )
    op.drop_index(
        "ix_announcement_reads_announcement_id",
        table_name="announcement_reads",
    )
    op.drop_table("announcement_reads")
