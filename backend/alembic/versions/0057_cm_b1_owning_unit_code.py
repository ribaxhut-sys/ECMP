"""Normalize cm_batch1 owning_unit_id UUID → Branch.code.

Revision ID: 0057_cm_b1_owning_unit_code
Revises: 0056_cm_b1_owning_unit
Create Date: 2026-08-08

Lab FE sent Branch.id as recordingUnitId; 0056 backfill copied that UUID into
owning_unit_id. Visibility/dashboard match Branch.code — rewrite UUID rows.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0057_cm_b1_owning_unit_code"
down_revision: Union[str, None] = "0056_cm_b1_owning_unit"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            UPDATE cm_batch1_complaints AS c
            SET owning_unit_id = b.code
            FROM branches AS b
            WHERE c.owning_unit_id = b.id::text
              AND b.deleted_at IS NULL
            """
        )
    )


def downgrade() -> None:
    # Irreversible without original UUID map; leave codes in place.
    pass
