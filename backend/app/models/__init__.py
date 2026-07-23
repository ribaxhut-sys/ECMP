"""ORM models for ECMP v1.0 foundation schema."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
    true,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampAuditSoftDeleteMixin


class Role(TimestampAuditSoftDeleteMixin, Base):
    __tablename__ = "roles"
    __table_args__ = (
        UniqueConstraint("code", name="uq_roles_code"),
        Index("ix_roles_is_active", "is_active"),
    )

    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=true()
    )

    users: Mapped[list[User]] = relationship(back_populates="role")


class Branch(TimestampAuditSoftDeleteMixin, Base):
    __tablename__ = "branches"
    __table_args__ = (
        UniqueConstraint("code", name="uq_branches_code"),
        Index("ix_branches_parent_branch_id", "parent_branch_id"),
        Index("ix_branches_is_active", "is_active"),
    )

    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=true()
    )
    parent_branch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("branches.id", ondelete="SET NULL"),
        nullable=True,
    )

    parent: Mapped[Branch | None] = relationship(
        remote_side="Branch.id",
        back_populates="children",
    )
    children: Mapped[list[Branch]] = relationship(back_populates="parent")
    users: Mapped[list[User]] = relationship(back_populates="branch")
    complaints: Mapped[list[Complaint]] = relationship(back_populates="branch")


class User(TimestampAuditSoftDeleteMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        UniqueConstraint("username", name="uq_users_username"),
        Index("ix_users_role_id", "role_id"),
        Index("ix_users_branch_id", "branch_id"),
        Index("ix_users_is_active", "is_active"),
    )

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="RESTRICT"),
        nullable=False,
    )
    branch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("branches.id", ondelete="SET NULL"),
        nullable=True,
    )
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    username: Mapped[str] = mapped_column(String(64), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=true()
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    role: Mapped[Role] = relationship(back_populates="users")
    branch: Mapped[Branch | None] = relationship(back_populates="users")


class Customer(TimestampAuditSoftDeleteMixin, Base):
    """Local customer reference cache — not Customer Master SoR (ADR-002)."""

    __tablename__ = "customers"
    __table_args__ = (
        UniqueConstraint("external_customer_id", name="uq_customers_external_customer_id"),
        Index("ix_customers_email", "email"),
        Index("ix_customers_phone", "phone"),
    )

    external_customer_id: Mapped[str] = mapped_column(String(64), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    complaints: Mapped[list[Complaint]] = relationship(back_populates="customer")


class Complaint(TimestampAuditSoftDeleteMixin, Base):
    __tablename__ = "complaints"
    __table_args__ = (
        UniqueConstraint("complaint_number", name="uq_complaints_complaint_number"),
        Index("ix_complaints_customer_id", "customer_id"),
        Index("ix_complaints_branch_id", "branch_id"),
        Index("ix_complaints_status", "status"),
        Index("ix_complaints_priority", "priority"),
        Index("ix_complaints_reported_at", "reported_at"),
        Index("ix_complaints_status_priority", "status", "priority"),
    )

    complaint_number: Mapped[str] = mapped_column(String(32), nullable=False)
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
    )
    branch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("branches.id", ondelete="SET NULL"),
        nullable=True,
    )
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    priority: Mapped[str] = mapped_column(String(16), nullable=False)
    channel: Mapped[str | None] = mapped_column(String(32), nullable=True)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    customer: Mapped[Customer] = relationship(back_populates="complaints")
    branch: Mapped[Branch | None] = relationship(back_populates="complaints")
    assignments: Mapped[list[ComplaintAssignment]] = relationship(
        back_populates="complaint"
    )
    escalations: Mapped[list[ComplaintEscalation]] = relationship(
        back_populates="complaint"
    )
    resolutions: Mapped[list[ComplaintResolution]] = relationship(
        back_populates="complaint"
    )
    timelines: Mapped[list[ComplaintTimeline]] = relationship(back_populates="complaint")
    attachments: Mapped[list[Attachment]] = relationship(back_populates="complaint")


class ComplaintResolution(TimestampAuditSoftDeleteMixin, Base):
    """Resolution record required before CLOSED (TASK-010). One current row per complaint."""

    __tablename__ = "complaint_resolutions"
    __table_args__ = (
        Index("ix_complaint_resolutions_complaint_id", "complaint_id"),
        Index("ix_complaint_resolutions_resolved_by", "resolved_by"),
        Index("ix_complaint_resolutions_resolved_at", "resolved_at"),
        Index(
            "ix_complaint_resolutions_complaint_current",
            "complaint_id",
            "is_current",
        ),
    )

    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("complaints.id", ondelete="CASCADE"),
        nullable=False,
    )
    resolution_category: Mapped[str] = mapped_column(String(32), nullable=False)
    root_cause: Mapped[str] = mapped_column(String(500), nullable=False)
    resolution_notes: Mapped[str] = mapped_column(Text, nullable=False)
    resolved_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    resolved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_current: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=true()
    )

    complaint: Mapped[Complaint] = relationship(back_populates="resolutions")
    resolver: Mapped[User] = relationship(foreign_keys=[resolved_by])


class ComplaintAssignment(TimestampAuditSoftDeleteMixin, Base):
    __tablename__ = "complaint_assignments"
    __table_args__ = (
        Index("ix_complaint_assignments_complaint_id", "complaint_id"),
        Index("ix_complaint_assignments_assignee_id", "assignee_id"),
        Index("ix_complaint_assignments_assigned_by", "assigned_by"),
        Index(
            "ix_complaint_assignments_complaint_current",
            "complaint_id",
            "is_current",
        ),
    )

    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("complaints.id", ondelete="CASCADE"),
        nullable=False,
    )
    assignee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    assigned_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    unassigned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_current: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=true()
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    complaint: Mapped[Complaint] = relationship(back_populates="assignments")
    assignee: Mapped[User] = relationship(foreign_keys=[assignee_id])
    assigner: Mapped[User | None] = relationship(foreign_keys=[assigned_by])


class ComplaintEscalation(TimestampAuditSoftDeleteMixin, Base):
    """Escalation history + Escalation Request (TASK-011 Branch → HO)."""

    __tablename__ = "complaint_escalations"
    __table_args__ = (
        Index("ix_complaint_escalations_complaint_id", "complaint_id"),
        Index("ix_complaint_escalations_escalated_to_user_id", "escalated_to_user_id"),
        Index("ix_complaint_escalations_escalated_to_role_id", "escalated_to_role_id"),
        Index("ix_complaint_escalations_status", "status"),
        Index("ix_complaint_escalations_level", "level"),
        Index("ix_complaint_escalations_requested_by", "requested_by"),
        Index("ix_complaint_escalations_requested_at", "requested_at"),
        Index("ix_complaint_escalations_reason_code", "reason_code"),
        Index("ix_complaint_escalations_reviewed_by", "reviewed_by"),
        Index("ix_complaint_escalations_reviewed_at", "reviewed_at"),
    )

    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("complaints.id", ondelete="CASCADE"),
        nullable=False,
    )
    escalated_from_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    escalated_to_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    escalated_to_role_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="SET NULL"),
        nullable=True,
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    escalated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # TASK-011 Escalation Request fields (API-301 / API-302)
    reason_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reason_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    diagnosis: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    requested_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    requested_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # TASK-012 Escalation Review fields (API-303 / API-304)
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    complaint: Mapped[Complaint] = relationship(back_populates="escalations")
    escalated_from_user: Mapped[User | None] = relationship(
        foreign_keys=[escalated_from_user_id]
    )
    escalated_to_user: Mapped[User | None] = relationship(
        foreign_keys=[escalated_to_user_id]
    )
    escalated_to_role: Mapped[Role | None] = relationship(
        foreign_keys=[escalated_to_role_id]
    )
    requester: Mapped[User | None] = relationship(foreign_keys=[requested_by])
    reviewer: Mapped[User | None] = relationship(foreign_keys=[reviewed_by])


class ComplaintTimeline(TimestampAuditSoftDeleteMixin, Base):
    __tablename__ = "complaint_timelines"
    __table_args__ = (
        Index("ix_complaint_timelines_complaint_id", "complaint_id"),
        Index("ix_complaint_timelines_event_at", "event_at"),
        Index("ix_complaint_timelines_event_type", "event_type"),
        Index(
            "ix_complaint_timelines_complaint_event_at",
            "complaint_id",
            "event_at",
        ),
    )

    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("complaints.id", ondelete="CASCADE"),
        nullable=False,
    )
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    event_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    from_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    to_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
    )

    complaint: Mapped[Complaint] = relationship(back_populates="timelines")
    actor: Mapped[User | None] = relationship(foreign_keys=[actor_user_id])


class Attachment(TimestampAuditSoftDeleteMixin, Base):
    __tablename__ = "attachments"
    __table_args__ = (
        Index("ix_attachments_complaint_id", "complaint_id"),
        Index("ix_attachments_uploaded_by", "uploaded_by"),
        Index("ix_attachments_storage_key", "storage_key"),
    )

    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("complaints.id", ondelete="CASCADE"),
        nullable=False,
    )
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    content_type: Mapped[str] = mapped_column(String(128), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)

    complaint: Mapped[Complaint] = relationship(back_populates="attachments")
    uploader: Mapped[User | None] = relationship(foreign_keys=[uploaded_by])


class AuditLog(Base):
    """Append-only audit trail (BR-CP-03). No update/delete path in application code."""

    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_action", "action"),
        Index("ix_audit_logs_entity", "entity_type", "entity_id"),
        Index("ix_audit_logs_occurred_at", "occurred_at"),
        Index("ix_audit_logs_actor_user_id", "actor_user_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    old_value: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    new_value: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class RefreshToken(Base):
    """Rotating refresh token session (hashed at rest; revoke on logout/rotation)."""

    __tablename__ = "refresh_tokens"
    __table_args__ = (
        UniqueConstraint("token_hash", name="uq_refresh_tokens_token_hash"),
        Index("ix_refresh_tokens_user_id", "user_id"),
        Index("ix_refresh_tokens_expires_at", "expires_at"),
        Index("ix_refresh_tokens_user_active", "user_id", "revoked_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    replaced_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("refresh_tokens.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    user: Mapped[User] = relationship(foreign_keys=[user_id])


__all__ = [
    "Attachment",
    "AuditLog",
    "Branch",
    "Complaint",
    "ComplaintAssignment",
    "ComplaintEscalation",
    "ComplaintResolution",
    "ComplaintTimeline",
    "Customer",
    "RefreshToken",
    "Role",
    "User",
]
