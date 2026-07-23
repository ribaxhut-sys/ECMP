"""Initial ECMP v1.0 schema.

Revision ID: 0001_ecmp_v1_schema
Revises:
Create Date: 2026-07-22

Tables: roles, users, branches, customers, complaints,
complaint_assignments, complaint_escalations, complaint_timelines, attachments.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_ecmp_v1_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    op.create_table(
        "roles",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
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
        sa.PrimaryKeyConstraint("id", name="pk_roles"),
        sa.UniqueConstraint("code", name="uq_roles_code"),
    )
    op.create_index("ix_roles_deleted_at", "roles", ["deleted_at"])
    op.create_index("ix_roles_is_active", "roles", ["is_active"])

    op.create_table(
        "branches",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("parent_branch_id", postgresql.UUID(as_uuid=True), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["parent_branch_id"],
            ["branches.id"],
            name="fk_branches_parent_branch_id_branches",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_branches"),
        sa.UniqueConstraint("code", name="uq_branches_code"),
    )
    op.create_index("ix_branches_deleted_at", "branches", ["deleted_at"])
    op.create_index("ix_branches_is_active", "branches", ["is_active"])
    op.create_index("ix_branches_parent_branch_id", "branches", ["parent_branch_id"])

    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["branch_id"],
            ["branches.id"],
            name="fk_users_branch_id_branches",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
            name="fk_users_role_id_roles",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.UniqueConstraint("username", name="uq_users_username"),
    )
    op.create_index("ix_users_branch_id", "users", ["branch_id"])
    op.create_index("ix_users_deleted_at", "users", ["deleted_at"])
    op.create_index("ix_users_is_active", "users", ["is_active"])
    op.create_index("ix_users_role_id", "users", ["role_id"])

    op.create_table(
        "customers",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("external_customer_id", sa.String(length=64), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.PrimaryKeyConstraint("id", name="pk_customers"),
        sa.UniqueConstraint(
            "external_customer_id", name="uq_customers_external_customer_id"
        ),
    )
    op.create_index("ix_customers_deleted_at", "customers", ["deleted_at"])
    op.create_index("ix_customers_email", "customers", ["email"])
    op.create_index("ix_customers_phone", "customers", ["phone"])

    op.create_table(
        "complaints",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("complaint_number", sa.String(length=32), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("subject", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("priority", sa.String(length=16), nullable=False),
        sa.Column("channel", sa.String(length=32), nullable=True),
        sa.Column("category", sa.String(length=64), nullable=True),
        sa.Column("reported_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["branch_id"],
            ["branches.id"],
            name="fk_complaints_branch_id_branches",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["customers.id"],
            name="fk_complaints_customer_id_customers",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_complaints"),
        sa.UniqueConstraint("complaint_number", name="uq_complaints_complaint_number"),
    )
    op.create_index("ix_complaints_branch_id", "complaints", ["branch_id"])
    op.create_index("ix_complaints_customer_id", "complaints", ["customer_id"])
    op.create_index("ix_complaints_deleted_at", "complaints", ["deleted_at"])
    op.create_index("ix_complaints_priority", "complaints", ["priority"])
    op.create_index("ix_complaints_reported_at", "complaints", ["reported_at"])
    op.create_index("ix_complaints_status", "complaints", ["status"])
    op.create_index(
        "ix_complaints_status_priority", "complaints", ["status", "priority"]
    )

    op.create_table(
        "complaint_assignments",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("complaint_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assignee_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assigned_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("unassigned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_current", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["assignee_id"],
            ["users.id"],
            name="fk_complaint_assignments_assignee_id_users",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["assigned_by"],
            ["users.id"],
            name="fk_complaint_assignments_assigned_by_users",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["complaint_id"],
            ["complaints.id"],
            name="fk_complaint_assignments_complaint_id_complaints",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_complaint_assignments"),
    )
    op.create_index(
        "ix_complaint_assignments_assignee_id",
        "complaint_assignments",
        ["assignee_id"],
    )
    op.create_index(
        "ix_complaint_assignments_assigned_by",
        "complaint_assignments",
        ["assigned_by"],
    )
    op.create_index(
        "ix_complaint_assignments_complaint_id",
        "complaint_assignments",
        ["complaint_id"],
    )
    op.create_index(
        "ix_complaint_assignments_complaint_current",
        "complaint_assignments",
        ["complaint_id", "is_current"],
    )
    op.create_index(
        "ix_complaint_assignments_deleted_at",
        "complaint_assignments",
        ["deleted_at"],
    )

    op.create_table(
        "complaint_escalations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("complaint_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("escalated_from_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("escalated_to_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("escalated_to_role_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("level", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("escalated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["complaint_id"],
            ["complaints.id"],
            name="fk_complaint_escalations_complaint_id_complaints",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["escalated_from_user_id"],
            ["users.id"],
            name="fk_complaint_escalations_escalated_from_user_id_users",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["escalated_to_role_id"],
            ["roles.id"],
            name="fk_complaint_escalations_escalated_to_role_id_roles",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["escalated_to_user_id"],
            ["users.id"],
            name="fk_complaint_escalations_escalated_to_user_id_users",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_complaint_escalations"),
    )
    op.create_index(
        "ix_complaint_escalations_complaint_id",
        "complaint_escalations",
        ["complaint_id"],
    )
    op.create_index(
        "ix_complaint_escalations_deleted_at",
        "complaint_escalations",
        ["deleted_at"],
    )
    op.create_index(
        "ix_complaint_escalations_escalated_to_role_id",
        "complaint_escalations",
        ["escalated_to_role_id"],
    )
    op.create_index(
        "ix_complaint_escalations_escalated_to_user_id",
        "complaint_escalations",
        ["escalated_to_user_id"],
    )
    op.create_index("ix_complaint_escalations_level", "complaint_escalations", ["level"])
    op.create_index(
        "ix_complaint_escalations_status", "complaint_escalations", ["status"]
    )

    op.create_table(
        "complaint_timelines",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("complaint_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("event_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("from_status", sa.String(length=32), nullable=True),
        sa.Column("to_status", sa.String(length=32), nullable=True),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["actor_user_id"],
            ["users.id"],
            name="fk_complaint_timelines_actor_user_id_users",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["complaint_id"],
            ["complaints.id"],
            name="fk_complaint_timelines_complaint_id_complaints",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_complaint_timelines"),
    )
    op.create_index(
        "ix_complaint_timelines_complaint_event_at",
        "complaint_timelines",
        ["complaint_id", "event_at"],
    )
    op.create_index(
        "ix_complaint_timelines_complaint_id",
        "complaint_timelines",
        ["complaint_id"],
    )
    op.create_index(
        "ix_complaint_timelines_deleted_at", "complaint_timelines", ["deleted_at"]
    )
    op.create_index(
        "ix_complaint_timelines_event_at", "complaint_timelines", ["event_at"]
    )
    op.create_index(
        "ix_complaint_timelines_event_type", "complaint_timelines", ["event_type"]
    )

    op.create_table(
        "attachments",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("complaint_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("storage_key", sa.String(length=512), nullable=False),
        sa.Column("content_type", sa.String(length=128), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["complaint_id"],
            ["complaints.id"],
            name="fk_attachments_complaint_id_complaints",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["uploaded_by"],
            ["users.id"],
            name="fk_attachments_uploaded_by_users",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_attachments"),
    )
    op.create_index("ix_attachments_complaint_id", "attachments", ["complaint_id"])
    op.create_index("ix_attachments_deleted_at", "attachments", ["deleted_at"])
    op.create_index("ix_attachments_storage_key", "attachments", ["storage_key"])
    op.create_index("ix_attachments_uploaded_by", "attachments", ["uploaded_by"])


def downgrade() -> None:
    op.drop_table("attachments")
    op.drop_table("complaint_timelines")
    op.drop_table("complaint_escalations")
    op.drop_table("complaint_assignments")
    op.drop_table("complaints")
    op.drop_table("customers")
    op.drop_table("users")
    op.drop_table("branches")
    op.drop_table("roles")
