"""Seed internal complaint cancel reason preset tags (internal_complaint.cancel_reason_presets).

Revision ID: 0088_cancel_reason_presets
Revises: 0087_internal_pusat_handled_at
Create Date: 2026-08-19
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0088_cancel_reason_presets"
down_revision: Union[str, None] = "0087_internal_pusat_handled_at"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_KEY = "internal_complaint.cancel_reason_presets"
_VALUE = '["Duplikat","Input salah","Pembatalan wajib pajak"]'


def upgrade() -> None:
    conn = op.get_bind()
    exists = conn.execute(
        sa.text("SELECT 1 FROM settings WHERE key = :key"),
        {"key": _KEY},
    ).first()
    if exists:
        return
    conn.execute(
        sa.text(
            "INSERT INTO settings "
            "(id, key, value, value_type, category, visibility, description, "
            "created_at, updated_at) "
            "VALUES (gen_random_uuid(), :key, :value, 'JSON', 'internal_complaint', "
            "'PUBLIC', :description, now(), now())"
        ),
        {
            "key": _KEY,
            "value": _VALUE,
            "description": "Quick-fill reason presets for the internal complaint cancel dialog",
        },
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM settings WHERE key = :key"), {"key": _KEY})
