"""CM Batch 1 FR-004 attachment business metadata tables (S2 Task 03).

Revision ID: 0042_cm_batch1_attachment
Revises: 0041_cm_batch1_duplicate
Create Date: 2026-07-29

Creates:
- cm_batch1_attachment_staging
- cm_batch1_attachments (FK to CAP-011 attachments + cm_batch1_complaints)
- cm_batch1_attachment_history

Does NOT modify 0040/0041. Binary engine remains CAP-011 ``attachments``.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0042_cm_batch1_attachment"
down_revision: Union[str, None] = "0041_cm_batch1_duplicate"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cm_batch1_attachment_staging",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("staging_token", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_by", sa.String(length=128), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_cm_batch1_attachment_staging"),
        sa.UniqueConstraint("staging_token", name="uq_cm_batch1_staging_token"),
    )
    op.create_index(
        "ix_cm_batch1_staging_status",
        "cm_batch1_attachment_staging",
        ["status"],
    )
    op.create_index(
        "ix_cm_batch1_staging_expires_at",
        "cm_batch1_attachment_staging",
        ["expires_at"],
    )

    op.create_table(
        "cm_batch1_attachments",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "platform_attachment_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("staging_token", sa.String(length=128), nullable=True),
        sa.Column("complaint_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("classification", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("original_name", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=False),
        sa.Column("supersedes_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("void_reason", sa.Text(), nullable=True),
        sa.Column("uploaded_by", sa.String(length=128), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["platform_attachment_id"],
            ["attachments.id"],
            name="fk_cm_batch1_att_platform",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["complaint_id"],
            ["cm_batch1_complaints.id"],
            name="fk_cm_batch1_att_complaint",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["supersedes_id"],
            ["cm_batch1_attachments.id"],
            name="fk_cm_batch1_att_supersedes",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_cm_batch1_attachments"),
    )
    op.create_index(
        "ix_cm_batch1_attachments_complaint_id",
        "cm_batch1_attachments",
        ["complaint_id"],
    )
    op.create_index(
        "ix_cm_batch1_attachments_staging_token",
        "cm_batch1_attachments",
        ["staging_token"],
    )
    op.create_index(
        "ix_cm_batch1_attachments_status",
        "cm_batch1_attachments",
        ["status"],
    )
    op.create_index(
        "ix_cm_batch1_attachments_platform_id",
        "cm_batch1_attachments",
        ["platform_attachment_id"],
    )
    op.create_index(
        "ix_cm_batch1_attachments_checksum",
        "cm_batch1_attachments",
        ["checksum_sha256"],
    )

    op.create_table(
        "cm_batch1_attachment_history",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("attachment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("from_status", sa.String(length=32), nullable=True),
        sa.Column("to_status", sa.String(length=32), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("actor_id", sa.String(length=128), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["attachment_id"],
            ["cm_batch1_attachments.id"],
            name="fk_cm_batch1_att_history_att",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_cm_batch1_attachment_history"),
    )
    op.create_index(
        "ix_cm_batch1_att_history_attachment_id",
        "cm_batch1_attachment_history",
        ["attachment_id"],
    )
    op.create_index(
        "ix_cm_batch1_att_history_created_at",
        "cm_batch1_attachment_history",
        ["created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_cm_batch1_att_history_created_at",
        table_name="cm_batch1_attachment_history",
    )
    op.drop_index(
        "ix_cm_batch1_att_history_attachment_id",
        table_name="cm_batch1_attachment_history",
    )
    op.drop_table("cm_batch1_attachment_history")
    op.drop_index(
        "ix_cm_batch1_attachments_checksum", table_name="cm_batch1_attachments"
    )
    op.drop_index(
        "ix_cm_batch1_attachments_platform_id", table_name="cm_batch1_attachments"
    )
    op.drop_index(
        "ix_cm_batch1_attachments_status", table_name="cm_batch1_attachments"
    )
    op.drop_index(
        "ix_cm_batch1_attachments_staging_token",
        table_name="cm_batch1_attachments",
    )
    op.drop_index(
        "ix_cm_batch1_attachments_complaint_id",
        table_name="cm_batch1_attachments",
    )
    op.drop_table("cm_batch1_attachments")
    op.drop_index(
        "ix_cm_batch1_staging_expires_at",
        table_name="cm_batch1_attachment_staging",
    )
    op.drop_index(
        "ix_cm_batch1_staging_status",
        table_name="cm_batch1_attachment_staging",
    )
    op.drop_table("cm_batch1_attachment_staging")
