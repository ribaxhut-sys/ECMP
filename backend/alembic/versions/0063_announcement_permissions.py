"""Seed announcement:read / announcement:manage permissions (Pengumuman).

Revision ID: 0063_announcement_permissions
Revises: 0062_announcements
Create Date: 2026-08-09

Business decision (LOCKED):
  - announcement:manage (create/update/publish/unpublish/delete) — only
    Admin Pusat / Supervisor Pusat / Manager Pusat, i.e. the ADMIN,
    SUPERVISOR, MANAGER system roles (aliases included for parity with the
    existing admin/supervisor role-code conventions — see gates.py
    _COMPLAINT_CLOSE_ROLES / _USER_STATUS_UPDATE_ROLES).
  - announcement:read — every role that already holds complaints:read, so
    "other roles only see announcements per their existing Pengaduan module
    access" without hardcoding a second role list that could drift from the
    complaint-access matrix.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0063_announcement_permissions"
down_revision: Union[str, None] = "0062_announcements"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_SEED_PERMISSIONS: tuple[tuple[str, str, str, str], ...] = (
    (
        "announcement:read",
        "Announcement Read",
        "announcement",
        "View Pengaduan module announcements",
    ),
    (
        "announcement:manage",
        "Announcement Manage",
        "announcement",
        "Create / edit / publish / unpublish / delete announcements",
    ),
)

_MANAGE_ROLE_CODES: tuple[str, ...] = (
    "ADMIN",
    "ADMINISTRATOR",
    "SUPER_ADMIN",
    "SUPERVISOR",
    "BRANCH_SUPERVISOR",
    "MANAGER",
)

_GRANT_SQL = """
    INSERT INTO role_permissions (id, role_id, permission_id, created_at)
    SELECT gen_random_uuid(), r.id, p.id, now()
    FROM roles r
    CROSS JOIN permissions p
    WHERE r.code = :role_code
      AND p.code = :perm_code
      AND r.deleted_at IS NULL
      AND p.deleted_at IS NULL
      AND NOT EXISTS (
        SELECT 1 FROM role_permissions rp
        WHERE rp.role_id = r.id AND rp.permission_id = p.id
      )
"""

_GRANT_LIKE_COMPLAINTS_READ_SQL = """
    INSERT INTO role_permissions (id, role_id, permission_id, created_at)
    SELECT gen_random_uuid(), rp_src.role_id, p.id, now()
    FROM role_permissions rp_src
    JOIN permissions p_src ON p_src.id = rp_src.permission_id
    CROSS JOIN permissions p
    WHERE p_src.code = 'complaints:read'
      AND p_src.deleted_at IS NULL
      AND p.code = :perm_code
      AND p.deleted_at IS NULL
      AND NOT EXISTS (
        SELECT 1 FROM role_permissions rp
        WHERE rp.role_id = rp_src.role_id AND rp.permission_id = p.id
      )
"""


def upgrade() -> None:
    conn = op.get_bind()

    for code, name, module, description in _SEED_PERMISSIONS:
        conn.execute(
            sa.text(
                """
                INSERT INTO permissions (
                    id, code, name, module, description,
                    is_system, is_active, created_at, updated_at
                )
                VALUES (
                    gen_random_uuid(), :code, :name, :module, :description,
                    true, true, now(), now()
                )
                ON CONFLICT (code) DO UPDATE SET
                    name = EXCLUDED.name,
                    module = EXCLUDED.module,
                    description = COALESCE(permissions.description, EXCLUDED.description),
                    is_system = true,
                    is_active = true,
                    deleted_at = NULL,
                    updated_at = now()
                """
            ),
            {"code": code, "name": name, "module": module, "description": description},
        )

    # announcement:read follows whoever already has complaints:read.
    conn.execute(sa.text(_GRANT_LIKE_COMPLAINTS_READ_SQL), {"perm_code": "announcement:read"})

    # announcement:manage — Admin Pusat / Supervisor Pusat / Manager Pusat only.
    for role_code in _MANAGE_ROLE_CODES:
        conn.execute(
            sa.text(_GRANT_SQL),
            {"role_code": role_code, "perm_code": "announcement:manage"},
        )
        # Manage implies read (management list/table needs announcement:read
        # too — but announcement:manage endpoints are gated on their own
        # permission, so this only matters if a manage-only role somehow
        # lacks complaints:read; harmless no-op otherwise).
        conn.execute(
            sa.text(_GRANT_SQL),
            {"role_code": role_code, "perm_code": "announcement:read"},
        )


def downgrade() -> None:
    # Non-destructive — do not strip grants that may be in use.
    pass
