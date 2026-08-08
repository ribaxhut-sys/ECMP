"""Add decided_by/decided_at columns on cm_batch1_complaints.

Revision ID: 0053_cm_b1_decided_by
Revises: 0052_supervisor_role_read
Create Date: 2026-08-07

Records who resolved an intake-escalation decision (APPROVE/REJECT/CANCEL)
and when, as normalized columns on the Aggregate itself instead of only
inside the append-only outbox event payload (UM-BUG-006). Needed so
per-user work metrics ("escalations approved/rejected") can be computed
with a plain indexed query instead of scanning payload_json.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0053_cm_b1_decided_by"
down_revision: Union[str, None] = "0052_supervisor_role_read"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cm_batch1_complaints",
        sa.Column("decided_by", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "cm_batch1_complaints",
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_cm_batch1_complaints_decided_by",
        "cm_batch1_complaints",
        ["decided_by"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_cm_batch1_complaints_decided_by", table_name="cm_batch1_complaints"
    )
    op.drop_column("cm_batch1_complaints", "decided_at")
    op.drop_column("cm_batch1_complaints", "decided_by")
