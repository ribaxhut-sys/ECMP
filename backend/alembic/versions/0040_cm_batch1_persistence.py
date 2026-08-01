"""CM Batch 1 Aggregate persistence tables (S2 Task 01).

Revision ID: 0040_cm_batch1_persistence
Revises: 0039_admin_rbac_repair
Create Date: 2026-07-29

Creates:
- cm_batch1_complaints (Aggregate Root; case_created always false)
- cm_batch1_idempotency (Request Id)
- cm_batch1_channel_messages (Channel Message Id)
- cm_batch1_customer_locks (FR-002 confirm)
- cm_batch1_number_counters (CM-######## generator)

Independent of legacy ``complaints`` / ``complaint_cases``. No Case FK.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0040_cm_batch1_persistence"
down_revision: Union[str, None] = "0039_admin_rbac_repair"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cm_batch1_complaints",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("complaint_number", sa.String(length=32), nullable=False),
        sa.Column("customer_id", sa.String(length=128), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("channel", sa.String(length=64), nullable=False),
        sa.Column("subject", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("priority", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column(
            "case_created",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("created_by", sa.String(length=128), nullable=True),
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
        sa.PrimaryKeyConstraint("id", name="pk_cm_batch1_complaints"),
        sa.UniqueConstraint(
            "complaint_number", name="uq_cm_batch1_complaints_number"
        ),
    )
    op.create_index(
        "ix_cm_batch1_complaints_customer_id",
        "cm_batch1_complaints",
        ["customer_id"],
    )
    op.create_index(
        "ix_cm_batch1_complaints_status",
        "cm_batch1_complaints",
        ["status"],
    )
    op.create_index(
        "ix_cm_batch1_complaints_created_at",
        "cm_batch1_complaints",
        ["created_at"],
    )

    op.create_table(
        "cm_batch1_idempotency",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("request_id", sa.String(length=256), nullable=False),
        sa.Column("complaint_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["complaint_id"],
            ["cm_batch1_complaints.id"],
            name="fk_cm_batch1_idempotency_complaint_id_cm_batch1_complaints",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_cm_batch1_idempotency"),
        sa.UniqueConstraint(
            "request_id", name="uq_cm_batch1_idempotency_request_id"
        ),
    )
    op.create_index(
        "ix_cm_batch1_idempotency_complaint_id",
        "cm_batch1_idempotency",
        ["complaint_id"],
    )

    op.create_table(
        "cm_batch1_channel_messages",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("channel_message_id", sa.String(length=256), nullable=False),
        sa.Column("complaint_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["complaint_id"],
            ["cm_batch1_complaints.id"],
            name="fk_cm_batch1_channel_messages_complaint_id_cm_batch1_complaints",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_cm_batch1_channel_messages"),
        sa.UniqueConstraint(
            "channel_message_id", name="uq_cm_batch1_channel_message_id"
        ),
    )
    op.create_index(
        "ix_cm_batch1_channel_messages_complaint_id",
        "cm_batch1_channel_messages",
        ["complaint_id"],
    )

    op.create_table(
        "cm_batch1_customer_locks",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("principal_key", sa.String(length=128), nullable=False),
        sa.Column("customer_id", sa.String(length=128), nullable=False),
        sa.Column(
            "locked_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_cm_batch1_customer_locks"),
        sa.UniqueConstraint(
            "principal_key", name="uq_cm_batch1_customer_locks_principal"
        ),
    )

    op.create_table(
        "cm_batch1_number_counters",
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("value", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("name", name="pk_cm_batch1_number_counters"),
    )
    op.execute(
        "INSERT INTO cm_batch1_number_counters (name, value) "
        "VALUES ('complaint_number', 0)"
    )


def downgrade() -> None:
    op.drop_table("cm_batch1_number_counters")
    op.drop_table("cm_batch1_customer_locks")
    op.drop_index(
        "ix_cm_batch1_channel_messages_complaint_id",
        table_name="cm_batch1_channel_messages",
    )
    op.drop_table("cm_batch1_channel_messages")
    op.drop_index(
        "ix_cm_batch1_idempotency_complaint_id",
        table_name="cm_batch1_idempotency",
    )
    op.drop_table("cm_batch1_idempotency")
    op.drop_index(
        "ix_cm_batch1_complaints_created_at",
        table_name="cm_batch1_complaints",
    )
    op.drop_index(
        "ix_cm_batch1_complaints_status",
        table_name="cm_batch1_complaints",
    )
    op.drop_index(
        "ix_cm_batch1_complaints_customer_id",
        table_name="cm_batch1_complaints",
    )
    op.drop_table("cm_batch1_complaints")
