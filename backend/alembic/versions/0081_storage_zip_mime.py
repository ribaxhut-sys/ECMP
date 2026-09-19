"""Allow ZIP in storage.allowed.mime (complaint-module uploads).

Revision ID: 0081_storage_zip_mime
Revises: 0080_internal_withdraw
Create Date: 2026-08-17

ZIP is stored as an opaque blob (never extracted). Canonical MIME only:
application/zip. Aliases are normalized at upload time.
"""

from __future__ import annotations

import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0081_storage_zip_mime"
down_revision: Union[str, None] = "0080_internal_withdraw"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_KEY = "storage.allowed.mime"
_ZIP = "application/zip"


def _load_list(raw: object) -> list[object] | None:
    if raw is None:
        return None
    try:
        parsed = json.loads(raw) if isinstance(raw, str) else raw
    except (TypeError, json.JSONDecodeError):
        return None
    if not isinstance(parsed, list):
        return None
    return parsed


def upgrade() -> None:
    conn = op.get_bind()
    row = conn.execute(
        sa.text("SELECT value FROM settings WHERE key = :k"), {"k": _KEY}
    ).fetchone()
    if row is None:
        return
    current = _load_list(row[0])
    if current is None or _ZIP in current:
        return
    current.append(_ZIP)
    conn.execute(
        sa.text("UPDATE settings SET value = :v WHERE key = :k"),
        {"v": json.dumps(current, separators=(",", ":")), "k": _KEY},
    )


def downgrade() -> None:
    conn = op.get_bind()
    row = conn.execute(
        sa.text("SELECT value FROM settings WHERE key = :k"), {"k": _KEY}
    ).fetchone()
    if row is None:
        return
    current = _load_list(row[0])
    if current is None or _ZIP not in current:
        return
    next_value = [item for item in current if item != _ZIP]
    conn.execute(
        sa.text("UPDATE settings SET value = :v WHERE key = :k"),
        {"v": json.dumps(next_value, separators=(",", ":")), "k": _KEY},
    )
