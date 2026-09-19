"""Add hq_accepted_at on cm_batch1_complaints (HQ takeover lock).

Revision ID: 0050_cm_b1_hq_accepted
Revises: 0049_cm_b1_intake_disp
Create Date: 2026-08-07

When set, supervisor cannot CANCEL (Batalkan Eskalasi) an approved intake
escalation — Pusat has accepted/claimed the complaint.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0050_cm_b1_hq_accepted"
down_revision: Union[str, None] = "0049_cm_b1_intake_disp"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cm_batch1_complaints",
        sa.Column("hq_accepted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_cm_batch1_complaints_hq_accepted_at",
        "cm_batch1_complaints",
        ["hq_accepted_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_cm_batch1_complaints_hq_accepted_at",
        table_name="cm_batch1_complaints",
    )
    op.drop_column("cm_batch1_complaints", "hq_accepted_at")
