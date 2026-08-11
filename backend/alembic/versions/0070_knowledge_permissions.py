"""Seed knowledge:read / knowledge:manage permissions (Pengetahuan).

Revision ID: 0070_knowledge_permissions
Revises: 0069_knowledge
Create Date: 2026-08-11

Business decision (LOCKED — ECMP Modul Pengetahuan §3):
  - knowledge:manage (create/update/publish/archive/delete/upload) — only
    Admin Pusat / Supervisor Pusat / Manager Pusat, i.e. the ADMIN,
    SUPERVISOR, MANAGER system roles (aliases included for parity — see
    gates.py _KNOWLEDGE_ADMIN_ROLES / _KNOWLEDGE_UNIT_ROLES). Identical
    role set to announcement:manage (0063_announcement_permissions).
  - knowledge:read — every role that already holds complaints:read (global
    read, Pusat-curated), mirroring announcement:read's reasoning exactly.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0070_knowledge_permissions"
down_revision: Union[str, None] = "0069_knowledge"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_SEED_PERMISSIONS: tuple[tuple[str, str, str, str], ...] = (
    (
        "knowledge:read",
        "Knowledge Read",
        "knowledge",
        "View Pengaduan module Knowledge (Pengetahuan)",
    ),
    (
        "knowledge:manage",
        "Knowledge Manage",
        "knowledge",
        "Create / edit / publish / archive / delete Knowledge and its files",
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

    # knowledge:read follows whoever already has complaints:read.
    conn.execute(sa.text(_GRANT_LIKE_COMPLAINTS_READ_SQL), {"perm_code": "knowledge:read"})

    # knowledge:manage — Admin Pusat / Supervisor Pusat / Manager Pusat only.
    for role_code in _MANAGE_ROLE_CODES:
        conn.execute(
            sa.text(_GRANT_SQL),
            {"role_code": role_code, "perm_code": "knowledge:manage"},
        )
        conn.execute(
            sa.text(_GRANT_SQL),
            {"role_code": role_code, "perm_code": "knowledge:read"},
        )


def downgrade() -> None:
    # Non-destructive — do not strip grants that may be in use.
    pass
