"""Store unique 3-letter user initials at registration.

Revision ID: 0079_user_initials
Revises: 0078_cm_case_handling_claimed_by
Create Date: 2026-08-17

``users.initials`` is unique for every row, including inactive and
soft-deleted users, so a deactivated account does not free the code.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.modules.users.initials import allocate_user_initials

revision: str = "0079_user_initials"
down_revision: Union[str, None] = "0078_cm_case_handling_claimed_by"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("initials", sa.String(length=3), nullable=True))
    conn = op.get_bind()
    rows = conn.execute(
        sa.text(
            """
            SELECT id, full_name, username
            FROM users
            ORDER BY created_at ASC, id ASC
            """
        )
    ).fetchall()
    taken: set[str] = set()
    for row in rows:
        code = allocate_user_initials(row.full_name, taken, username=row.username)
        taken.add(code)
        conn.execute(
            sa.text("UPDATE users SET initials = :code WHERE id = :id"),
            {"code": code, "id": row.id},
        )
    op.alter_column("users", "initials", existing_type=sa.String(length=3), nullable=False)
    op.create_unique_constraint("uq_users_initials", "users", ["initials"])


def downgrade() -> None:
    op.drop_constraint("uq_users_initials", "users", type_="unique")
    op.drop_column("users", "initials")
