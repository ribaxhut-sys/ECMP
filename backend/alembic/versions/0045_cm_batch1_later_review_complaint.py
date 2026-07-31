"""Add nullable complaint_id to cm_batch1_later_review_items (M3d / EX-G).

Revision ID: 0045_cm_batch1_later_review_complaint
Revises: 0044_admin_rbac_repair
Create Date: 2026-07-31

Mode A: optional Aggregate Complaint anchor on later-review work items when
known (attachment bind failure). Pre-create degraded duplicate remains null.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0045_cm_batch1_later_review_complaint"
down_revision: Union[str, None] = "0044_admin_rbac_repair"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cm_batch1_later_review_items",
        sa.Column("complaint_id", sa.String(length=64), nullable=True),
    )
    op.create_index(
        "ix_cm_batch1_later_review_complaint_id",
        "cm_batch1_later_review_items",
        ["complaint_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_cm_batch1_later_review_complaint_id",
        table_name="cm_batch1_later_review_items",
    )
    op.drop_column("cm_batch1_later_review_items", "complaint_id")
