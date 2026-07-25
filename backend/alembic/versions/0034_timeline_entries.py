"""CAPABILITY-010 — reusable timeline_entries table (append-only activity history).

Revision ID: 0034_timeline_entries
Revises: 0033_notification_domain
Create Date: 2026-07-25

Does not alter complaint_timelines (API-209). No soft-delete / update path.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0034_timeline_entries"
down_revision: Union[str, None] = "0033_notification_domain"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_SEED_PERMISSIONS: tuple[tuple[str, str, str, str], ...] = (
    ("timeline:read", "Timeline Read", "timeline", "Read activity timeline entries"),
    (
        "timeline:create",
        "Timeline Create",
        "timeline",
        "Create timeline entries (internal/testing)",
    ),
)

_ADMIN_ROLE_CODES: tuple[str, ...] = ("ADMIN", "ADMINISTRATOR", "SUPER_ADMIN")


def upgrade() -> None:
    op.create_table(
        "timeline_entries",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("aggregate_type", sa.String(length=50), nullable=False),
        sa.Column("aggregate_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("actor_type", sa.String(length=50), nullable=True),
        sa.Column("actor_id", sa.String(length=100), nullable=True),
        sa.Column("actor_name", sa.String(length=200), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_timeline_entries"),
    )
    op.create_index(
        "ix_timeline_entries_aggregate_type",
        "timeline_entries",
        ["aggregate_type"],
    )
    op.create_index(
        "ix_timeline_entries_aggregate_id",
        "timeline_entries",
        ["aggregate_id"],
    )
    op.create_index(
        "ix_timeline_entries_event_type",
        "timeline_entries",
        ["event_type"],
    )
    op.create_index(
        "ix_timeline_entries_created_at",
        "timeline_entries",
        ["created_at"],
    )
    op.create_index(
        "ix_timeline_entries_aggregate_created",
        "timeline_entries",
        ["aggregate_type", "aggregate_id", "created_at"],
    )

    conn = op.get_bind()
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

    for role_code in _ADMIN_ROLE_CODES:
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
        "ix_timeline_entries_aggregate_created", table_name="timeline_entries"
    )
    op.drop_index("ix_timeline_entries_created_at", table_name="timeline_entries")
    op.drop_index("ix_timeline_entries_event_type", table_name="timeline_entries")
    op.drop_index("ix_timeline_entries_aggregate_id", table_name="timeline_entries")
    op.drop_index("ix_timeline_entries_aggregate_type", table_name="timeline_entries")
    op.drop_table("timeline_entries")
