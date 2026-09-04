"""Seed the remaining internal complaint quick-fill presets.

Revision ID: 0092_internal_more_presets
Revises: 0091_role_display_names_dec027
Create Date: 2026-08-21
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0092_internal_more_presets"
down_revision: Union[str, None] = "0091_role_display_names_dec027"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_SEED_SETTINGS: tuple[dict[str, str], ...] = (
    {
        "key": "internal_complaint.withdraw_decision_reason_presets",
        "value": '["Alasan penarikan tidak jelas","Pengaduan masih perlu ditindaklanjuti"]',
        "description": (
            "Quick-fill reason presets for approving/rejecting an internal complaint "
            "withdraw request"
        ),
    },
    {
        "key": "internal_complaint.reject_proposal_reason_presets",
        "value": (
            '["Penyelesaian belum sesuai","Bukti pendukung kurang",'
            '"Perlu penjelasan tambahan"]'
        ),
        "description": (
            "Quick-fill reason presets for rejecting an internal complaint resolution proposal"
        ),
    },
    {
        "key": "internal_complaint.resolution_comment_presets",
        "value": (
            '["Sudah ditindaklanjuti sesuai SOP","Sudah dikoordinasikan dengan unit terkait",'
            '"Selesai, tidak ada tindak lanjut tambahan"]'
        ),
        "description": (
            "Quick-fill comment presets for the internal complaint resolution dialog"
        ),
    },
    {
        "key": "internal_complaint.acceptance_note_presets",
        "value": (
            '["Diterima untuk ditindaklanjuti","Bukan kewenangan unit ini",'
            '"Perlu dilengkapi terlebih dahulu"]'
        ),
        "description": (
            "Quick-fill note presets for accepting or returning an internal complaint"
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
