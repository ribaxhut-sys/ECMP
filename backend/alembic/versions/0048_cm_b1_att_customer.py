"""Add customer_id to cm_batch1_attachments for checksum scope (FR-004).

Revision ID: 0048_cm_b1_att_customer
Revises: 0047_bapenda_branch_master_data
Create Date: 2026-08-06

Duplicate checksum policy scopes by customer: identical bytes for different
customers MUST be allowed (Mode A intake / lab evidence reuse).
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0048_cm_b1_att_customer"
down_revision: Union[str, None] = "0047_bapenda_branch_master_data"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cm_batch1_attachments",
        sa.Column("customer_id", sa.String(length=128), nullable=True),
    )
    op.create_index(
        "ix_cm_batch1_attachments_customer_id",
        "cm_batch1_attachments",
        ["customer_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_cm_batch1_attachments_customer_id",
        table_name="cm_batch1_attachments",
    )
    op.drop_column("cm_batch1_attachments", "customer_id")
