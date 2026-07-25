"""CAPABILITY-011 — evolve attachments to aggregate-bound domain model.

Revision ID: 0035_attachment_domain
Revises: 0034_timeline_entries
Create Date: 2026-07-25

Renames polymorphic object_* columns to aggregate_*, introduces status-based
logical delete, and indexes required by CAPABILITY-011. Does not alter
Complaint / Queue / Notification / Timeline tables.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0035_attachment_domain"
down_revision: Union[str, None] = "0034_timeline_entries"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop TASK-029 indexes that will be replaced.
    op.drop_index("ix_attachments_object", table_name="attachments")
    op.drop_index("ix_attachments_checksum", table_name="attachments")
    op.drop_index("ix_attachments_stored_filename", table_name="attachments")
    op.drop_index("ix_attachments_deleted_at", table_name="attachments")

    op.alter_column("attachments", "object_type", new_column_name="aggregate_type")
    op.alter_column("attachments", "object_id", new_column_name="aggregate_id")
    op.alter_column("attachments", "filename", new_column_name="original_name")
    op.alter_column("attachments", "stored_filename", new_column_name="file_name")
    op.alter_column("attachments", "checksum", new_column_name="checksum_sha256")
    op.alter_column("attachments", "created_at", new_column_name="uploaded_at")

    op.add_column(
        "attachments",
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="AVAILABLE",
        ),
    )

    # Map soft-deleted rows to logical DELETED, then drop deleted_at.
    op.execute(
        sa.text(
            """
            UPDATE attachments
            SET status = 'DELETED'
            WHERE deleted_at IS NOT NULL
            """
        )
    )
    # Normalize legacy lowercase / free-form object types to AggregateType values.
    op.execute(
        sa.text(
            """
            UPDATE attachments
            SET aggregate_type = CASE lower(aggregate_type)
                WHEN 'complaint' THEN 'Complaint'
                WHEN 'queue' THEN 'Queue'
                WHEN 'notification' THEN 'Notification'
                ELSE aggregate_type
            END
            """
        )
    )

    op.drop_column("attachments", "deleted_at")

    op.create_index(
        "ix_attachments_aggregate_type", "attachments", ["aggregate_type"]
    )
    op.create_index(
        "ix_attachments_aggregate_id", "attachments", ["aggregate_id"]
    )
    op.create_index("ix_attachments_uploaded_at", "attachments", ["uploaded_at"])
    op.create_index(
        "ix_attachments_checksum_sha256", "attachments", ["checksum_sha256"]
    )
    op.create_index(
        "ix_attachments_aggregate",
        "attachments",
        ["aggregate_type", "aggregate_id"],
    )
    op.create_index("ix_attachments_status", "attachments", ["status"])
    op.create_index("ix_attachments_file_name", "attachments", ["file_name"])

    # Prefer CAPABILITY-011 default root when still on TASK-029 seed value.
    op.execute(
        sa.text(
            """
            UPDATE settings
            SET value = 'storage/attachments',
                description = 'Local storage root path for attachment blobs'
            WHERE key = 'storage.root.path'
              AND value = 'data/attachments'
            """
        )
    )


def downgrade() -> None:
    op.drop_index("ix_attachments_file_name", table_name="attachments")
    op.drop_index("ix_attachments_status", table_name="attachments")
    op.drop_index("ix_attachments_aggregate", table_name="attachments")
    op.drop_index("ix_attachments_checksum_sha256", table_name="attachments")
    op.drop_index("ix_attachments_uploaded_at", table_name="attachments")
    op.drop_index("ix_attachments_aggregate_id", table_name="attachments")
    op.drop_index("ix_attachments_aggregate_type", table_name="attachments")

    op.add_column(
        "attachments",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute(
        sa.text(
            """
            UPDATE attachments
            SET deleted_at = now()
            WHERE status = 'DELETED'
            """
        )
    )
    op.drop_column("attachments", "status")

    op.alter_column("attachments", "uploaded_at", new_column_name="created_at")
    op.alter_column("attachments", "checksum_sha256", new_column_name="checksum")
    op.alter_column("attachments", "file_name", new_column_name="stored_filename")
    op.alter_column("attachments", "original_name", new_column_name="filename")
    op.alter_column("attachments", "aggregate_id", new_column_name="object_id")
    op.alter_column("attachments", "aggregate_type", new_column_name="object_type")

    op.create_index(
        "ix_attachments_object", "attachments", ["object_type", "object_id"]
    )
    op.create_index("ix_attachments_checksum", "attachments", ["checksum"])
    op.create_index(
        "ix_attachments_stored_filename", "attachments", ["stored_filename"]
    )
    op.create_index("ix_attachments_deleted_at", "attachments", ["deleted_at"])

    op.execute(
        sa.text(
            """
            UPDATE settings
            SET value = 'data/attachments'
            WHERE key = 'storage.root.path'
              AND value = 'storage/attachments'
            """
        )
    )
