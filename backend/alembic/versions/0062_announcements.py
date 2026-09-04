"""Pengumuman (Complaint module operational announcements) — persistence table.

Revision ID: 0062_announcements
Revises: 0061_internal_related_complaint
Create Date: 2026-08-09

Business decision (LOCKED): no approval workflow, no scheduling engine.
start_at/end_at/published_at stay plain nullable timestamps evaluated at
read time. created_by/updated_by/deleted_at reuse the standard
TimestampAuditSoftDeleteMixin shape (see app/db/base.py) — no bespoke
audit system.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0062_announcements"
down_revision: Union[str, None] = "0061_internal_related_complaint"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "announcements",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("priority", sa.String(20), nullable=False, server_default="NORMAL"),
        sa.Column("status", sa.String(20), nullable=False, server_default="DRAFT"),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_by", postgresql.UUID(as_uuid=True), nullable=True),
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
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_announcements_status", "announcements", ["status"])
    op.create_index(
        "ix_announcements_published_at", "announcements", ["published_at"]
    )
    op.create_index("ix_announcements_deleted_at", "announcements", ["deleted_at"])


def downgrade() -> None:
    op.drop_index("ix_announcements_deleted_at", table_name="announcements")
    op.drop_index("ix_announcements_published_at", table_name="announcements")
    op.drop_index("ix_announcements_status", table_name="announcements")
    op.drop_table("announcements")
