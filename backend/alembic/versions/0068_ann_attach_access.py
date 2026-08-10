"""Announcement attachment catalog access (PUBLIC/PRIVATE) + uploader org unit.

Revision ID: 0068_ann_attach_access
Revises: 0067_announcement_ref_num
Create Date: 2026-08-10

Adds catalog-level access metadata on ``attachments`` (nullable — only
populated for Announcement-domain rows). Orthogonal to join-row
``announcement_attachments.visibility`` (IMMEDIATE/PUBLISHED).

Backfill: existing announcement-linked files → PRIVATE; org unit derived
from uploader's branch when available (otherwise NULL — Pusat-only for Private).
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0068_ann_attach_access"
down_revision: Union[str, None] = "0067_announcement_ref_num"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "attachments",
        sa.Column("access_level", sa.String(length=20), nullable=True),
    )
    op.add_column(
        "attachments",
        sa.Column("uploaded_org_unit_id", sa.String(length=64), nullable=True),
    )
    op.create_index(
        "ix_attachments_access_level", "attachments", ["access_level"]
    )
    op.create_index(
        "ix_attachments_uploaded_org_unit_id",
        "attachments",
        ["uploaded_org_unit_id"],
    )

    conn = op.get_bind()
    # Announcement-domain rows that already have a join.
    # PostgreSQL UPDATE … FROM cannot reference the target alias inside JOIN ON.
    conn.execute(
        sa.text(
            """
            UPDATE attachments AS a
            SET access_level = 'PRIVATE',
                uploaded_org_unit_id = src.branch_code
            FROM (
                SELECT DISTINCT ON (aa.attachment_id)
                    aa.attachment_id AS attachment_id,
                    b.code AS branch_code
                FROM announcement_attachments AS aa
                INNER JOIN attachments AS att ON att.id = aa.attachment_id
                LEFT JOIN users AS u
                    ON u.id = att.uploaded_by AND u.deleted_at IS NULL
                LEFT JOIN branches AS b
                    ON b.id = u.branch_id AND b.deleted_at IS NULL
                ORDER BY aa.attachment_id
            ) AS src
            WHERE a.id = src.attachment_id
              AND a.access_level IS NULL
            """
        )
    )
    # Announcement aggregate rows without a join yet (edge).
    conn.execute(
        sa.text(
            """
            UPDATE attachments AS a
            SET access_level = 'PRIVATE',
                uploaded_org_unit_id = src.branch_code
            FROM (
                SELECT
                    att.id AS attachment_id,
                    b.code AS branch_code
                FROM attachments AS att
                LEFT JOIN users AS u
                    ON u.id = att.uploaded_by AND u.deleted_at IS NULL
                LEFT JOIN branches AS b
                    ON b.id = u.branch_id AND b.deleted_at IS NULL
                WHERE att.aggregate_type = 'Announcement'
                  AND att.access_level IS NULL
            ) AS src
            WHERE a.id = src.attachment_id
              AND a.access_level IS NULL
            """
        )
    )
    conn.execute(
        sa.text(
            """
            UPDATE attachments
            SET access_level = 'PRIVATE'
            WHERE aggregate_type = 'Announcement'
              AND access_level IS NULL
            """
        )
    )


def downgrade() -> None:
    op.drop_index("ix_attachments_uploaded_org_unit_id", table_name="attachments")
    op.drop_index("ix_attachments_access_level", table_name="attachments")
    op.drop_column("attachments", "uploaded_org_unit_id")
    op.drop_column("attachments", "access_level")
