"""Pengaduan Internal — persistence tables (domain terpisah dari F4).

Revision ID: 0060_internal_complaints
Revises: 0059_manager_f4_complaint_perms
Create Date: 2026-08-08
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0060_internal_complaints"
down_revision: Union[str, None] = "0059_manager_f4_complaint_perms"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "internal_complaints",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("complaint_number", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("subject", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("subcategory", sa.String(200), nullable=True),
        sa.Column("priority", sa.String(32), nullable=False),
        sa.Column("chronology", sa.Text(), nullable=True),
        sa.Column("impact", sa.Text(), nullable=True),
        sa.Column("owner_unit_id", sa.String(128), nullable=False),
        sa.Column("handling_unit_id", sa.String(128), nullable=False),
        sa.Column(
            "supervisor_approved_after_resolved",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column("closed_by", sa.String(128), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.String(128), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("complaint_number", name="uq_internal_complaints_number"),
    )
    op.create_index(
        "ix_internal_complaints_status", "internal_complaints", ["status"]
    )
    op.create_index(
        "ix_internal_complaints_owner_unit", "internal_complaints", ["owner_unit_id"]
    )
    op.create_index(
        "ix_internal_complaints_handling_unit",
        "internal_complaints",
        ["handling_unit_id"],
    )
    op.create_index(
        "ix_internal_complaints_created_at", "internal_complaints", ["created_at"]
    )

    op.create_table(
        "internal_complaint_resolutions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "complaint_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("internal_complaints.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("resolution_code", sa.String(64), nullable=False),
        sa.Column("summary", sa.String(1000), nullable=False),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("comment", sa.Text(), nullable=False),
        sa.Column("proposed_by", sa.String(128), nullable=True),
        sa.Column("proposed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decided_by", sa.String(128), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_ic_resolutions_complaint_id",
        "internal_complaint_resolutions",
        ["complaint_id"],
    )

    op.create_table(
        "internal_complaint_acceptances",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "complaint_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("internal_complaints.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("party", sa.String(32), nullable=False),
        sa.Column("decision", sa.String(32), nullable=False),
        sa.Column("actor_id", sa.String(128), nullable=False),
        sa.Column("actor_unit_id", sa.String(128), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "decided_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_ic_acceptances_complaint_id",
        "internal_complaint_acceptances",
        ["complaint_id"],
    )

    op.create_table(
        "internal_complaint_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "complaint_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("internal_complaints.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("actor_id", sa.String(128), nullable=False),
        sa.Column("actor_unit_id", sa.String(128), nullable=True),
        sa.Column("source_unit_id", sa.String(128), nullable=True),
        sa.Column("target_unit_id", sa.String(128), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("payload", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_ic_events_complaint_id", "internal_complaint_events", ["complaint_id"]
    )
    op.create_index(
        "ix_ic_events_occurred_at", "internal_complaint_events", ["occurred_at"]
    )

    op.create_table(
        "internal_complaint_number_counters",
        sa.Column("year", sa.Integer(), primary_key=True),
        sa.Column("last_seq", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_table("internal_complaint_number_counters")
    op.drop_index("ix_ic_events_occurred_at", table_name="internal_complaint_events")
    op.drop_index("ix_ic_events_complaint_id", table_name="internal_complaint_events")
    op.drop_table("internal_complaint_events")
    op.drop_index(
        "ix_ic_acceptances_complaint_id", table_name="internal_complaint_acceptances"
    )
    op.drop_table("internal_complaint_acceptances")
    op.drop_index(
        "ix_ic_resolutions_complaint_id", table_name="internal_complaint_resolutions"
    )
    op.drop_table("internal_complaint_resolutions")
    op.drop_index("ix_internal_complaints_created_at", table_name="internal_complaints")
    op.drop_index(
        "ix_internal_complaints_handling_unit", table_name="internal_complaints"
    )
    op.drop_index("ix_internal_complaints_owner_unit", table_name="internal_complaints")
    op.drop_index("ix_internal_complaints_status", table_name="internal_complaints")
    op.drop_table("internal_complaints")
