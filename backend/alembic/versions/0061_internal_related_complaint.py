"""Add optional related Batch-1 Aggregate reference on Pengaduan Internal.

Revision ID: 0061_internal_related_complaint
Revises: 0060_internal_complaints
Create Date: 2026-08-08
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0061_internal_related_complaint"
down_revision: Union[str, None] = "0060_internal_complaints"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "internal_complaints",
        sa.Column("related_complaint_id", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "internal_complaints",
        sa.Column("related_complaint_number", sa.String(length=64), nullable=True),
    )
    op.create_index(
        "ix_internal_complaints_related_complaint_id",
        "internal_complaints",
        ["related_complaint_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_internal_complaints_related_complaint_id",
        table_name="internal_complaints",
    )
    op.drop_column("internal_complaints", "related_complaint_number")
    op.drop_column("internal_complaints", "related_complaint_id")
