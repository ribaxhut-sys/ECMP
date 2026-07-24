"""Complaint multi-source / multi-target (TASK-042 / DEC-018).

Revision ID: 0026_complaint_source_target
Revises: 0025_permission_resolver
Create Date: 2026-07-24

Adds polymorphic source/target columns on complaints. Existing rows are
backfilled as CUSTOMER → BRANCH using customer_id / branch_id. customer_id
becomes nullable so non-customer sources can persist without a dummy customer.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0026_complaint_source_target"
down_revision: Union[str, None] = "0025_permission_resolver"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "complaints",
        sa.Column("source_type", sa.String(length=32), nullable=True),
    )
    op.add_column(
        "complaints",
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "complaints",
        sa.Column("target_type", sa.String(length=32), nullable=True),
    )
    op.add_column(
        "complaints",
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Safe backfill: legacy complaints are customer → branch.
    op.execute(
        sa.text(
            """
            UPDATE complaints
            SET
                source_type = 'CUSTOMER',
                source_id = customer_id,
                target_type = 'BRANCH',
                target_id = branch_id
            WHERE source_type IS NULL
            """
        )
    )

    op.alter_column("complaints", "source_type", nullable=False)
    op.alter_column("complaints", "source_id", nullable=False)
    op.alter_column("complaints", "target_type", nullable=False)
    # target_id stays nullable: legacy rows may have had null branch_id.

    op.alter_column("complaints", "customer_id", existing_type=postgresql.UUID(as_uuid=True), nullable=True)

    op.create_index("ix_complaints_source_type", "complaints", ["source_type"])
    op.create_index("ix_complaints_source_id", "complaints", ["source_id"])
    op.create_index("ix_complaints_target_type", "complaints", ["target_type"])
    op.create_index("ix_complaints_target_id", "complaints", ["target_id"])


def downgrade() -> None:
    op.drop_index("ix_complaints_target_id", table_name="complaints")
    op.drop_index("ix_complaints_target_type", table_name="complaints")
    op.drop_index("ix_complaints_source_id", table_name="complaints")
    op.drop_index("ix_complaints_source_type", table_name="complaints")

    # Restore legacy NOT NULL customer_id where safe.
    op.execute(
        sa.text(
            """
            UPDATE complaints
            SET customer_id = source_id
            WHERE customer_id IS NULL
              AND source_type = 'CUSTOMER'
              AND source_id IS NOT NULL
            """
        )
    )
    remaining = op.get_bind().execute(
        sa.text("SELECT COUNT(*) FROM complaints WHERE customer_id IS NULL")
    ).scalar()
    if remaining:
        raise RuntimeError(
            "Cannot downgrade 0026: complaints with null customer_id remain "
            f"({remaining}). Remove or migrate non-CUSTOMER sourced rows first."
        )
    op.alter_column(
        "complaints",
        "customer_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )

    op.drop_column("complaints", "target_id")
    op.drop_column("complaints", "target_type")
    op.drop_column("complaints", "source_id")
    op.drop_column("complaints", "source_type")
