"""Add appointments table (TASK-014).

Revision ID: 0007_appointments
Revises: 0006_escalation_review
Create Date: 2026-07-23
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0007_appointments"
down_revision: Union[str, None] = "0006_escalation_review"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "appointments",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("escalation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("appointment_date", sa.Date(), nullable=False),
        sa.Column("appointment_start_time", sa.Time(), nullable=False),
        sa.Column("appointment_end_time", sa.Time(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column(
            "assigned_engineer_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["escalation_id"],
            ["complaint_escalations.id"],
            name="fk_appointments_escalation_id_complaint_escalations",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["assigned_engineer_id"],
            ["users.id"],
            name="fk_appointments_assigned_engineer_id_users",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_appointments"),
    )
    op.create_index("ix_appointments_escalation_id", "appointments", ["escalation_id"])
    op.create_index(
        "ix_appointments_assigned_engineer_id",
        "appointments",
        ["assigned_engineer_id"],
    )
    op.create_index(
        "ix_appointments_appointment_date",
        "appointments",
        ["appointment_date"],
    )
    op.create_index("ix_appointments_status", "appointments", ["status"])
    op.create_index(
        "ix_appointments_engineer_date",
        "appointments",
        ["assigned_engineer_id", "appointment_date"],
    )
    op.create_index("ix_appointments_deleted_at", "appointments", ["deleted_at"])
    # One active (BOOKED) appointment per escalation.
    op.create_index(
        "uq_appointments_escalation_booked",
        "appointments",
        ["escalation_id"],
        unique=True,
        postgresql_where=sa.text("status = 'BOOKED' AND deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_appointments_escalation_booked",
        table_name="appointments",
    )
    op.drop_index("ix_appointments_deleted_at", table_name="appointments")
    op.drop_index("ix_appointments_engineer_date", table_name="appointments")
    op.drop_index("ix_appointments_status", table_name="appointments")
    op.drop_index("ix_appointments_appointment_date", table_name="appointments")
    op.drop_index("ix_appointments_assigned_engineer_id", table_name="appointments")
    op.drop_index("ix_appointments_escalation_id", table_name="appointments")
    op.drop_table("appointments")
