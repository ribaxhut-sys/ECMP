"""Create cm_hq_holidays table (HQ arrival schedule holiday calendar).

Revision ID: 0084_cm_hq_holidays
Revises: 0083_hq_schedule_settings
Create Date: 2026-08-17
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0084_cm_hq_holidays"
down_revision: Union[str, None] = "0083_hq_schedule_settings"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cm_hq_holidays",
        sa.Column("holiday_date", sa.Date(), nullable=False),
        sa.Column("label", sa.String(length=200), nullable=False),
        sa.Column("created_by", sa.String(length=128), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("holiday_date", name="pk_cm_hq_holidays"),
    )


def downgrade() -> None:
    op.drop_table("cm_hq_holidays")
