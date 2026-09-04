"""Add kind / source / imported_at to cm_hq_holidays.

Revision ID: 0109_cm_hq_holiday_kind
Revises: 0108_hq_accepted_by
Create Date: 2026-08-28

National-holiday import (API-548/549) needs to distinguish libur nasional
from cuti bersama and keep a vendor trail when SKB is revised. Manual rows
stay NULL on kind/source/imported_at until labelled.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0109_cm_hq_holiday_kind"
down_revision: Union[str, None] = "0108_hq_accepted_by"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cm_hq_holidays",
        sa.Column("kind", sa.String(length=32), nullable=True),
    )
    op.add_column(
        "cm_hq_holidays",
        sa.Column("source", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "cm_hq_holidays",
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("cm_hq_holidays", "imported_at")
    op.drop_column("cm_hq_holidays", "source")
    op.drop_column("cm_hq_holidays", "kind")
