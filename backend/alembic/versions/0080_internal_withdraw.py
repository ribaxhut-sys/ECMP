"""Pengaduan Internal — withdraw / cancel-request columns.

Revision ID: 0080_internal_withdraw
Revises: 0079_user_initials
Create Date: 2026-08-17

Mode A: branch may withdraw before Pusat receives (WITHDRAWN, no Pusat
notify). After receive, branch may request withdraw; Pusat decides.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0080_internal_withdraw"
down_revision: Union[str, None] = "0079_user_initials"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE = "internal_complaints"


def upgrade() -> None:
    op.add_column(
        _TABLE, sa.Column("withdraw_request_status", sa.String(16), nullable=True)
    )
    op.add_column(
        _TABLE, sa.Column("withdraw_request_reason", sa.Text(), nullable=True)
    )
    op.add_column(
        _TABLE, sa.Column("withdraw_requested_by", sa.String(128), nullable=True)
    )
    op.add_column(
        _TABLE,
        sa.Column("withdraw_requested_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        _TABLE, sa.Column("withdraw_decided_by", sa.String(128), nullable=True)
    )
    op.add_column(
        _TABLE,
        sa.Column("withdraw_decided_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        _TABLE, sa.Column("withdraw_decision_reason", sa.Text(), nullable=True)
    )
    op.add_column(
        _TABLE, sa.Column("withdrawn_by", sa.String(128), nullable=True)
    )
    op.add_column(
        _TABLE,
        sa.Column("withdrawn_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(_TABLE, sa.Column("withdraw_reason", sa.Text(), nullable=True))
    op.create_index(
        "ix_internal_complaints_withdraw_request_status",
        _TABLE,
        ["withdraw_request_status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_internal_complaints_withdraw_request_status", table_name=_TABLE
    )
    op.drop_column(_TABLE, "withdraw_reason")
    op.drop_column(_TABLE, "withdrawn_at")
    op.drop_column(_TABLE, "withdrawn_by")
    op.drop_column(_TABLE, "withdraw_decision_reason")
    op.drop_column(_TABLE, "withdraw_decided_at")
    op.drop_column(_TABLE, "withdraw_decided_by")
    op.drop_column(_TABLE, "withdraw_requested_at")
    op.drop_column(_TABLE, "withdraw_requested_by")
    op.drop_column(_TABLE, "withdraw_request_reason")
    op.drop_column(_TABLE, "withdraw_request_status")
