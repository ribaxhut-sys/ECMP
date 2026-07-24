"""Add sla_records foundation table (TASK-021).

Revision ID: 0014_sla_foundation
Revises: 0013_escalation_closure
Create Date: 2026-07-23
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0014_sla_foundation"
down_revision: Union[str, None] = "0013_escalation_closure"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sla_records",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("complaint_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assignment_due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolution_due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("appointment_due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("escalation_due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("overall_due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("assignment_status", sa.String(length=32), nullable=False),
        sa.Column("resolution_status", sa.String(length=32), nullable=False),
        sa.Column("appointment_status", sa.String(length=32), nullable=False),
        sa.Column("escalation_status", sa.String(length=32), nullable=False),
        sa.Column("overall_status", sa.String(length=32), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["complaint_id"],
            ["complaints.id"],
            name="fk_sla_records_complaint_id_complaints",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_sla_records"),
        sa.UniqueConstraint("complaint_id", name="uq_sla_records_complaint_id"),
    )
    op.create_index("ix_sla_records_complaint_id", "sla_records", ["complaint_id"])
    op.create_index(
        "ix_sla_records_overall_status", "sla_records", ["overall_status"]
    )
    op.create_index(
        "ix_sla_records_overall_due_at", "sla_records", ["overall_due_at"]
    )

    # Backfill foundation rows for existing (non-deleted) complaints.
    op.execute(
        sa.text(
            """
            INSERT INTO sla_records (
                complaint_id,
                assignment_status,
                resolution_status,
                appointment_status,
                escalation_status,
                overall_status,
                created_at,
                updated_at
            )
            SELECT
                c.id,
                'PENDING',
                'PENDING',
                'PENDING',
                'PENDING',
                'PENDING',
                now(),
                now()
            FROM complaints c
            WHERE c.deleted_at IS NULL
              AND NOT EXISTS (
                  SELECT 1 FROM sla_records s WHERE s.complaint_id = c.id
              )
            """
        )
    )


def downgrade() -> None:
    op.drop_index("ix_sla_records_overall_due_at", table_name="sla_records")
    op.drop_index("ix_sla_records_overall_status", table_name="sla_records")
    op.drop_index("ix_sla_records_complaint_id", table_name="sla_records")
    op.drop_table("sla_records")
