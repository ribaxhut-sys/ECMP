"""Pengaduan Internal — Agent transfer-request gate columns.

Revision ID: 0076_internal_transfer_request
Revises: 0075_internal_escalate_decide
Create Date: 2026-08-14

Adds the state an Agent-family transfer request travels through before a
Supervisor/Manager/Admin decides it (see ``internal:escalate-decide``,
migration 0075). All-nullable: existing rows (Supervisor/Manager direct
create+transfer, or plain local create) have no request and stay NULL.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0076_internal_transfer_request"
down_revision: Union[str, None] = "0075_internal_escalate_decide"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE = "internal_complaints"


def upgrade() -> None:
    op.add_column(
        _TABLE, sa.Column("transfer_request_status", sa.String(16), nullable=True)
    )
    op.add_column(
        _TABLE,
        sa.Column(
            "transfer_request_destination_unit_id", sa.String(128), nullable=True
        ),
    )
    op.add_column(
        _TABLE, sa.Column("transfer_request_reason", sa.Text(), nullable=True)
    )
    op.add_column(
        _TABLE, sa.Column("transfer_requested_by", sa.String(128), nullable=True)
    )
    op.add_column(
        _TABLE,
        sa.Column(
            "transfer_requested_at", sa.DateTime(timezone=True), nullable=True
        ),
    )
    op.add_column(
        _TABLE, sa.Column("transfer_decided_by", sa.String(128), nullable=True)
    )
    op.add_column(
        _TABLE,
        sa.Column("transfer_decided_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        _TABLE, sa.Column("transfer_decision_reason", sa.Text(), nullable=True)
    )
    op.create_index(
        "ix_internal_complaints_transfer_request_status",
        _TABLE,
        ["transfer_request_status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_internal_complaints_transfer_request_status", table_name=_TABLE
    )
    op.drop_column(_TABLE, "transfer_decision_reason")
    op.drop_column(_TABLE, "transfer_decided_at")
    op.drop_column(_TABLE, "transfer_decided_by")
    op.drop_column(_TABLE, "transfer_requested_at")
    op.drop_column(_TABLE, "transfer_requested_by")
    op.drop_column(_TABLE, "transfer_request_reason")
    op.drop_column(_TABLE, "transfer_request_destination_unit_id")
    op.drop_column(_TABLE, "transfer_request_status")
