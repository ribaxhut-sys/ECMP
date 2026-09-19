"""Knowledge ↔ Attachment relation (source files) + one-primary-per-Knowledge.

Revision ID: 0071_knowledge_files
Revises: 0070_knowledge_permissions
Create Date: 2026-08-11

Reuses the existing generic ``attachments`` table (CAPABILITY-011) for
storage/upload/download/checksum — this migration only adds the join table
that records which platform attachment belongs to which Knowledge, and its
role (PRIMARY or SUPPORTING). A partial unique index guarantees at most one
PRIMARY per Knowledge at the database level (ECMP Modul Pengetahuan §10).
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0071_knowledge_files"
down_revision: Union[str, None] = "0070_knowledge_permissions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "knowledge_files",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("knowledge_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("attachment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="SUPPORTING"),
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
        sa.ForeignKeyConstraint(
            ["knowledge_id"],
            ["knowledge.id"],
            name="fk_knowledge_files_knowledge_id_knowledge",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["attachment_id"],
            ["attachments.id"],
            name="fk_knowledge_files_attachment_id_attachments",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "knowledge_id", "attachment_id", name="uq_knowledge_files_pair"
        ),
    )
    op.create_index(
        "ix_knowledge_files_knowledge_id", "knowledge_files", ["knowledge_id"]
    )
    op.create_index(
        "ix_knowledge_files_attachment_id", "knowledge_files", ["attachment_id"]
    )
    op.create_index(
        "uq_knowledge_files_one_primary",
        "knowledge_files",
        ["knowledge_id"],
        unique=True,
        postgresql_where=sa.text("role = 'PRIMARY'"),
    )


def downgrade() -> None:
    op.drop_index("uq_knowledge_files_one_primary", table_name="knowledge_files")
    op.drop_index("ix_knowledge_files_attachment_id", table_name="knowledge_files")
    op.drop_index("ix_knowledge_files_knowledge_id", table_name="knowledge_files")
    op.drop_table("knowledge_files")
