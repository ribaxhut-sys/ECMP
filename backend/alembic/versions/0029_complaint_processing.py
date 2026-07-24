"""Add Complaint resolution columns (CAPABILITY-005).

Revision ID: 0029_complaint_processing
Revises: 0028_complaint_domain_foundation
Create Date: 2026-07-24

Nullable resolution fields — backward compatible with existing complaint_cases rows.
No Timeline / Assignment / Escalation tables.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0029_complaint_processing"
down_revision: Union[str, None] = "0028_complaint_domain_foundation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "complaint_cases",
        sa.Column("resolution_summary", sa.Text(), nullable=True),
    )
    op.add_column(
        "complaint_cases",
        sa.Column("resolution_resolved_by", sa.String(length=200), nullable=True),
    )
    op.add_column(
        "complaint_cases",
        sa.Column(
            "resolution_resolved_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("complaint_cases", "resolution_resolved_at")
    op.drop_column("complaint_cases", "resolution_resolved_by")
    op.drop_column("complaint_cases", "resolution_summary")
