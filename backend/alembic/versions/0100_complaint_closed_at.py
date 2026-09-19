"""Complaint closure timestamp for the 30-day resolution SLA (DEC-031).

Revision ID: 0100_complaint_closed_at
Revises: 0099_attachment_case_pin
Create Date: 2026-08-23

``cm_batch1_complaints`` recorded *that* a complaint closed but never *when*.
``updated_at`` cannot stand in: any later edit moves it, so it would silently
misreport whether the 30-day target was met.

Backfill reads the closing event out of ``timeline_entries`` — the same events
the dashboard activity feed already treats as closure
(``CmBatch1ActivityDashboardProvider._is_case_closed_event``). Verified on the
lab database 2026-08-23: 21 of 21 CLOSED complaints carry one, so no closed row
is left without a timestamp. Rows that somehow lack the event keep NULL and are
reported as "SLA unknown" rather than being given a fabricated date.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0100_complaint_closed_at"
down_revision: Union[str, None] = "0099_attachment_case_pin"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Earliest closing event per complaint. MIN, not MAX: a complaint that was
# closed, reopened and closed again should be measured from the closure that
# is current, but the reopen path clears ``closed_at`` and the next closure
# re-stamps it, so at backfill time the earliest is the only defensible pick
# for rows whose history we cannot replay.
_BACKFILL = sa.text(
    """
    UPDATE cm_batch1_complaints AS c
       SET closed_at = t.closed_at
      FROM (
            SELECT aggregate_id, MIN(created_at) AS closed_at
              FROM timeline_entries
             WHERE aggregate_type = 'Complaint'
               AND (
                     event_type IN ('CaseClosed', 'HqCompleted')
                  OR (
                       event_type = 'IntakeDispositionRecorded'
                   AND metadata ->> 'intakeDisposition'
                       IN ('BRANCH_CLOSED', 'HQ_CLOSED', 'ALL_CASES_CANCELLED')
                     )
                   )
             GROUP BY aggregate_id
           ) AS t
     WHERE c.id = t.aggregate_id
       AND c.status = 'CLOSED'
       AND c.closed_at IS NULL
    """
)


def upgrade() -> None:
    op.add_column(
        "cm_batch1_complaints",
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
    )
    # Partial index: the SLA feed only ever scans complaints that are still
    # open (closed_at IS NULL) looking for ones past their target.
    op.create_index(
        "ix_cm_batch1_complaints_open_created_at",
        "cm_batch1_complaints",
        ["created_at"],
        postgresql_where=sa.text("closed_at IS NULL"),
    )
    op.execute(_BACKFILL)


def downgrade() -> None:
    op.drop_index(
        "ix_cm_batch1_complaints_open_created_at",
        table_name="cm_batch1_complaints",
    )
    op.drop_column("cm_batch1_complaints", "closed_at")
