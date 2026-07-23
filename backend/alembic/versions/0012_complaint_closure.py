"""Add complaint closure fields (TASK-019).

Revision ID: 0012_complaint_closure
Revises: 0011_final_resolution
Create Date: 2026-07-23
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0012_complaint_closure"
down_revision: Union[str, None] = "0011_final_resolution"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # closed_at already exists from 0001; add actor + notes for explicit closure.
    op.add_column(
        "complaints",
        sa.Column(
            "closed_by",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )
    op.add_column(
        "complaints",
        sa.Column("closure_notes", sa.Text(), nullable=True),
    )
    op.create_foreign_key(
        "fk_complaints_closed_by_users",
        "complaints",
        "users",
        ["closed_by"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_complaints_closed_by", "complaints", ["closed_by"])
    op.create_index("ix_complaints_closed_at", "complaints", ["closed_at"])


def downgrade() -> None:
    op.drop_index("ix_complaints_closed_at", table_name="complaints")
    op.drop_index("ix_complaints_closed_by", table_name="complaints")
    op.drop_constraint(
        "fk_complaints_closed_by_users",
        "complaints",
        type_="foreignkey",
    )
    op.drop_column("complaints", "closure_notes")
    op.drop_column("complaints", "closed_by")
