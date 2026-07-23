"""Add appointment no-show fields (TASK-017).

Revision ID: 0010_appointment_no_show
Revises: 0009_appointment_completion
Create Date: 2026-07-23
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0010_appointment_no_show"
down_revision: Union[str, None] = "0009_appointment_completion"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "appointments",
        sa.Column("no_show_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "appointments",
        sa.Column("no_show_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "appointments",
        sa.Column("no_show_reason", sa.Text(), nullable=True),
    )
    op.create_index(
        "ix_appointments_no_show_at",
        "appointments",
        ["no_show_at"],
    )
    op.create_index(
        "ix_appointments_no_show_by",
        "appointments",
        ["no_show_by"],
    )


def downgrade() -> None:
    op.drop_index("ix_appointments_no_show_by", table_name="appointments")
    op.drop_index("ix_appointments_no_show_at", table_name="appointments")
    op.drop_column("appointments", "no_show_reason")
    op.drop_column("appointments", "no_show_by")
    op.drop_column("appointments", "no_show_at")
