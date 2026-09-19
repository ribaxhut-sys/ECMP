"""Case inbox receipts for Cabang unread (return / HQ schedule).

Revision ID: 0106_cm_case_inbox_receipts
Revises: 0105_complaint_close_cro_roles
Create Date: 2026-08-24

One row per (case, user). ``read_at`` NULL = unread. Later events clear
``read_at`` so the Case lights up again. Actor ``user_id`` has no FK
(same convention as ``announcement_reads``).
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0106_cm_case_inbox_receipts"
down_revision: Union[str, None] = "0105_complaint_close_cro_roles"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cm_case_inbox_receipts",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("reason", sa.String(length=32), nullable=False),
        sa.Column(
            "event_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["case_id"],
            ["cm_cases.id"],
            name="fk_cm_case_inbox_receipts_case_id_cm_cases",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "case_id",
            "user_id",
            name="uq_cm_case_inbox_receipts_pair",
        ),
    )
    op.create_index(
        "ix_cm_case_inbox_receipts_user_id",
        "cm_case_inbox_receipts",
        ["user_id"],
    )
    op.create_index(
        "ix_cm_case_inbox_receipts_case_id",
        "cm_case_inbox_receipts",
        ["case_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_cm_case_inbox_receipts_case_id",
        table_name="cm_case_inbox_receipts",
    )
    op.drop_index(
        "ix_cm_case_inbox_receipts_user_id",
        table_name="cm_case_inbox_receipts",
    )
    op.drop_table("cm_case_inbox_receipts")
