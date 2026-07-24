"""Add Queue persistence tables (TASK-063).

Revision ID: 0027_queue_persistence
Revises: 0026_complaint_source_target
Create Date: 2026-07-24

Creates queues, queue_tickets, queue_counters.
Migration only — no seed data.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0027_queue_persistence"
down_revision: Union[str, None] = "0026_complaint_source_target"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "queues",
        sa.Column("queue_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("policy", sa.String(length=32), nullable=False),
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
        sa.PrimaryKeyConstraint("queue_id", name="pk_queues"),
    )
    op.create_index("ix_queues_organization_id", "queues", ["organization_id"])
    op.create_index("ix_queues_status", "queues", ["status"])
    op.create_index(
        "ix_queues_organization_status",
        "queues",
        ["organization_id", "status"],
    )

    op.create_table(
        "queue_tickets",
        sa.Column("ticket_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("queue_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ticket_number", sa.String(length=64), nullable=False),
        sa.Column("priority", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["queue_id"],
            ["queues.queue_id"],
            name="fk_queue_tickets_queue_id_queues",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("ticket_id", name="pk_queue_tickets"),
        sa.UniqueConstraint(
            "queue_id",
            "ticket_number",
            name="uq_queue_tickets_queue_id_ticket_number",
        ),
    )
    op.create_index("ix_queue_tickets_queue_id", "queue_tickets", ["queue_id"])
    op.create_index("ix_queue_tickets_status", "queue_tickets", ["status"])
    op.create_index(
        "ix_queue_tickets_queue_status",
        "queue_tickets",
        ["queue_id", "status"],
    )
    op.create_index("ix_queue_tickets_created_at", "queue_tickets", ["created_at"])

    op.create_table(
        "queue_counters",
        sa.Column("counter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("queue_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
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
            ["queue_id"],
            ["queues.queue_id"],
            name="fk_queue_counters_queue_id_queues",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("counter_id", name="pk_queue_counters"),
    )
    op.create_index("ix_queue_counters_queue_id", "queue_counters", ["queue_id"])
    op.create_index("ix_queue_counters_status", "queue_counters", ["status"])


def downgrade() -> None:
    op.drop_index("ix_queue_counters_status", table_name="queue_counters")
    op.drop_index("ix_queue_counters_queue_id", table_name="queue_counters")
    op.drop_table("queue_counters")

    op.drop_index("ix_queue_tickets_created_at", table_name="queue_tickets")
    op.drop_index("ix_queue_tickets_queue_status", table_name="queue_tickets")
    op.drop_index("ix_queue_tickets_status", table_name="queue_tickets")
    op.drop_index("ix_queue_tickets_queue_id", table_name="queue_tickets")
    op.drop_table("queue_tickets")

    op.drop_index("ix_queues_organization_status", table_name="queues")
    op.drop_index("ix_queues_status", table_name="queues")
    op.drop_index("ix_queues_organization_id", table_name="queues")
    op.drop_table("queues")
