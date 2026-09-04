"""Pengetahuan (Knowledge Module) — persistence table.

Revision ID: 0069_knowledge
Revises: 0068_ann_attach_access
Create Date: 2026-08-11

Business decision (LOCKED — ECMP Modul Pengetahuan §4–9): lifecycle
DRAFT -> ACTIVE -> ARCHIVED, no EXPIRED status column (derived at read time
from effective_from/effective_to). Versioning = a new record per version
(``supersedes_knowledge_id``), no ``knowledge_versions`` table. Mirrors the
plain-timestamp / TimestampAuditSoftDeleteMixin shape already used by
``announcements`` (0062_announcements) — no bespoke audit system.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0069_knowledge"
down_revision: Union[str, None] = "0068_ann_attach_access"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "knowledge",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("knowledge_type", sa.String(32), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="DRAFT"),
        sa.Column("document_number", sa.String(100), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("version_label", sa.String(32), nullable=True),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("effective_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("owner_org_unit_id", sa.String(64), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "supersedes_knowledge_id", postgresql.UUID(as_uuid=True), nullable=True
        ),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["supersedes_knowledge_id"],
            ["knowledge.id"],
            name="fk_knowledge_supersedes_knowledge_id_knowledge",
            ondelete="SET NULL",
        ),
    )
    op.create_index("ix_knowledge_status", "knowledge", ["status"])
    op.create_index("ix_knowledge_knowledge_type", "knowledge", ["knowledge_type"])
    op.create_index("ix_knowledge_published_at", "knowledge", ["published_at"])
    op.create_index(
        "ix_knowledge_supersedes_knowledge_id", "knowledge", ["supersedes_knowledge_id"]
    )
    op.create_index("ix_knowledge_deleted_at", "knowledge", ["deleted_at"])


def downgrade() -> None:
    op.drop_index("ix_knowledge_deleted_at", table_name="knowledge")
    op.drop_index("ix_knowledge_supersedes_knowledge_id", table_name="knowledge")
    op.drop_index("ix_knowledge_published_at", table_name="knowledge")
    op.drop_index("ix_knowledge_knowledge_type", table_name="knowledge")
    op.drop_index("ix_knowledge_status", table_name="knowledge")
    op.drop_table("knowledge")
