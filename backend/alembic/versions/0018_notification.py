"""Add notification templates + queue tables and seed notification settings (TASK-030).

Revision ID: 0018_notification
Revises: 0017_attachments
Create Date: 2026-07-24

Soft-delete for templates uses is_active=False (table contract has no deleted_at).
No provider / worker / send path in this revision.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0018_notification"
down_revision: Union[str, None] = "0017_attachments"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_SEED_SETTINGS: tuple[dict[str, str | None], ...] = (
    {
        "key": "notification.enabled",
        "value": "true",
        "value_type": "BOOLEAN",
        "category": "notification",
        "visibility": "PROTECTED",
        "description": "Master switch for notification enqueue (foundation)",
    },
    {
        "key": "notification.default.channel",
        "value": "EMAIL",
        "value_type": "STRING",
        "category": "notification",
        "visibility": "PROTECTED",
        "description": "Default notification channel (EMAIL|WHATSAPP|PUSH)",
    },
    {
        "key": "notification.max.retry",
        "value": "3",
        "value_type": "INTEGER",
        "category": "notification",
        "visibility": "PROTECTED",
        "description": "Max delivery retries (stored for future worker; unused in TASK-030)",
    },
)


def upgrade() -> None:
    op.create_table(
        "notification_templates",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("channel", sa.String(length=30), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "is_active",
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
        sa.PrimaryKeyConstraint("id", name="pk_notification_templates"),
        sa.UniqueConstraint("code", name="uq_notification_templates_code"),
    )
    op.create_index(
        "ix_notification_templates_channel", "notification_templates", ["channel"]
    )
    op.create_index(
        "ix_notification_templates_is_active",
        "notification_templates",
        ["is_active"],
    )

    op.create_table(
        "notification_queue",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("template_code", sa.String(length=100), nullable=True),
        sa.Column("recipient", sa.String(length=255), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column(
            "retry_count",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_notification_queue"),
    )
    op.create_index(
        "ix_notification_queue_template_code",
        "notification_queue",
        ["template_code"],
    )
    op.create_index("ix_notification_queue_status", "notification_queue", ["status"])
    op.create_index(
        "ix_notification_queue_scheduled_at",
        "notification_queue",
        ["scheduled_at"],
    )
    op.create_index(
        "ix_notification_queue_created_at", "notification_queue", ["created_at"]
    )

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
            "'notification.enabled', 'notification.default.channel', "
            "'notification.max.retry')"
        )
    )

    op.drop_index("ix_notification_queue_created_at", table_name="notification_queue")
    op.drop_index(
        "ix_notification_queue_scheduled_at", table_name="notification_queue"
    )
    op.drop_index("ix_notification_queue_status", table_name="notification_queue")
    op.drop_index(
        "ix_notification_queue_template_code", table_name="notification_queue"
    )
    op.drop_table("notification_queue")

    op.drop_index(
        "ix_notification_templates_is_active", table_name="notification_templates"
    )
    op.drop_index(
        "ix_notification_templates_channel", table_name="notification_templates"
    )
    op.drop_table("notification_templates")
