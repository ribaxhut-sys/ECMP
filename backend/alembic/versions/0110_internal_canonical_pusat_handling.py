"""Collapse Internal handling sub-units (PUSAT-CRO, …) to canonical PUSAT.

Revision ID: 0110_internal_canonical_pusat_handling
Revises: 0109_cm_hq_holiday_kind
Create Date: 2026-09-02

Pengaduan Internal has one Pusat door. HQ visit schedule (PUSAT-CRO) is
unchanged — this rewrite is internal_complaints only.
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "0110_internal_canonical_pusat_handling"
down_revision: Union[str, None] = "0109_cm_hq_holiday_kind"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_PUSAT_SUBUNIT = """
(
    UPPER(TRIM({col})) IN ('HO', 'HEAD_OFFICE', 'HEAD-OFFICE')
    OR UPPER(TRIM({col})) LIKE 'PUSAT-%'
    OR UPPER(TRIM({col})) LIKE 'PUSAT.%'
    OR UPPER(TRIM({col})) LIKE 'PUSAT/%'
    OR UPPER(TRIM({col})) LIKE 'HO-%'
    OR UPPER(TRIM({col})) LIKE 'HO.%'
    OR UPPER(TRIM({col})) LIKE 'HO/%'
    OR UPPER(TRIM({col})) LIKE 'HEAD_OFFICE-%'
    OR UPPER(TRIM({col})) LIKE 'HEAD_OFFICE.%'
    OR UPPER(TRIM({col})) LIKE 'HEAD_OFFICE/%'
    OR UPPER(TRIM({col})) LIKE 'HEAD-OFFICE-%'
    OR UPPER(TRIM({col})) LIKE 'HEAD-OFFICE.%'
    OR UPPER(TRIM({col})) LIKE 'HEAD-OFFICE/%'
)
"""


def upgrade() -> None:
    handling = _PUSAT_SUBUNIT.format(col="handling_unit_id")
    dest = _PUSAT_SUBUNIT.format(col="transfer_request_destination_unit_id")
    op.execute(
        f"""
        UPDATE internal_complaints
        SET handling_unit_id = 'PUSAT'
        WHERE handling_unit_id IS NOT NULL
          AND UPPER(TRIM(handling_unit_id)) <> 'PUSAT'
          AND {handling}
        """
    )
    op.execute(
        f"""
        UPDATE internal_complaints
        SET transfer_request_destination_unit_id = 'PUSAT'
        WHERE transfer_request_destination_unit_id IS NOT NULL
          AND UPPER(TRIM(transfer_request_destination_unit_id)) <> 'PUSAT'
          AND {dest}
        """
    )
    for col in ("source_unit_id", "target_unit_id", "actor_unit_id"):
        clause = _PUSAT_SUBUNIT.format(col=col)
        op.execute(
            f"""
            UPDATE internal_complaint_events
            SET {col} = 'PUSAT'
            WHERE {col} IS NOT NULL
              AND UPPER(TRIM({col})) <> 'PUSAT'
              AND {clause}
            """
        )


def downgrade() -> None:
    # Irreversible: original sub-unit codes are not stored.
    pass
