"""Record the Pusat officer who accepted an escalation.

Revision ID: 0108_hq_accepted_by
Revises: 0107_cm_pusat_queue_seen
Create Date: 2026-08-26

``accept_at_hq`` only stamped ``hq_accepted_at``, so the "accepted, not yet
scheduled" phase had no actor to show as the current handler on the work
lists. Backfill uses ``hq_destination_set_by``: accept-and-schedule writes
both in one transaction, so for existing rows that column *is* the accepting
officer. Rows accepted without a schedule stay NULL — nothing to recover from
the columns; the actor only exists in ``timeline_entries``.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0108_hq_accepted_by"
down_revision: Union[str, None] = "0107_cm_pusat_queue_seen"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cm_batch1_complaints",
        sa.Column("hq_accepted_by", sa.String(length=128), nullable=True),
    )
    op.execute(
        """
        UPDATE cm_batch1_complaints
        SET hq_accepted_by = hq_destination_set_by
        WHERE hq_accepted_at IS NOT NULL
          AND hq_accepted_by IS NULL
          AND hq_destination_set_by IS NOT NULL
        """
    )


def downgrade() -> None:
    op.drop_column("cm_batch1_complaints", "hq_accepted_by")
