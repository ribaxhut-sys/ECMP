"""Drop announcements.target — global audience (no domain targeting).

Revision ID: 0066_drop_announcement_target
Revises: 0065_announcement_reads
Create Date: 2026-08-10

0062 was later edited in-place to omit ``target`` for greenfield installs.
Lab/prod DBs that already applied the original 0062 still have the column
and index — this revision removes them idempotently for those environments.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0066_drop_announcement_target"
down_revision: Union[str, None] = "0065_announcement_reads"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {c["name"] for c in inspector.get_columns("announcements")}
    indexes = {i["name"] for i in inspector.get_indexes("announcements")}

    if "ix_announcements_target" in indexes:
        op.drop_index("ix_announcements_target", table_name="announcements")
    if "target" in columns:
        op.drop_column("announcements", "target")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {c["name"] for c in inspector.get_columns("announcements")}
    indexes = {i["name"] for i in inspector.get_indexes("announcements")}

    if "target" not in columns:
        op.add_column(
            "announcements",
            sa.Column(
                "target",
                sa.String(20),
                nullable=False,
                server_default="ALL",
            ),
        )
    if "ix_announcements_target" not in indexes:
        op.create_index("ix_announcements_target", "announcements", ["target"])
