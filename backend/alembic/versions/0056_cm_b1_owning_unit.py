"""Add owning_unit_id on cm_batch1_complaints (list visibility SoT).

Revision ID: 0056_cm_b1_owning_unit
Revises: 0055_manager_dashboard_read
Create Date: 2026-08-08

Persists organization unit on the Aggregate so list/dashboard/org-guard share
one column (DEC-024 pattern). Backfill from ComplaintCreated outbox
recordingUnitId, then creator User.branch → Branch.code.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0056_cm_b1_owning_unit"
down_revision: Union[str, None] = "0055_manager_dashboard_read"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cm_batch1_complaints",
        sa.Column("owning_unit_id", sa.String(length=128), nullable=True),
    )
    op.create_index(
        "ix_cm_batch1_complaints_owning_unit_id",
        "cm_batch1_complaints",
        ["owning_unit_id"],
    )

    conn = op.get_bind()
    # Prefer latest ComplaintCreated outbox payload (Postgres JSON).
    conn.execute(
        sa.text(
            """
            UPDATE cm_batch1_complaints AS c
            SET owning_unit_id = sub.unit
            FROM (
                SELECT DISTINCT ON (o.aggregate_id)
                    o.aggregate_id AS aggregate_id,
                    NULLIF(
                        TRIM(
                            COALESCE(
                                o.payload_json::json ->> 'recordingUnitId',
                                o.payload_json::json ->> 'recording_unit_id',
                                o.payload_json::json ->> 'orgUnitId',
                                o.payload_json::json ->> 'org_unit_id'
                            )
                        ),
                        ''
                    ) AS unit
                FROM cm_batch1_outbox AS o
                WHERE o.aggregate_type = 'Complaint'
                  AND o.event_name = 'ComplaintCreated'
                ORDER BY o.aggregate_id, o.created_at DESC
            ) AS sub
            WHERE c.id::text = sub.aggregate_id
              AND sub.unit IS NOT NULL
              AND c.owning_unit_id IS NULL
            """
        )
    )
    # Fallback: creator's branch code when still null.
    conn.execute(
        sa.text(
            """
            UPDATE cm_batch1_complaints AS c
            SET owning_unit_id = b.code
            FROM users AS u
            JOIN branches AS b ON b.id = u.branch_id
            WHERE c.owning_unit_id IS NULL
              AND c.created_by IS NOT NULL
              AND u.deleted_at IS NULL
              AND b.deleted_at IS NULL
              AND (
                    c.created_by = u.id::text
                    OR c.created_by = u.username
                  )
            """
        )
    )


def downgrade() -> None:
    op.drop_index(
        "ix_cm_batch1_complaints_owning_unit_id",
        table_name="cm_batch1_complaints",
    )
    op.drop_column("cm_batch1_complaints", "owning_unit_id")
