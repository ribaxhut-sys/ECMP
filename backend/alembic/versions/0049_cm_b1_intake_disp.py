"""Add intake_disposition on cm_batch1_complaints (escalate pending label).

Revision ID: 0049_cm_b1_intake_disp
Revises: 0048_cm_b1_att_customer
Create Date: 2026-08-06

Stores intake path without overloading Aggregate status (REGISTERED|CLOSED).
Backfills escalate marker from description text used by Mode A intake.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0049_cm_b1_intake_disp"
down_revision: Union[str, None] = "0048_cm_b1_att_customer"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cm_batch1_complaints",
        sa.Column("intake_disposition", sa.String(length=64), nullable=True),
    )
    op.create_index(
        "ix_cm_batch1_complaints_intake_disposition",
        "cm_batch1_complaints",
        ["intake_disposition"],
    )
    op.execute(
        sa.text(
            """
            UPDATE cm_batch1_complaints
            SET intake_disposition = 'ESCALATE_PENDING_APPROVAL'
            WHERE status = 'REGISTERED'
              AND intake_disposition IS NULL
              AND description LIKE '%Ajuan eskalasi:%'
            """
        )
    )
    op.execute(
        sa.text(
            """
            UPDATE cm_batch1_complaints
            SET intake_disposition = 'BRANCH_CLOSED'
            WHERE status = 'CLOSED'
              AND intake_disposition IS NULL
              AND description LIKE '%Penyelesaian:%'
            """
        )
    )


def downgrade() -> None:
    op.drop_index(
        "ix_cm_batch1_complaints_intake_disposition",
        table_name="cm_batch1_complaints",
    )
    op.drop_column("cm_batch1_complaints", "intake_disposition")
