"""Add announcements.reference_number (PGM-YYMM-NNNN) + monthly counters.

Revision ID: 0067_announcement_ref_num
Revises: 0066_drop_announcement_target
Create Date: 2026-08-10

Server-owned human reference for management/history. Existing rows are
backfilled by created_at ascending within each YYMM bucket.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0067_announcement_ref_num"
down_revision: Union[str, None] = "0066_drop_announcement_target"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "announcement_number_counters",
        sa.Column("name", sa.String(length=64), primary_key=True),
        sa.Column("value", sa.Integer(), nullable=False, server_default="0"),
    )

    op.add_column(
        "announcements",
        sa.Column("reference_number", sa.String(length=32), nullable=True),
    )

    conn = op.get_bind()
    rows = conn.execute(
        sa.text(
            """
            SELECT id, created_at
            FROM announcements
            WHERE deleted_at IS NULL
            ORDER BY created_at ASC, id ASC
            """
        )
    ).fetchall()

    counters: dict[str, int] = {}
    for row in rows:
        created_at = row.created_at
        year = int(created_at.year)
        month = int(created_at.month)
        key = f"an:{year:04d}{month:02d}"
        counters[key] = counters.get(key, 0) + 1
        seq = counters[key]
        yymm = f"{year % 100:02d}{month:02d}"
        width = 4 if seq <= 9999 else len(str(seq))
        ref = f"PGM-{yymm}-{seq:0{width}d}"
        conn.execute(
            sa.text(
                "UPDATE announcements SET reference_number = :ref WHERE id = :id"
            ),
            {"ref": ref, "id": row.id},
        )

    for key, value in counters.items():
        conn.execute(
            sa.text(
                "INSERT INTO announcement_number_counters (name, value) "
                "VALUES (:name, :value)"
            ),
            {"name": key, "value": value},
        )

    # Soft-deleted rows without a number get a stable placeholder so NOT NULL
    # can apply; they are never shown in management/history lists.
    orphan = conn.execute(
        sa.text(
            "SELECT id FROM announcements WHERE reference_number IS NULL ORDER BY id"
        )
    ).fetchall()
    for index, row in enumerate(orphan, start=1):
        ref = f"PGM-DEL-{index:04d}"
        conn.execute(
            sa.text(
                "UPDATE announcements SET reference_number = :ref WHERE id = :id"
            ),
            {"ref": ref, "id": row.id},
        )

    op.alter_column(
        "announcements",
        "reference_number",
        existing_type=sa.String(length=32),
        nullable=False,
    )
    op.create_index(
        "uq_announcements_reference_number",
        "announcements",
        ["reference_number"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_announcements_reference_number", table_name="announcements")
    op.drop_column("announcements", "reference_number")
    op.drop_table("announcement_number_counters")
