"""Identity & Password Management — force_password_change + password_reset_tokens.

Revision ID: 0037_password_management
Revises: 0036_search_indexes
Create Date: 2026-07-28

Non-destructive: adds column + table + permission seed only.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0037_password_management"
down_revision: Union[str, None] = "0036_search_indexes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_SEED_PERMISSIONS: tuple[tuple[str, str, str, str], ...] = (
    (
        "users:reset_password",
        "Users Reset Password",
        "users",
        "Admin/supervisor reset of another user's password",
    ),
)

_ADMIN_ROLE_CODES: tuple[str, ...] = ("ADMIN", "ADMINISTRATOR", "SUPER_ADMIN")
_SUPERVISOR_ROLE_CODES: tuple[str, ...] = ("SUPERVISOR", "BRANCH_SUPERVISOR")


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    user_cols = {c["name"] for c in inspector.get_columns("users")}

    # Idempotent: column may already exist from a prior partial apply.
    if "force_password_change" not in user_cols:
        op.add_column(
            "users",
            sa.Column(
                "force_password_change",
                sa.Boolean(),
                server_default=sa.text("false"),
                nullable=False,
            ),
        )

    if not inspector.has_table("password_reset_tokens"):
        op.create_table(
            "password_reset_tokens",
            sa.Column(
                "id",
                postgresql.UUID(as_uuid=True),
                server_default=sa.text("gen_random_uuid()"),
                nullable=False,
            ),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("token_hash", sa.String(length=64), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(
                ["user_id"],
                ["users.id"],
                name="fk_password_reset_tokens_user_id_users",
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id", name="pk_password_reset_tokens"),
            sa.UniqueConstraint(
                "token_hash", name="uq_password_reset_tokens_token_hash"
            ),
        )
        op.create_index(
            "ix_password_reset_tokens_user_id",
            "password_reset_tokens",
            ["user_id"],
        )
        op.create_index(
            "ix_password_reset_tokens_expires_at",
            "password_reset_tokens",
            ["expires_at"],
        )
    for code, name, module, description in _SEED_PERMISSIONS:
        conn.execute(
            sa.text(
                """
                INSERT INTO permissions (
                    id, code, name, module, description,
                    is_system, is_active, created_at, updated_at
                )
                VALUES (
                    gen_random_uuid(), :code, :name, :module, :description,
                    true, true, now(), now()
                )
                ON CONFLICT (code) DO NOTHING
                """
            ),
            {
                "code": code,
                "name": name,
                "module": module,
                "description": description,
            },
        )

    for role_code in (*_ADMIN_ROLE_CODES, *_SUPERVISOR_ROLE_CODES):
        for perm_code, _, _, _ in _SEED_PERMISSIONS:
            conn.execute(
                sa.text(
                    """
                    INSERT INTO role_permissions (id, role_id, permission_id, created_at)
                    SELECT gen_random_uuid(), r.id, p.id, now()
                    FROM roles r
                    CROSS JOIN permissions p
                    WHERE r.code = :role_code
                      AND p.code = :perm_code
                      AND r.deleted_at IS NULL
                      AND NOT EXISTS (
                        SELECT 1 FROM role_permissions rp
                        WHERE rp.role_id = r.id AND rp.permission_id = p.id
                      )
                    """
                ),
                {"role_code": role_code, "perm_code": perm_code},
            )


def downgrade() -> None:
    conn = op.get_bind()
    for perm_code, _, _, _ in _SEED_PERMISSIONS:
        conn.execute(
            sa.text(
                """
                DELETE FROM role_permissions
                WHERE permission_id IN (
                    SELECT id FROM permissions WHERE code = :code
                )
                """
            ),
            {"code": perm_code},
        )
        conn.execute(
            sa.text("DELETE FROM permissions WHERE code = :code"),
            {"code": perm_code},
        )

    op.drop_index(
        "ix_password_reset_tokens_expires_at",
        table_name="password_reset_tokens",
    )
    op.drop_index(
        "ix_password_reset_tokens_user_id",
        table_name="password_reset_tokens",
    )
    op.drop_table("password_reset_tokens")
    op.drop_column("users", "force_password_change")
