"""Seed remaining internal complaint quick-fill reason presets.

Revision ID: 0089_more_reason_presets
Revises: 0088_cancel_reason_presets
Create Date: 2026-08-19
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0089_more_reason_presets"
down_revision: Union[str, None] = "0088_cancel_reason_presets"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_SEED_SETTINGS: tuple[dict[str, str], ...] = (
    {
        "key": "internal_complaint.transfer_reason_presets",
        "value": '["Salah unit","Perlu keahlian khusus","Beban kerja unit tujuan lebih sesuai"]',
        "description": "Quick-fill reason presets shown in the internal complaint transfer dialog",
    },
    {
        "key": "internal_complaint.request_transfer_reason_presets",
        "value": '["Di luar kewenangan unit","Perlu koordinasi lintas unit"]',
        "description": "Quick-fill reason presets for requesting an internal complaint transfer",
    },
    {
        "key": "internal_complaint.transfer_decision_reason_presets",
        "value": '["Alasan tidak jelas","Dokumen pendukung kurang"]',
        "description": (
            "Quick-fill reason presets for approving/rejecting an internal "
            "complaint transfer request"
        ),
    },
    {
        "key": "internal_complaint.completion_return_reason_presets",
        "value": '["Dokumen kurang","Perlu verifikasi ulang","Data tidak sesuai"]',
        "description": "Quick-fill reason presets for returning an internal complaint",
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
