"""Seed HQ arrival schedule settings (hq.schedule.*).

Revision ID: 0083_hq_schedule_settings
Revises: 0082_storage_max_upload_50mb
Create Date: 2026-08-17
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0083_hq_schedule_settings"
down_revision: Union[str, None] = "0082_storage_max_upload_50mb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_SEED_SETTINGS: tuple[dict[str, str], ...] = (
    {
        "key": "hq.schedule.start",
        "value": "08:00",
        "value_type": "STRING",
        "category": "hq_schedule",
        "visibility": "PROTECTED",
        "description": "HQ arrival schedule opening time (HH:MM)",
    },
    {
        "key": "hq.schedule.end",
        "value": "16:00",
        "value_type": "STRING",
        "category": "hq_schedule",
        "visibility": "PROTECTED",
        "description": "HQ arrival schedule closing time (HH:MM)",
    },
    {
        "key": "hq.schedule.slot_minutes",
        "value": "60",
        "value_type": "INTEGER",
        "category": "hq_schedule",
        "visibility": "PROTECTED",
        "description": "HQ arrival schedule slot length in minutes",
    },
    {
        "key": "hq.schedule.capacity_per_slot",
        "value": "2",
        "value_type": "INTEGER",
        "category": "hq_schedule",
        "visibility": "PROTECTED",
        "description": "Max taxpayer arrivals accommodated per HQ schedule slot",
    },
    {
        "key": "hq.schedule.workdays",
        "value": "1,2,3,4,5",
        "value_type": "STRING",
        "category": "hq_schedule",
        "visibility": "PROTECTED",
        "description": "ISO weekdays (1=Mon..7=Sun) HQ accepts arrivals, comma-separated",
    },
)

def upgrade() -> None:
    conn = op.get_bind()
    for seed in _SEED_SETTINGS:
        exists = conn.execute(
            sa.text("SELECT 1 FROM settings WHERE key = :key"),
            {"key": seed["key"]},
        ).first()
        if exists:
            continue
        conn.execute(
            sa.text(
                "INSERT INTO settings "
                "(id, key, value, value_type, category, visibility, description, "
                "created_at, updated_at) "
                "VALUES (gen_random_uuid(), :key, :value, :value_type, :category, "
                ":visibility, :description, now(), now())"
            ),
            seed,
        )


def downgrade() -> None:
    conn = op.get_bind()
    keys = [seed["key"] for seed in _SEED_SETTINGS]
    conn.execute(
        sa.text("DELETE FROM settings WHERE key = ANY(:keys)"),
        {"keys": keys},
    )
