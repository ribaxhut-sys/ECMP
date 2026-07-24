"""Create permissions table for Permission Management (TASK-034).

Revision ID: 0021_permissions
Revises: 0020_roles
Create Date: 2026-07-24

Seeds baseline system permissions used by the application. Role↔permission
matrix and Authorization Engine wiring remain out of scope.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0021_permissions"
down_revision: Union[str, None] = "0020_roles"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# (code, name, module, description)
_SEED_PERMISSIONS: tuple[tuple[str, str, str, str], ...] = (
    ("complaint:read", "Complaint Read", "complaint", "Read complaints"),
    ("complaint:create", "Complaint Create", "complaint", "Create complaints"),
    ("complaint:update", "Complaint Update", "complaint", "Update complaints"),
    ("complaint:delete", "Complaint Delete", "complaint", "Delete complaints"),
    ("assignment:read", "Assignment Read", "assignment", "Read assignments"),
    ("assignment:update", "Assignment Update", "assignment", "Update assignments"),
    ("appointment:read", "Appointment Read", "appointment", "Read appointments"),
    ("appointment:create", "Appointment Create", "appointment", "Create appointments"),
    ("appointment:update", "Appointment Update", "appointment", "Update appointments"),
    ("appointment:delete", "Appointment Delete", "appointment", "Delete appointments"),
    ("resolution:read", "Resolution Read", "resolution", "Read resolutions"),
    ("resolution:create", "Resolution Create", "resolution", "Create resolutions"),
    ("resolution:update", "Resolution Update", "resolution", "Update resolutions"),
    ("resolution:delete", "Resolution Delete", "resolution", "Delete resolutions"),
    ("escalation:read", "Escalation Read", "escalation", "Read escalations"),
    ("escalation:create", "Escalation Create", "escalation", "Create escalations"),
    ("escalation:update", "Escalation Update", "escalation", "Update escalations"),
    ("escalation:delete", "Escalation Delete", "escalation", "Delete escalations"),
    ("dashboard:read", "Dashboard Read", "dashboard", "Read dashboard summary"),
    ("settings:read", "Settings Read", "settings", "Read system settings"),
    ("settings:update", "Settings Update", "settings", "Update system settings"),
    ("attachment:read", "Attachment Read", "attachment", "Read attachments"),
    ("attachment:create", "Attachment Create", "attachment", "Upload attachments"),
    ("attachment:delete", "Attachment Delete", "attachment", "Soft-delete attachments"),
    ("notification:read", "Notification Read", "notification", "Read notifications"),
    ("notification:create", "Notification Create", "notification", "Create notifications"),
    ("notification:update", "Notification Update", "notification", "Update notifications"),
    ("notification:delete", "Notification Delete", "notification", "Delete notifications"),
    ("audit:read", "Audit Read", "audit", "Read audit logs"),
    ("role:read", "Role Read", "role", "Read roles"),
    ("role:create", "Role Create", "role", "Create roles"),
    ("role:update", "Role Update", "role", "Update roles"),
    ("role:delete", "Role Delete", "role", "Soft-delete roles"),
    ("permission:read", "Permission Read", "permission", "Read permissions"),
    ("permission:create", "Permission Create", "permission", "Create permissions"),
    ("permission:update", "Permission Update", "permission", "Update permissions"),
    ("permission:delete", "Permission Delete", "permission", "Soft-delete permissions"),
)


def upgrade() -> None:
    op.create_table(
        "permissions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("code", sa.String(length=150), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("module", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "is_system",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_permissions"),
        sa.UniqueConstraint("code", name="uq_permissions_code"),
    )
    op.create_index("ix_permissions_module", "permissions", ["module"])
    op.create_index("ix_permissions_is_active", "permissions", ["is_active"])
    op.create_index("ix_permissions_is_system", "permissions", ["is_system"])
    op.create_index("ix_permissions_deleted_at", "permissions", ["deleted_at"])

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
            {
                "code": code,
                "name": name,
                "module": module,
                "description": description,
            },
        )


def downgrade() -> None:
    op.drop_index("ix_permissions_deleted_at", table_name="permissions")
    op.drop_index("ix_permissions_is_system", table_name="permissions")
    op.drop_index("ix_permissions_is_active", table_name="permissions")
    op.drop_index("ix_permissions_module", table_name="permissions")
    op.drop_table("permissions")
