"""Case-scoped escalate to Pusat (DEC-029 / API-520 lab).

Revision ID: 0098_case_escalate_to_pusat
Revises: 0097_hq_destination_unit
Create Date: 2026-08-22

Flag + reason live on the Case. originating ``owning_unit_id`` is not
overwritten (DEC-028 / FR-CM-010). Mode A does not persist status ESCALATED
(BQ-009).
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0098_case_escalate_to_pusat"
down_revision: Union[str, None] = "0097_hq_destination_unit"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cm_cases",
        sa.Column(
            "escalated_to_pusat",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "cm_cases",
        sa.Column("escalation_reason", sa.Text(), nullable=True),
    )
    op.add_column(
        "cm_cases",
        sa.Column("escalated_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("cm_cases", "escalated_at")
    op.drop_column("cm_cases", "escalation_reason")
    op.drop_column("cm_cases", "escalated_to_pusat")
