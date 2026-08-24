"""Seed per-Pusat-unit arrival capacity (hq.schedule.capacity_by_unit).

Pusat is not one door: CRO schedules the taxpayer to its own counter, to
Sekretariat or to a Suban, and each of those has its own quota per slot.
The map starts empty — every unit then inherits capacity_per_slot (same as
CRO today) until an admin gives a unit its own number.

Revision ID: 0102_hq_capacity_by_unit
Revises: 0101_hq_schedule_break_overrides
Create Date: 2026-08-23

Note: revision id must stay <= 32 chars (alembic_version.version_num).
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0102_hq_capacity_by_unit"
down_revision: Union[str, None] = "0101_hq_schedule_break_overrides"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_KEY = "hq.schedule.capacity_by_unit"
_DESCRIPTION = (
    "Arrivals per slot for a specific Pusat unit "
    '(e.g. {"PUSAT-SEKRETARIAT": 1}); units not listed use capacity_per_slot'
)


def upgrade() -> None:
    conn = op.get_bind()
    exists = conn.execute(
        sa.text("SELECT 1 FROM settings WHERE key = :key"), {"key": _KEY}
    ).first()
    if exists:
        return
    conn.execute(
        sa.text(
            "INSERT INTO settings "
            "(id, key, value, value_type, category, visibility, description, "
            "created_at, updated_at) "
            "VALUES (gen_random_uuid(), :key, '{}', 'JSON', 'hq_schedule', "
            "'PROTECTED', :description, now(), now())"
        ),
        {"key": _KEY, "description": _DESCRIPTION},
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM settings WHERE key = :key"), {"key": _KEY})
