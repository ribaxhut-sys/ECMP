"""Per-user Pusat read receipt for the HQ queue badge.

Revision ID: 0107_cm_pusat_queue_seen
Revises: 0106_cm_case_inbox_receipts
Create Date: 2026-08-25

One row per (complaint, user), written when a Pusat user opens the complaint
or one of its Cases. Derived-unread: the badge compares ``seen_at`` with the
last branch movement, so no fan-out row is created at escalation time.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0107_cm_pusat_queue_seen"
down_revision: Union[str, None] = "0106_cm_case_inbox_receipts"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cm_pusat_queue_seen",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("complaint_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column(
            "seen_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["complaint_id"],
            ["cm_batch1_complaints.id"],
            name="fk_cm_pusat_queue_seen_complaint_id",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "complaint_id",
            "user_id",
            name="uq_cm_pusat_queue_seen_pair",
        ),
    )
    op.create_index(
        "ix_cm_pusat_queue_seen_user_id",
        "cm_pusat_queue_seen",
        ["user_id"],
    )
    op.create_index(
        "ix_cm_pusat_queue_seen_complaint_id",
        "cm_pusat_queue_seen",
        ["complaint_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_cm_pusat_queue_seen_complaint_id",
        table_name="cm_pusat_queue_seen",
    )
    op.drop_index(
        "ix_cm_pusat_queue_seen_user_id",
        table_name="cm_pusat_queue_seen",
    )
    op.drop_table("cm_pusat_queue_seen")
