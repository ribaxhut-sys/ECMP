"""Rename legacy audit_logs and create platform audit_logs (TASK-031).

Revision ID: 0019_audit
Revises: 0018_notification
Create Date: 2026-07-24

Legacy Complaint/Auth/Resolution writers keep using ``audit_logs_legacy``
(same columns). New platform AuditService uses ``audit_logs`` (TASK-031
schema). No Complaint domain logic changes.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0019_audit"
down_revision: Union[str, None] = "0018_notification"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Preserve existing append-only rows for Complaint/Auth/Resolution.
    op.rename_table("audit_logs", "audit_logs_legacy")
    op.execute(
        sa.text(
            "ALTER INDEX IF EXISTS ix_audit_logs_action "
            "RENAME TO ix_audit_logs_legacy_action"
        )
    )
    op.execute(
        sa.text(
            "ALTER INDEX IF EXISTS ix_audit_logs_entity "
            "RENAME TO ix_audit_logs_legacy_entity"
        )
    )
    op.execute(
        sa.text(
            "ALTER INDEX IF EXISTS ix_audit_logs_occurred_at "
            "RENAME TO ix_audit_logs_legacy_occurred_at"
        )
    )
    op.execute(
        sa.text(
            "ALTER INDEX IF EXISTS ix_audit_logs_actor_user_id "
            "RENAME TO ix_audit_logs_legacy_actor_user_id"
        )
    )
    op.execute(
        sa.text(
            "ALTER TABLE audit_logs_legacy "
            "RENAME CONSTRAINT pk_audit_logs TO pk_audit_logs_legacy"
        )
    )

    op.create_table(
        "audit_logs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=100), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_name", sa.String(length=255), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("old_values", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("new_values", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_audit_logs"),
    )
    op.create_index("ix_audit_logs_event_type", "audit_logs", ["event_type"])
    op.create_index(
        "ix_audit_logs_entity", "audit_logs", ["entity_type", "entity_id"]
    )
    op.create_index("ix_audit_logs_actor_id", "audit_logs", ["actor_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_audit_logs_created_at", table_name="audit_logs")
    op.drop_index("ix_audit_logs_action", table_name="audit_logs")
    op.drop_index("ix_audit_logs_actor_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_entity", table_name="audit_logs")
    op.drop_index("ix_audit_logs_event_type", table_name="audit_logs")
    op.drop_table("audit_logs")

    op.execute(
        sa.text(
            "ALTER TABLE audit_logs_legacy "
            "RENAME CONSTRAINT pk_audit_logs_legacy TO pk_audit_logs"
        )
    )
    op.execute(
        sa.text(
            "ALTER INDEX IF EXISTS ix_audit_logs_legacy_action "
            "RENAME TO ix_audit_logs_action"
        )
    )
    op.execute(
        sa.text(
            "ALTER INDEX IF EXISTS ix_audit_logs_legacy_entity "
            "RENAME TO ix_audit_logs_entity"
        )
    )
    op.execute(
        sa.text(
            "ALTER INDEX IF EXISTS ix_audit_logs_legacy_occurred_at "
            "RENAME TO ix_audit_logs_occurred_at"
        )
    )
    op.execute(
        sa.text(
            "ALTER INDEX IF EXISTS ix_audit_logs_legacy_actor_user_id "
            "RENAME TO ix_audit_logs_actor_user_id"
        )
    )
    op.rename_table("audit_logs_legacy", "audit_logs")
