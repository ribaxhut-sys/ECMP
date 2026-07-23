"""Add appointment check-in fields (TASK-015).

Revision ID: 0008_appointment_checkin
Revises: 0007_appointments
Create Date: 2026-07-23
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0008_appointment_checkin"
down_revision: Union[str, None] = "0007_appointments"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "appointments",
        sa.Column("checked_in_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "appointments",
        sa.Column("checked_in_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "appointments",
        sa.Column("checkin_notes", sa.Text(), nullable=True),
    )
    op.create_index(
        "ix_appointments_checked_in_at",
        "appointments",
        ["checked_in_at"],
    )
    op.create_index(
        "ix_appointments_checked_in_by",
        "appointments",
        ["checked_in_by"],
    )


def downgrade() -> None:
    op.drop_index("ix_appointments_checked_in_by", table_name="appointments")
    op.drop_index("ix_appointments_checked_in_at", table_name="appointments")
    op.drop_column("appointments", "checkin_notes")
    op.drop_column("appointments", "checked_in_by")
    op.drop_column("appointments", "checked_in_at")
