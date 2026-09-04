"""Add branch-proposed HQ arrival slot columns on cm_batch1_complaints.

Revision ID: 0085_cm_b1_proposed_arrival
Revises: 0084_cm_hq_holidays
Create Date: 2026-08-17

Cabang may propose a date/time when escalating to Pusat; Pusat still decides
the final hq_arrival_date/hq_arrival_time via accept_and_schedule_at_hq /
schedule_hq_arrival. Proposed_* is advisory only, cleared once Pusat decides.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0085_cm_b1_proposed_arrival"
down_revision: Union[str, None] = "0084_cm_hq_holidays"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cm_batch1_complaints",
        sa.Column("proposed_arrival_date", sa.Date(), nullable=True),
    )
    op.add_column(
        "cm_batch1_complaints",
        sa.Column("proposed_arrival_time", sa.String(length=5), nullable=True),
    )
    op.add_column(
        "cm_batch1_complaints",
        sa.Column("proposed_by", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "cm_batch1_complaints",
        sa.Column("proposed_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("cm_batch1_complaints", "proposed_at")
    op.drop_column("cm_batch1_complaints", "proposed_by")
    op.drop_column("cm_batch1_complaints", "proposed_arrival_time")
    op.drop_column("cm_batch1_complaints", "proposed_arrival_date")
