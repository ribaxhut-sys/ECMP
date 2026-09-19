"""Pengaduan Internal — return-for-completion (berkas kurang).

Revision ID: 0086_internal_completion_return
Revises: 0085_cm_b1_proposed_arrival
Create Date: 2026-08-19

Mode A: Pusat may return a branch-owned ticket to the owner unit when
documents are incomplete. Not WITHDRAWN. completion_request_status=PENDING
until the branch resends to Pusat.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0086_internal_completion_return"
down_revision: Union[str, None] = "0085_cm_b1_proposed_arrival"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE = "internal_complaints"


def upgrade() -> None:
    op.add_column(
        _TABLE, sa.Column("completion_request_status", sa.String(16), nullable=True)
    )
    op.add_column(
        _TABLE, sa.Column("completion_return_reason", sa.Text(), nullable=True)
    )
    op.add_column(
        _TABLE, sa.Column("completion_returned_by", sa.String(128), nullable=True)
    )
    op.add_column(
        _TABLE,
        sa.Column(
            "completion_returned_at", sa.DateTime(timezone=True), nullable=True
        ),
    )
    op.create_index(
        "ix_internal_complaints_completion_request_status",
        _TABLE,
        ["completion_request_status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_internal_complaints_completion_request_status", table_name=_TABLE
    )
    op.drop_column(_TABLE, "completion_returned_at")
    op.drop_column(_TABLE, "completion_returned_by")
    op.drop_column(_TABLE, "completion_return_reason")
    op.drop_column(_TABLE, "completion_request_status")
