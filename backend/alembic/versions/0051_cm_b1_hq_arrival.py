"""Add HQ arrival schedule columns on cm_batch1_complaints.

Revision ID: 0051_cm_b1_hq_arrival
Revises: 0050_cm_b1_hq_accepted
Create Date: 2026-08-07

Lab Mode A: after Pusat accepts (hq_accepted_at), scheduler may set
customer arrival date + time without foundation Appointment (API-305).
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0051_cm_b1_hq_arrival"
down_revision: Union[str, None] = "0050_cm_b1_hq_accepted"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cm_batch1_complaints",
        sa.Column("hq_arrival_date", sa.Date(), nullable=True),
    )
    op.add_column(
        "cm_batch1_complaints",
        sa.Column("hq_arrival_time", sa.String(length=5), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("cm_batch1_complaints", "hq_arrival_time")
    op.drop_column("cm_batch1_complaints", "hq_arrival_date")
