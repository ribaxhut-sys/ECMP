"""Replace complaint-bound attachments with generic platform attachments + storage settings (TASK-029).

Revision ID: 0017_attachments
Revises: 0016_settings
Create Date: 2026-07-23
"""

from __future__ import annotations

import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0017_attachments"
down_revision: Union[str, None] = "0016_settings"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_ALLOWED_MIME = [
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "text/plain",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
]

_SEED_SETTINGS: tuple[dict[str, str | None], ...] = (
    {
        "key": "storage.provider",
        "value": "local",
        "value_type": "STRING",
        "category": "storage",
        "visibility": "PROTECTED",
        "description": "Attachment storage provider (local)",
    },
    {
        "key": "storage.root.path",
        "value": "data/attachments",
        "value_type": "STRING",
        "category": "storage",
        "visibility": "PROTECTED",
        "description": "Local storage root path for attachment blobs",
    },
    {
        "key": "storage.max.upload.mb",
        "value": "10",
        "value_type": "INTEGER",
        "category": "storage",
        "visibility": "PROTECTED",
        "description": "Maximum attachment upload size in megabytes",
    },
    {
        "key": "storage.allowed.mime",
        "value": json.dumps(_ALLOWED_MIME, separators=(",", ":")),
        "value_type": "JSON",
        "category": "storage",
        "visibility": "PROTECTED",
        "description": "Allowed attachment MIME types (JSON array)",
    },
)


def upgrade() -> None:
    # Foundation table was complaint-owned and unused by any API. Replace with
    # polymorphic platform attachments (object_type + object_id).
    op.drop_index("ix_attachments_uploaded_by", table_name="attachments")
    op.drop_index("ix_attachments_storage_key", table_name="attachments")
    op.drop_index("ix_attachments_deleted_at", table_name="attachments")
    op.drop_index("ix_attachments_complaint_id", table_name="attachments")
    op.drop_table("attachments")

    op.create_table(
        "attachments",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("object_type", sa.String(length=50), nullable=False),
        sa.Column("object_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("stored_filename", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("extension", sa.String(length=20), nullable=True),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("checksum", sa.String(length=64), nullable=False),
        sa.Column("storage_provider", sa.String(length=50), nullable=False),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["uploaded_by"],
            ["users.id"],
            name="fk_attachments_uploaded_by_users",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_attachments"),
    )
    op.create_index(
        "ix_attachments_object", "attachments", ["object_type", "object_id"]
    )
    op.create_index("ix_attachments_uploaded_by", "attachments", ["uploaded_by"])
    op.create_index("ix_attachments_checksum", "attachments", ["checksum"])
    op.create_index(
        "ix_attachments_stored_filename", "attachments", ["stored_filename"]
    )
    op.create_index("ix_attachments_deleted_at", "attachments", ["deleted_at"])

    settings_table = sa.table(
        "settings",
        sa.column("key", sa.String),
        sa.column("value", sa.Text),
        sa.column("value_type", sa.String),
        sa.column("category", sa.String),
        sa.column("visibility", sa.String),
        sa.column("description", sa.Text),
    )
    op.bulk_insert(settings_table, list(_SEED_SETTINGS))


def downgrade() -> None:
    op.execute(
        sa.text(
            "DELETE FROM settings WHERE key IN ("
            "'storage.provider', 'storage.root.path', "
            "'storage.max.upload.mb', 'storage.allowed.mime')"
        )
    )

    op.drop_index("ix_attachments_deleted_at", table_name="attachments")
    op.drop_index("ix_attachments_stored_filename", table_name="attachments")
    op.drop_index("ix_attachments_checksum", table_name="attachments")
    op.drop_index("ix_attachments_uploaded_by", table_name="attachments")
    op.drop_index("ix_attachments_object", table_name="attachments")
    op.drop_table("attachments")

    op.create_table(
        "attachments",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("complaint_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("storage_key", sa.String(length=512), nullable=False),
        sa.Column("content_type", sa.String(length=128), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=True),
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
            name="fk_attachments_complaint_id_complaints",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["uploaded_by"],
            ["users.id"],
            name="fk_attachments_uploaded_by_users",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_attachments"),
    )
    op.create_index("ix_attachments_complaint_id", "attachments", ["complaint_id"])
    op.create_index("ix_attachments_deleted_at", "attachments", ["deleted_at"])
    op.create_index("ix_attachments_storage_key", "attachments", ["storage_key"])
    op.create_index("ix_attachments_uploaded_by", "attachments", ["uploaded_by"])
