"""Seed official BAPENDA DKI Jakarta Branch master data (UPPPD).

Revision ID: 0047_bapenda_branch_master_data
Revises: 0046_cm_case_management
Create Date: 2026-08-04

Populates the existing `branches` table with the 44 official UPPPD
(Unit Pelayanan Pemungutan Pajak Daerah) offices, grouped under the five
Jakarta administrative regions (stored in `city`). No schema change.

"Pusat" (Head Office) is not a Branch row — it remains represented
implicitly by `branch_id IS NULL` per the existing EBS-001 authorization
model. Only Branch (Cabang / UPPPD) rows are seeded here.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0047_bapenda_branch_master_data"
down_revision: Union[str, None] = "0046_cm_case_management"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# (region/city, UPPPD name) — official branch list, BAPENDA DKI Jakarta.
_UPPPD: tuple[tuple[str, str], ...] = (
    ("Jakarta Pusat", "UPPPD Tanah Abang"),
    ("Jakarta Pusat", "UPPPD Gambir"),
    ("Jakarta Pusat", "UPPPD Sawah Besar"),
    ("Jakarta Pusat", "UPPPD Kemayoran"),
    ("Jakarta Pusat", "UPPPD Senen"),
    ("Jakarta Pusat", "UPPPD Cempaka Putih"),
    ("Jakarta Pusat", "UPPPD Menteng"),
    ("Jakarta Pusat", "UPPPD Johar Baru"),
    ("Jakarta Utara", "UPPPD Penjaringan"),
    ("Jakarta Utara", "UPPPD Pademangan"),
    ("Jakarta Utara", "UPPPD Tanjung Priok"),
    ("Jakarta Utara", "UPPPD Koja"),
    ("Jakarta Utara", "UPPPD Kelapa Gading"),
    ("Jakarta Utara", "UPPPD Cilincing"),
    ("Jakarta Barat", "UPPPD Grogol Petamburan"),
    ("Jakarta Barat", "UPPPD Taman Sari"),
    ("Jakarta Barat", "UPPPD Tambora"),
    ("Jakarta Barat", "UPPPD Kebon Jeruk"),
    ("Jakarta Barat", "UPPPD Palmerah"),
    ("Jakarta Barat", "UPPPD Kembangan"),
    ("Jakarta Barat", "UPPPD Cengkareng"),
    ("Jakarta Barat", "UPPPD Kalideres"),
    ("Jakarta Selatan", "UPPPD Kebayoran Baru"),
    ("Jakarta Selatan", "UPPPD Kebayoran Lama"),
    ("Jakarta Selatan", "UPPPD Pesanggrahan"),
    ("Jakarta Selatan", "UPPPD Cilandak"),
    ("Jakarta Selatan", "UPPPD Pasar Minggu"),
    ("Jakarta Selatan", "UPPPD Jagakarsa"),
    ("Jakarta Selatan", "UPPPD Mampang Prapatan"),
    ("Jakarta Selatan", "UPPPD Pancoran"),
    ("Jakarta Selatan", "UPPPD Tebet"),
    ("Jakarta Selatan", "UPPPD Setiabudi"),
    ("Jakarta Timur", "UPPPD Matraman"),
    ("Jakarta Timur", "UPPPD Pulogadung"),
    ("Jakarta Timur", "UPPPD Jatinegara"),
    ("Jakarta Timur", "UPPPD Duren Sawit"),
    ("Jakarta Timur", "UPPPD Kramat Jati"),
    ("Jakarta Timur", "UPPPD Makasar"),
    ("Jakarta Timur", "UPPPD Pasar Rebo"),
    ("Jakarta Timur", "UPPPD Ciracas"),
    ("Jakarta Timur", "UPPPD Cipayung"),
    ("Jakarta Timur", "UPPPD Cakung"),
)


def _slug_code(name: str) -> str:
    # "UPPPD Tanah Abang" -> "UPPPD-TANAH-ABANG" (deterministic, human readable).
    return name.upper().replace(" ", "-")


def upgrade() -> None:
    conn = op.get_bind()

    for city, name in _UPPPD:
        code = _slug_code(name)
        conn.execute(
            sa.text(
                """
                INSERT INTO branches (
                    id, code, name, city, is_active, created_at, updated_at
                )
                VALUES (
                    gen_random_uuid(), :code, :name, :city, true, now(), now()
                )
                ON CONFLICT (code) DO UPDATE SET
                    name = EXCLUDED.name,
                    city = EXCLUDED.city,
                    is_active = true,
                    deleted_at = NULL,
                    updated_at = now()
                """
            ),
            {"code": code, "name": name, "city": city},
        )


def downgrade() -> None:
    # Leave seeded branch master data — may be live-referenced by users/complaints.
    pass
