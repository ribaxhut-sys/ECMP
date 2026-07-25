"""CAPABILITY-009 — extend notification_queue for domain Notification fields.

Revision ID: 0033_notification_domain
Revises: 0032_complaint_sla
Create Date: 2026-07-25

Adds type/channel/subject/message/failed_at plus indexes on channel and
recipient. Does not implement transport adapters or schedulers.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0033_notification_domain"
down_revision: Union[str, None] = "0032_complaint_sla"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "notification_queue",
        sa.Column("notification_type", sa.String(length=80), nullable=True),
    )
    op.add_column(
        "notification_queue",
        sa.Column("channel", sa.String(length=30), nullable=True),
    )
    op.add_column(
        "notification_queue",
        sa.Column("subject", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "notification_queue",
        sa.Column("message", sa.Text(), nullable=True),
    )
    op.add_column(
        "notification_queue",
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Backfill channel/subject/message from JSON payload where present.
    op.execute(
        sa.text(
            """
            UPDATE notification_queue
            SET
              channel = COALESCE(channel, payload->>'channel'),
              subject = COALESCE(subject, payload->>'subject'),
              message = COALESCE(message, payload->>'content')
            WHERE payload IS NOT NULL
            """
        )
    )

    op.create_index(
        "ix_notification_queue_channel",
        "notification_queue",
        ["channel"],
    )
    op.create_index(
        "ix_notification_queue_recipient",
        "notification_queue",
        ["recipient"],
    )
    # status + created_at already indexed in 0018_notification


def downgrade() -> None:
    op.drop_index("ix_notification_queue_recipient", table_name="notification_queue")
    op.drop_index("ix_notification_queue_channel", table_name="notification_queue")
    op.drop_column("notification_queue", "failed_at")
    op.drop_column("notification_queue", "message")
    op.drop_column("notification_queue", "subject")
    op.drop_column("notification_queue", "channel")
    op.drop_column("notification_queue", "notification_type")
