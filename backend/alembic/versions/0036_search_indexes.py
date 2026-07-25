"""CAPABILITY-012 — search support indexes on complaints (no search tables).

Revision ID: 0036_search_indexes
Revises: 0035_attachment_domain
Create Date: 2026-07-25

Adds indexes used by Complaint search filters/sort only. Does not alter
Complaint / Queue / Notification / Timeline / Attachment domain tables
beyond index DDL.
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "0036_search_indexes"
down_revision: Union[str, None] = "0035_attachment_domain"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("ix_complaints_created_at", "complaints", ["created_at"])
    op.create_index("ix_complaints_updated_at", "complaints", ["updated_at"])
    op.create_index("ix_complaints_category", "complaints", ["category"])
    op.create_index("ix_complaints_created_by", "complaints", ["created_by"])


def downgrade() -> None:
    op.drop_index("ix_complaints_created_by", table_name="complaints")
    op.drop_index("ix_complaints_category", table_name="complaints")
    op.drop_index("ix_complaints_updated_at", table_name="complaints")
    op.drop_index("ix_complaints_created_at", table_name="complaints")
