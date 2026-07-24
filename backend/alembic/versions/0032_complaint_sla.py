"""Add Complaint SLA foundation tables (CAPABILITY-008).

Revision ID: 0032_complaint_sla
Revises: 0031_complaint_escalation
Create Date: 2026-07-24

Creates:
- ``complaint_sla_policies`` — CA BC SLAPolicy (legacy ECMF ``sla_policies`` unchanged)
- ``complaint_case_slas`` — ComplaintSLA child of ``complaint_cases``

Partial unique index enforces at most one active SLA per complaint.
Seeds one default policy (24h / 1440 minutes).
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0032_complaint_sla"
down_revision: Union[str, None] = "0031_complaint_escalation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_DEFAULT_POLICY_ID = "a0000000-0000-4000-8000-000000000032"


def upgrade() -> None:
    op.create_table(
        "complaint_sla_policies",
        sa.Column("policy_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("target_minutes", sa.Integer(), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("policy_id", name="pk_complaint_sla_policies"),
    )
    op.create_index(
        "ix_complaint_sla_policies_name",
        "complaint_sla_policies",
        ["name"],
        unique=False,
    )
    op.create_index(
        "ix_complaint_sla_policies_default",
        "complaint_sla_policies",
        ["is_default"],
        unique=True,
        postgresql_where=sa.text("is_default = true"),
    )

    op.create_table(
        "complaint_case_slas",
        sa.Column("sla_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("complaint_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("policy_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("breached_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_breached", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["complaint_id"],
            ["complaint_cases.complaint_id"],
            name="fk_complaint_case_slas_complaint_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["policy_id"],
            ["complaint_sla_policies.policy_id"],
            name="fk_complaint_case_slas_policy_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("sla_id", name="pk_complaint_case_slas"),
    )
    op.create_index(
        "ix_complaint_case_slas_complaint_id",
        "complaint_case_slas",
        ["complaint_id"],
        unique=False,
    )
    op.create_index(
        "ix_complaint_case_slas_complaint_active",
        "complaint_case_slas",
        ["complaint_id"],
        unique=True,
        postgresql_where=sa.text("is_active = true"),
    )
    op.create_index(
        "ix_complaint_case_slas_policy_id",
        "complaint_case_slas",
        ["policy_id"],
        unique=False,
    )

    op.execute(
        sa.text(
            """
            INSERT INTO complaint_sla_policies
                (policy_id, name, target_minutes, is_default, description)
            VALUES
                (
                    CAST(:policy_id AS uuid),
                    'Default 24h Resolution',
                    1440,
                    true,
                    'CAPABILITY-008 default SLA policy (24 hours)'
                )
            """
        ).bindparams(policy_id=_DEFAULT_POLICY_ID)
    )


def downgrade() -> None:
    op.drop_index(
        "ix_complaint_case_slas_policy_id",
        table_name="complaint_case_slas",
    )
    op.drop_index(
        "ix_complaint_case_slas_complaint_active",
        table_name="complaint_case_slas",
    )
    op.drop_index(
        "ix_complaint_case_slas_complaint_id",
        table_name="complaint_case_slas",
    )
    op.drop_table("complaint_case_slas")
    op.drop_index(
        "ix_complaint_sla_policies_default",
        table_name="complaint_sla_policies",
    )
    op.drop_index(
        "ix_complaint_sla_policies_name",
        table_name="complaint_sla_policies",
    )
    op.drop_table("complaint_sla_policies")
