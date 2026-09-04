"""Case number counters: per-unit-per-month key (UNIT-YYMM-NNNN).

Revision ID: 0096_case_number_unit_month
Revises: 0095_case_number_four_digits
Create Date: 2026-08-22

BQ-004 (Product Owner / DEC-028): Case identity is ``TAB-2608-0001`` (independent of
``CMTAB-2608-0001`` complaints). Counters move from a per-year integer PK
to ``cs:UNIT:YYYYMM``. Existing rows are dropped — lab will recreate data.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0096_case_number_unit_month"
down_revision: Union[str, None] = "0095_case_number_four_digits"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("cm_case_number_counters")
    op.create_table(
        "cm_case_number_counters",
        sa.Column("name", sa.String(length=64), primary_key=True),
        sa.Column("last_seq", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_table("cm_case_number_counters")
    op.create_table(
        "cm_case_number_counters",
        sa.Column("year", sa.Integer(), primary_key=True),
        sa.Column("last_seq", sa.Integer(), nullable=False, server_default="0"),
    )
