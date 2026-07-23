"""Add appointment completion fields and HO Engineer role (TASK-016).

Revision ID: 0009_appointment_completion
Revises: 0008_appointment_checkin
Create Date: 2026-07-23
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0009_appointment_completion"
down_revision: Union[str, None] = "0008_appointment_checkin"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "appointments",
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "appointments",
        sa.Column("completed_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "appointments",
        sa.Column("completion_notes", sa.Text(), nullable=True),
    )
    op.add_column(
        "appointments",
        sa.Column(
            "completion_result",
            sa.String(length=50),
            server_default="COMPLETED",
            nullable=False,
        ),
    )
    op.create_index(
        "ix_appointments_completed_at",
        "appointments",
        ["completed_at"],
    )
    op.create_index(
        "ix_appointments_completed_by",
        "appointments",
        ["completed_by"],
    )

    # Ensure Head Office Engineer / Admin roles exist for API-308 gates.
    op.execute(
        """
        INSERT INTO roles (id, code, name, description, is_active, created_at, updated_at)
        VALUES
          (gen_random_uuid(), 'HO_ENGINEER', 'Head Office Engineer',
           'Head Office Engineer — appointment completion (TASK-016)', true, now(), now()),
          (gen_random_uuid(), 'ADMIN', 'Administrator',
           'System administrator', true, now(), now())
        ON CONFLICT (code) DO NOTHING
        """
    )


def downgrade() -> None:
    op.drop_index("ix_appointments_completed_by", table_name="appointments")
    op.drop_index("ix_appointments_completed_at", table_name="appointments")
    op.drop_column("appointments", "completion_result")
    op.drop_column("appointments", "completion_notes")
    op.drop_column("appointments", "completed_by")
    op.drop_column("appointments", "completed_at")
