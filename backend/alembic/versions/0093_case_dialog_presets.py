"""Seed quick-fill presets for the CM case dialogs.

Revision ID: 0093_case_dialog_presets
Revises: 0092_internal_more_presets
Create Date: 2026-08-21
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0093_case_dialog_presets"
down_revision: Union[str, None] = "0092_internal_more_presets"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_SEED_SETTINGS: tuple[dict[str, str], ...] = (
    {
        "key": "case.close_note_presets",
        "value": (
            '["Kasus selesai ditangani","Ditutup atas persetujuan pelapor",'
            '"Ditutup, tidak ada tindak lanjut tambahan"]'
        ),
        "description": "Quick-fill note presets shown in the case close dialog",
    },
    {
        "key": "case.cancel_reason_presets",
        "value": '["Duplikat","Input salah","Permintaan dibatalkan pelapor"]',
        "description": "Quick-fill reason presets shown when a case is cancelled",
    },
    {
        "key": "case.resolution_comment_presets",
        "value": (
            '["Sudah ditindaklanjuti sesuai SOP","Sudah dikoordinasikan dengan unit terkait",'
            '"Selesai, pelapor sudah diinformasikan"]'
        ),
        "description": "Quick-fill comment presets shown in the case resolve dialog",
    },
    {
        "key": "case.rejection_reason_presets",
        "value": (
            '["Penyelesaian belum sesuai","Bukti pendukung kurang",'
            '"Perlu penjelasan tambahan"]'
        ),
        "description": "Quick-fill reason presets shown when a case resolution is rejected",
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
                "VALUES (gen_random_uuid(), :key, :value, 'JSON', 'case', "
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
