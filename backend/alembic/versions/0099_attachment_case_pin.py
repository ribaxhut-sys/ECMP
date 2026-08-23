"""Optional Case pin on Batch 1 attachments (FR-004).

Revision ID: 0099_attachment_case_pin
Revises: 0098_case_escalate_to_pusat
Create Date: 2026-08-23

Stores optional case_id so evidence can be pinned to a Case that belongs
to the same Complaint. NULL = shared complaint evidence (intake / D-02).
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0099_attachment_case_pin"
down_revision: Union[str, None] = "0098_case_escalate_to_pusat"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cm_batch1_attachments",
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index(
        "ix_cm_batch1_attachments_case_id",
        "cm_batch1_attachments",
        ["case_id"],
    )
    op.create_foreign_key(
        "fk_cm_batch1_attachments_case_id",
        "cm_batch1_attachments",
        "cm_cases",
        ["case_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_cm_batch1_attachments_case_id",
        "cm_batch1_attachments",
        type_="foreignkey",
    )
    op.drop_index(
        "ix_cm_batch1_attachments_case_id",
        table_name="cm_batch1_attachments",
    )
    op.drop_column("cm_batch1_attachments", "case_id")
