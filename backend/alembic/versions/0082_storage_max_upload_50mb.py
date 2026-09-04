"""Raise default attachment upload cap to 50 MB.

Revision ID: 0082_storage_max_upload_50mb
Revises: 0081_storage_zip_mime
Create Date: 2026-08-17

Updates settings key storage.max.upload.mb (CAPABILITY-011). Batch-1
AttachmentConfig default is aligned in code to 50 MiB.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0082_storage_max_upload_50mb"
down_revision: Union[str, None] = "0081_storage_zip_mime"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_KEY = "storage.max.upload.mb"
_NEW = "50"
_OLD = "10"


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text("UPDATE settings SET value = :v WHERE key = :k"),
        {"v": _NEW, "k": _KEY},
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text("UPDATE settings SET value = :v WHERE key = :k"),
        {"v": _OLD, "k": _KEY},
    )
