"""Per-user Internal read receipts (typography only; not API-551).

Revision ID: 0111_internal_complaint_seen
Revises: 0110_internal_pusat_canonical
Create Date: 2026-09-04

One row per (ticket, user), written when that user opens GET detail.
Derived-unread: the list bolds while ``seen_at`` is older than
``internal_complaints.updated_at`` AND the ticket still needs action
for the caller's unit. Sidebar badge (API-551) does not read this table.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0111_internal_complaint_seen"
down_revision: Union[str, None] = "0110_internal_pusat_canonical"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "internal_complaint_seen",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("complaint_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column(
            "seen_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["complaint_id"],
            ["internal_complaints.id"],
            name="fk_internal_complaint_seen_complaint_id",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "complaint_id",
            "user_id",
            name="uq_internal_complaint_seen_pair",
        ),
    )
    op.create_index(
        "ix_internal_complaint_seen_user_id",
        "internal_complaint_seen",
        ["user_id"],
    )
    op.create_index(
        "ix_internal_complaint_seen_complaint_id",
        "internal_complaint_seen",
        ["complaint_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_internal_complaint_seen_complaint_id",
        table_name="internal_complaint_seen",
    )
    op.drop_index(
        "ix_internal_complaint_seen_user_id",
        table_name="internal_complaint_seen",
    )
    op.drop_table("internal_complaint_seen")
