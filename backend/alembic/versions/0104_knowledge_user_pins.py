"""Per-user Knowledge pins — pinned records sort to the top of the catalog.

Revision ID: 0104_knowledge_user_pins
Revises: 0103_attachment_user_pins
Create Date: 2026-08-23

Same shape and same reasoning as ``attachment_user_pins`` (0103): a pin is a
presentation preference, never an access grant, and ``user_id`` carries no FK
— the identity contract with the platform is still open (see 0103's own
docstring). Kept as its own table rather than a shared polymorphic "pin"
concept: Knowledge and Attachment are different aggregates with different
visibility rules, and a generic pin service is not something this module
needs yet (CLAUDE.md §1 — no framework beyond what's asked).
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0104_knowledge_user_pins"
down_revision: Union[str, None] = "0103_attachment_user_pins"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "knowledge_user_pins",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "knowledge_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "pinned_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["knowledge_id"],
            ["knowledge.id"],
            name="fk_knowledge_user_pins_knowledge_id_knowledge",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "knowledge_id",
            "user_id",
            name="uq_knowledge_user_pins_pair",
        ),
    )
    op.create_index(
        "ix_knowledge_user_pins_user_id",
        "knowledge_user_pins",
        ["user_id"],
    )
    op.create_index(
        "ix_knowledge_user_pins_knowledge_id",
        "knowledge_user_pins",
        ["knowledge_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_knowledge_user_pins_knowledge_id",
        table_name="knowledge_user_pins",
    )
    op.drop_index(
        "ix_knowledge_user_pins_user_id",
        table_name="knowledge_user_pins",
    )
    op.drop_table("knowledge_user_pins")
