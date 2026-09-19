"""DEC-026 M-026-3 — H1 DROP Foundation complaint tables.

Revision ID: 0072_drop_foundation_tables
Revises: 0071_knowledge_files
Create Date: 2026-08-13

Drops unused-leave Foundation persistence after readers moved to CM Aggregate.
Does NOT touch CA BC ``complaint_cases*``, ``cm_batch1_*``, ``sla_policies``,
generic ``attachments``, or ``timeline_entries``.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0072_drop_foundation_tables"
down_revision: Union[str, None] = "0071_knowledge_files"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Child → parent. Appointments hang off complaint_escalations.
_DROP_ORDER = (
    "appointments",
    "sla_records",
    "complaint_timelines",
    "complaint_resolutions",
    "complaint_assignments",
    "complaint_escalations",
    "complaints",
)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = set(inspector.get_table_names())
    for name in _DROP_ORDER:
        if name in existing:
            op.drop_table(name)


def downgrade() -> None:
    raise NotImplementedError(
        "DEC-026 H1 Foundation drop is irreversible; restore from backup if needed."
    )
