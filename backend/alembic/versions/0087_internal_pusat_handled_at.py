"""Pengaduan Internal — sticky Pusat-handled timestamp for WITHDRAWN visibility.

Revision ID: 0087_internal_pusat_handled_at
Revises: 0086_internal_completion_return
Create Date: 2026-08-19

Pusat list/GET hide unilaterally withdrawn tickets unless Pusat already
acted (RECEIVED, RETURNED_FOR_COMPLETION, or WITHDRAW_REQUEST_APPROVED).
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0087_internal_pusat_handled_at"
down_revision: Union[str, None] = "0086_internal_completion_return"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE = "internal_complaints"


def upgrade() -> None:
    op.add_column(
        _TABLE,
        sa.Column("pusat_handled_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute(
        """
        UPDATE internal_complaints AS c
        SET pusat_handled_at = sub.first_at
        FROM (
            SELECT complaint_id, MIN(occurred_at) AS first_at
            FROM internal_complaint_events
            WHERE event_type IN (
                'RECEIVED',
                'RETURNED_FOR_COMPLETION',
                'WITHDRAW_REQUEST_APPROVED'
            )
            GROUP BY complaint_id
        ) AS sub
        WHERE c.id = sub.complaint_id
          AND c.pusat_handled_at IS NULL
        """
    )


def downgrade() -> None:
    op.drop_column(_TABLE, "pusat_handled_at")
