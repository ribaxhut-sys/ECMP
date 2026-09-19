"""HQ arrival destination unit — which Pusat unit the taxpayer reports to.

Revision ID: 0097_hq_destination_unit
Revises: 0096_case_number_unit_month
Create Date: 2026-08-22

Pusat is not one door: an escalated taxpayer may be directed to CRO, to
Sekretariat, or to a Suban. The branch proposes a slot; Pusat decides the
final time **and** the destination unit, then informs the taxpayer itself.

Deliberately a separate column from ``owning_unit_id``: that one is the row
visibility source of truth and holds the originating branch — overwriting it
with a Pusat sub-unit would cut the originating branch off from its own
complaint (FR-CM-010: origin keeps read access).
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0097_hq_destination_unit"
down_revision: Union[str, None] = "0096_case_number_unit_month"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cm_batch1_complaints",
        sa.Column("hq_destination_unit_id", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "cm_batch1_complaints",
        sa.Column("hq_destination_set_by", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "cm_batch1_complaints",
        sa.Column(
            "hq_destination_set_at", sa.DateTime(timezone=True), nullable=True
        ),
    )
    op.create_index(
        "ix_cm_batch1_complaints_hq_destination_unit_id",
        "cm_batch1_complaints",
        ["hq_destination_unit_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_cm_batch1_complaints_hq_destination_unit_id",
        table_name="cm_batch1_complaints",
    )
    op.drop_column("cm_batch1_complaints", "hq_destination_set_at")
    op.drop_column("cm_batch1_complaints", "hq_destination_set_by")
    op.drop_column("cm_batch1_complaints", "hq_destination_unit_id")
