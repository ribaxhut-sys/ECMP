"""Add Escalation Request fields to complaint_escalations (TASK-011).

Revision ID: 0005_complaint_escalations
Revises: 0004_complaint_resolutions
Create Date: 2026-07-23

Table already exists from 0001; this migration extends it for Branch → HO
Escalation Request (API-301/API-302) without Review/Approve.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005_complaint_escalations"
down_revision: Union[str, None] = "0004_complaint_resolutions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "complaint_escalations",
        sa.Column("reason_code", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "complaint_escalations",
        sa.Column("reason_description", sa.Text(), nullable=True),
    )
    op.add_column(
        "complaint_escalations",
        sa.Column("diagnosis", sa.Text(), nullable=True),
    )
    op.add_column(
        "complaint_escalations",
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.add_column(
        "complaint_escalations",
        sa.Column("requested_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "complaint_escalations",
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_complaint_escalations_requested_by_users",
        "complaint_escalations",
        "users",
        ["requested_by"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_complaint_escalations_requested_by",
        "complaint_escalations",
        ["requested_by"],
    )
    op.create_index(
        "ix_complaint_escalations_requested_at",
        "complaint_escalations",
        ["requested_at"],
    )
    op.create_index(
        "ix_complaint_escalations_reason_code",
        "complaint_escalations",
        ["reason_code"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_complaint_escalations_reason_code", table_name="complaint_escalations"
    )
    op.drop_index(
        "ix_complaint_escalations_requested_at", table_name="complaint_escalations"
    )
    op.drop_index(
        "ix_complaint_escalations_requested_by", table_name="complaint_escalations"
    )
    op.drop_constraint(
        "fk_complaint_escalations_requested_by_users",
        "complaint_escalations",
        type_="foreignkey",
    )
    op.drop_column("complaint_escalations", "requested_at")
    op.drop_column("complaint_escalations", "requested_by")
    op.drop_column("complaint_escalations", "notes")
    op.drop_column("complaint_escalations", "diagnosis")
    op.drop_column("complaint_escalations", "reason_description")
    op.drop_column("complaint_escalations", "reason_code")
