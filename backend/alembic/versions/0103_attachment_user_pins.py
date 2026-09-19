"""Per-user attachment pins — pinned files sort to the top of the catalog.

Revision ID: 0103_attachment_user_pins
Revises: 0102_hq_capacity_by_unit
Create Date: 2026-08-23

Presentation preference, not domain state: a pin only reorders one user's
view of the catalog and never changes who may see or use a file.

``user_id`` carries no FK to ``users.id`` — same choice as
``announcement_reads`` (0065). The identity contract with the platform is
still open, so this table stays indifferent to how module users are
provisioned. Orphan rows are harmless: the catalog query already filters
``status != DELETED`` and pins are only read for the calling user.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0103_attachment_user_pins"
down_revision: Union[str, None] = "0102_hq_capacity_by_unit"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "attachment_user_pins",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "attachment_id",
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
            ["attachment_id"],
            ["attachments.id"],
            name="fk_attachment_user_pins_attachment_id_attachments",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "attachment_id",
            "user_id",
            name="uq_attachment_user_pins_pair",
        ),
    )
    op.create_index(
        "ix_attachment_user_pins_user_id",
        "attachment_user_pins",
        ["user_id"],
    )
    op.create_index(
        "ix_attachment_user_pins_attachment_id",
        "attachment_user_pins",
        ["attachment_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_attachment_user_pins_attachment_id",
        table_name="attachment_user_pins",
    )
    op.drop_index(
        "ix_attachment_user_pins_user_id",
        table_name="attachment_user_pins",
    )
    op.drop_table("attachment_user_pins")
