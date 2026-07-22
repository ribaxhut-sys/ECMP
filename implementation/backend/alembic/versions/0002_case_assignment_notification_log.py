"""Revision 0002: case assignment columns + notification_log (Sprint-02B).

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-22
"""

import sqlalchemy as sa

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("cases", sa.Column("assignee_id", sa.String(64), nullable=True))
    op.add_column("cases", sa.Column("unit_id", sa.String(64), nullable=True))
    op.create_index("ix_cases_assignee_id", "cases", ["assignee_id"])
    op.create_index("ix_cases_unit_id", "cases", ["unit_id"])

    op.create_table(
        "notification_log",
        sa.Column("notification_id", sa.String(36), primary_key=True),
        sa.Column("outbox_id", sa.String(36), nullable=False),
        sa.Column("event_id", sa.String(16), nullable=False),
        sa.Column("event_name", sa.String(64), nullable=False),
        sa.Column("payload", sa.JSON, nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("outbox_id", name="uq_notification_log_outbox_id"),
    )
    op.create_index("ix_notification_log_event_id", "notification_log", ["event_id"])


def downgrade() -> None:
    op.drop_table("notification_log")
    op.drop_index("ix_cases_unit_id", table_name="cases")
    op.drop_index("ix_cases_assignee_id", table_name="cases")
    op.drop_column("cases", "unit_id")
    op.drop_column("cases", "assignee_id")
