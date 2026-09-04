"""Mode A operational handling claim (not BQ-006 Assigned User).

Revision ID: 0078_cm_case_handling_claimed_by
Revises: 0077_internal_unit_counters
Create Date: 2026-08-14

Adds ``cm_cases.handling_claimed_by`` — who is currently working the Case.
Existing rows stay NULL so Tangani remains available until the first claim.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0078_cm_case_handling_claimed_by"
down_revision: Union[str, None] = "0077_internal_unit_counters"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cm_cases",
        sa.Column("handling_claimed_by", sa.String(length=128), nullable=True),
    )
    op.create_index(
        "ix_cm_cases_handling_claimed_by",
        "cm_cases",
        ["handling_claimed_by"],
    )


def downgrade() -> None:
    op.drop_index("ix_cm_cases_handling_claimed_by", table_name="cm_cases")
    op.drop_column("cm_cases", "handling_claimed_by")
