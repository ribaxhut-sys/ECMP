"""CM Batch 1 event outbox (S2 Task 04) — persist only, no publisher.

Revision ID: 0043_cm_batch1_foundation
Revises: 0042_cm_batch1_attachment
Create Date: 2026-07-29

Creates:
- cm_batch1_outbox (EVT-CM-* unpublished payloads)

Does NOT modify 0040–0042. Reuses platform audit_logs + timeline_entries.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0043_cm_batch1_foundation"
down_revision: Union[str, None] = "0042_cm_batch1_attachment"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cm_batch1_outbox",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("event_id", sa.String(length=32), nullable=False),
        sa.Column("event_name", sa.String(length=128), nullable=False),
        sa.Column("aggregate_type", sa.String(length=64), nullable=False),
        sa.Column("aggregate_id", sa.String(length=64), nullable=True),
        sa.Column("idempotency_key", sa.String(length=256), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_cm_batch1_outbox"),
        sa.UniqueConstraint(
            "idempotency_key", name="uq_cm_batch1_outbox_idempotency_key"
        ),
    )
    op.create_index("ix_cm_batch1_outbox_event_id", "cm_batch1_outbox", ["event_id"])
    op.create_index("ix_cm_batch1_outbox_status", "cm_batch1_outbox", ["status"])
    op.create_index(
        "ix_cm_batch1_outbox_aggregate",
        "cm_batch1_outbox",
        ["aggregate_type", "aggregate_id"],
    )
    op.create_index(
        "ix_cm_batch1_outbox_occurred_at", "cm_batch1_outbox", ["occurred_at"]
    )


def downgrade() -> None:
    op.drop_index("ix_cm_batch1_outbox_occurred_at", table_name="cm_batch1_outbox")
    op.drop_index("ix_cm_batch1_outbox_aggregate", table_name="cm_batch1_outbox")
    op.drop_index("ix_cm_batch1_outbox_status", table_name="cm_batch1_outbox")
    op.drop_index("ix_cm_batch1_outbox_event_id", table_name="cm_batch1_outbox")
    op.drop_table("cm_batch1_outbox")
