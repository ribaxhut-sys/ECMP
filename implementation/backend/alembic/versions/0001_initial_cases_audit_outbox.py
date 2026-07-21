"""Revision 0: cases, audit_log, outbox (G0 platform floor per DEC-002 / ADR-004).

Revision ID: 0001
Revises:
Create Date: 2026-07-21
"""

import sqlalchemy as sa

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cases",
        sa.Column("case_id", sa.String(32), primary_key=True),
        sa.Column("customer_id", sa.String(64), nullable=False),
        sa.Column("case_type", sa.String(32), nullable=False),
        sa.Column("priority", sa.String(16), nullable=False),
        sa.Column("subject", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("channel", sa.String(32), nullable=True),
        sa.Column("customer_verified", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.String(64), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_by", sa.String(64), nullable=False),
    )
    op.create_index("ix_cases_customer_id", "cases", ["customer_id"])

    op.create_table(
        "audit_log",
        sa.Column("log_id", sa.String(36), primary_key=True),
        sa.Column("actor_user_id", sa.String(64), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("entity_type", sa.String(64), nullable=False),
        sa.Column("entity_id", sa.String(64), nullable=False),
        sa.Column("new_value", sa.JSON, nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_log_entity", "audit_log", ["entity_type", "entity_id"])

    op.create_table(
        "outbox",
        sa.Column("outbox_id", sa.String(36), primary_key=True),
        sa.Column("event_id", sa.String(16), nullable=False),
        sa.Column("event_name", sa.String(64), nullable=False),
        sa.Column("payload", sa.JSON, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_outbox_unpublished", "outbox", ["published_at", "created_at"])


def downgrade() -> None:
    op.drop_table("outbox")
    op.drop_table("audit_log")
    op.drop_table("cases")
