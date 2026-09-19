"""Seed resend-to-pusat note presets for internal complaints.

Revision ID: 0090_resend_note_presets
Revises: 0089_more_reason_presets
Create Date: 2026-08-19
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0090_resend_note_presets"
down_revision: Union[str, None] = "0089_more_reason_presets"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_SEED_SETTINGS: tuple[dict[str, str], ...] = (
    {
        "key": "internal_complaint.resend_to_pusat_note_presets",
        "value": '["Dokumen sudah dilengkapi","Sudah diverifikasi ulang","Data sudah disesuaikan"]',
        "description": (
            "Quick-fill note presets shown when a branch resends an internal complaint to HQ"
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
                "VALUES (gen_random_uuid(), :key, :value, 'JSON', 'internal_complaint', "
                "'PUBLIC', :description, now(), now())"
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
