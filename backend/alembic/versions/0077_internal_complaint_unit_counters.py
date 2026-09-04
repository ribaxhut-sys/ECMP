"""Pengaduan Internal — per-unit-per-month number counter.

Revision ID: 0077_internal_unit_counters
Revises: 0076_internal_transfer_request
Create Date: 2026-08-14

New format ``PI-{UNIT}-{YYMM}-{NNN}`` (e.g. ``PI-TAB-2608-001``), mirroring
cm_batch1's ``UNIT-YYMM-NNNN`` vocabulary via the same ``resolve_unit_code``.
The old ``internal_complaint_number_counters`` table (global per-year,
``PI-YYYY-NNNNNN``) is left untouched — existing lab rows are never remapped,
and that table simply stops being written to.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0077_internal_unit_counters"
down_revision: Union[str, None] = "0076_internal_transfer_request"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "internal_complaint_unit_counters",
        sa.Column("unit_code", sa.String(8), primary_key=True),
        sa.Column("period", sa.Integer(), primary_key=True),
        sa.Column("last_seq", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_table("internal_complaint_unit_counters")
