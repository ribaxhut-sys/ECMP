"""Add settings table + seed defaults (TASK-028).

Revision ID: 0016_settings
Revises: 0015_sla_policy
Create Date: 2026-07-23
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0016_settings"
down_revision: Union[str, None] = "0015_sla_policy"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_SEED_SETTINGS: tuple[dict[str, str | None], ...] = (
    {
        "key": "company.name",
        "value": "ECMP",
        "value_type": "STRING",
        "category": "company",
        "visibility": "PUBLIC",
        "description": "Company / product display name",
    },
    {
        "key": "company.logo",
        "value": "",
        "value_type": "URL",
        "category": "company",
        "visibility": "PUBLIC",
        "description": "Company logo URL (empty until configured)",
    },
    {
        "key": "app.language.default",
        "value": "id",
        "value_type": "STRING",
        "category": "app",
        "visibility": "PUBLIC",
        "description": "Default application language code",
    },
    {
        "key": "app.timezone",
        "value": "Asia/Jakarta",
        "value_type": "STRING",
        "category": "app",
        "visibility": "PUBLIC",
        "description": "Default application timezone (IANA)",
    },
    {
        "key": "dashboard.recent.limit",
        "value": "10",
        "value_type": "INTEGER",
        "category": "dashboard",
        "visibility": "PROTECTED",
        "description": "Max recent activity items on dashboard summary",
    },
    {
        "key": "complaint.number.prefix",
        "value": "CMP",
        "value_type": "STRING",
        "category": "complaint",
        "visibility": "PROTECTED",
        "description": "Prefix for generated complaint numbers",
    },
)


def upgrade() -> None:
    op.create_table(
        "settings",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("key", sa.String(length=200), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("value_type", sa.String(length=20), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("visibility", sa.String(length=20), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_settings"),
        sa.UniqueConstraint("key", name="uq_settings_key"),
    )
    op.create_index("ix_settings_category", "settings", ["category"])
    op.create_index("ix_settings_visibility", "settings", ["visibility"])

    settings_table = sa.table(
        "settings",
        sa.column("key", sa.String),
        sa.column("value", sa.Text),
        sa.column("value_type", sa.String),
        sa.column("category", sa.String),
        sa.column("visibility", sa.String),
        sa.column("description", sa.Text),
    )
    op.bulk_insert(settings_table, list(_SEED_SETTINGS))


def downgrade() -> None:
    op.drop_index("ix_settings_visibility", table_name="settings")
    op.drop_index("ix_settings_category", table_name="settings")
    op.drop_table("settings")
