"""Seed quick-fill presets for the intake escalation and HQ visit dialogs.

Revision ID: 0094_cm_batch1_presets
Revises: 0093_case_dialog_presets
Create Date: 2026-08-21
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0094_cm_batch1_presets"
down_revision: Union[str, None] = "0093_case_dialog_presets"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_SEED_SETTINGS: tuple[dict[str, str], ...] = (
    {
        "key": "cm_batch1.approve_escalation_note_presets",
        "value": (
            '["Sesuai kewenangan Pusat","Perlu penanganan Pusat",'
            '"Eskalasi disetujui sesuai SOP"]'
        ),
        "description": "Quick-fill note presets for approving an intake escalation",
    },
    {
        "key": "cm_batch1.reject_escalation_note_presets",
        "value": (
            '["Masih dapat ditangani cabang","Alasan eskalasi kurang jelas",'
            '"Dokumen pendukung belum lengkap"]'
        ),
        "description": "Quick-fill note presets for rejecting an intake escalation",
    },
    {
        "key": "cm_batch1.cancel_escalation_note_presets",
        "value": (
            '["Diselesaikan di cabang","Eskalasi tidak jadi diperlukan",'
            '"Diajukan keliru"]'
        ),
        "description": "Quick-fill note presets for cancelling an intake escalation",
    },
    {
        "key": "cm_batch1.rerequest_escalation_reason_presets",
        "value": (
            '["Dokumen sudah dilengkapi","Ada informasi baru",'
            '"Kondisi berubah, tetap perlu Pusat"]'
        ),
        "description": "Quick-fill reason presets for re-requesting an intake escalation",
    },
    {
        "key": "cm_batch1.hq_accept_schedule_note_presets",
        "value": (
            '["Dijadwalkan sesuai ketersediaan",'
            '"Wajib pajak diminta hadir sesuai jadwal"]'
        ),
        "description": "Quick-fill note presets when HQ accepts and schedules a visit",
    },
    {
        "key": "cm_batch1.hq_return_note_presets",
        "value": (
            '["Dokumen kurang","Perlu verifikasi ulang cabang",'
            '"Bukan kewenangan Pusat"]'
        ),
        "description": "Quick-fill note presets when HQ returns a complaint to the branch",
    },
    {
        "key": "cm_batch1.hq_arrival_note_presets",
        "value": (
            '["Wajib pajak dijadwalkan hadir",'
            '"Perubahan jadwal atas permintaan wajib pajak"]'
        ),
        "description": "Quick-fill note presets for the HQ arrival schedule note",
    },
    {
        "key": "cm_batch1.hq_complete_note_presets",
        "value": (
            '["Kunjungan selesai, tidak ada tindak lanjut",'
            '"Selesai, hasil sudah disampaikan","Selesai sesuai SOP"]'
        ),
        "description": "Quick-fill note presets when HQ completes a visit",
    },
    {
        "key": "cm_batch1.intake_case_note_presets",
        "value": (
            '["Perlu penanganan lanjutan unit","Sesuai kategori layanan",'
            '"Dilanjutkan sesuai SOP"]'
        ),
        "description": "Quick-fill note presets for the per-case note on intake escalation",
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
                "VALUES (gen_random_uuid(), :key, :value, 'JSON', 'cm_batch1', "
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
