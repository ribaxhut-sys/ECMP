"""User preferred_language — drives email/API message localization.

Revision ID: 0038_preferred_language
Revises: 0037_password_management
Create Date: 2026-07-28

Non-destructive: adds a single NOT NULL column with a server default.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0038_preferred_language"
down_revision: Union[str, None] = "0037_password_management"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    user_cols = {c["name"] for c in inspector.get_columns("users")}
    # Idempotent: column may already exist from a prior partial apply.
    if "preferred_language" not in user_cols:
        op.add_column(
            "users",
            sa.Column(
                "preferred_language",
                sa.String(length=8),
                server_default=sa.text("'id'"),
                nullable=False,
            ),
        )


def downgrade() -> None:
    op.drop_column("users", "preferred_language")
