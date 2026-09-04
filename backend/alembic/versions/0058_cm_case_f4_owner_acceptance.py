"""F4 business rules — Case owner unit + closure acceptance (Handling Unit / Owner).

Revision ID: 0058_cm_case_f4_owner_acceptance
Revises: 0057_cm_b1_owning_unit_code
Create Date: 2026-08-08

Adds:
  - cm_cases.owner_unit_id — unit that created the parent Complaint,
    snapshotted once at Case creation and never mutated afterward (F4 owner
    rule). owning_unit_id keeps meaning "current handling unit" as before.
    Backfilled from cm_batch1_complaints.owning_unit_id via complaint_id.
  - cm_case_acceptances — append-only Handling Unit / Owner closure
    acceptance history (F4 closure rule). No backfill: existing Closed
    Cases predate the two-party acceptance rule and cannot be
    retroactively attributed to a real actor/unit/decision without
    inventing data; they simply have no acceptance rows (see F4 report).
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0058_cm_case_f4_owner_acceptance"
down_revision: Union[str, None] = "0057_cm_b1_owning_unit_code"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cm_cases",
        sa.Column("owner_unit_id", sa.String(length=128), nullable=True),
    )

    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            UPDATE cm_cases AS c
            SET owner_unit_id = b.owning_unit_id
            FROM cm_batch1_complaints AS b
            WHERE b.id::text = c.complaint_id
              AND c.owner_unit_id IS NULL
              AND b.owning_unit_id IS NOT NULL
            """
        )
    )

    op.create_table(
        "cm_case_acceptances",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "case_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cm_cases.id", ondelete="CASCADE"),
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
        "ix_cm_case_acceptances_case_id", "cm_case_acceptances", ["case_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_cm_case_acceptances_case_id", table_name="cm_case_acceptances")
    op.drop_table("cm_case_acceptances")
    op.drop_column("cm_cases", "owner_unit_id")
