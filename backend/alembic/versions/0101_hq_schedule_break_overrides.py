"""Seed HQ arrival schedule break settings (Jumat 11:30-13:30).

break_start/break_end were only defaults in the settings registry — never
seeded — so the break window could not be changed by an admin. This seeds
them together with the per-weekday override map used for Jumat.

Revision ID: 0101_hq_schedule_break_overrides
Revises: 0100_complaint_closed_at
Create Date: 2026-08-23
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0101_hq_schedule_break_overrides"
down_revision: Union[str, None] = "0100_complaint_closed_at"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_SEED_SETTINGS: tuple[dict[str, str], ...] = (
    {
        "key": "hq.schedule.break_start",
        "value": "12:00",
        "value_type": "STRING",
        "category": "hq_schedule",
        "visibility": "PROTECTED",
        "description": "HQ arrival schedule lunch break start (HH:MM)",
    },
    {
        "key": "hq.schedule.break_end",
        "value": "13:00",
        "value_type": "STRING",
        "category": "hq_schedule",
        "visibility": "PROTECTED",
        "description": "HQ arrival schedule lunch break end (HH:MM)",
    },
    {
        "key": "hq.schedule.break_overrides",
        "value": '{"5": {"start": "11:30", "end": "13:30"}}',
        "value_type": "JSON",
        "category": "hq_schedule",
        "visibility": "PROTECTED",
        "description": (
            "Per-weekday break windows overriding break_start/break_end "
            "(ISO weekday key, null = no break); Jumat defaults to 11:30-13:30"
        ),
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
