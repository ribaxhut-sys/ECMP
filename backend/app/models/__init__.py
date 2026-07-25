"""ORM models for ECMP v1.0 foundation schema."""

from __future__ import annotations

import uuid
from datetime import date, datetime, time
from typing import Any

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Time,
    UniqueConstraint,
    func,
    false,
    text,
    true,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampAuditSoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.modules.attachment.models import Attachment
from app.modules.iam.data_scope.models import DataScope
from app.modules.iam.permission.models import Permission
from app.modules.iam.role.models import Role
from app.modules.iam.role_permission.models import RolePermission
from app.modules.iam.user_role.models import UserRole
from app.modules.notification.models import NotificationQueue, NotificationTemplate
from app.modules.settings.models import Setting
from app.modules.timeline.models import TimelineEntryORM


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
        Index("ix_complaints_source_type", "source_type"),
        Index("ix_complaints_source_id", "source_id"),
        Index("ix_complaints_target_type", "target_type"),
        Index("ix_complaints_target_id", "target_id"),
        Index("ix_complaints_status", "status"),
        Index("ix_complaints_priority", "priority"),
        Index("ix_complaints_reported_at", "reported_at"),
        Index("ix_complaints_status_priority", "status", "priority"),
    )

    complaint_number: Mapped[str] = mapped_column(String(32), nullable=False)
    # Nullable when source_type is not CUSTOMER (TASK-042 / DEC-018).
    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=True,
    )
    branch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("branches.id", ondelete="SET NULL"),
        nullable=True,
    )
    # Polymorphic origin / destination (no typed FK — entity depends on *_type).
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    target_type: Mapped[str] = mapped_column(String(32), nullable=False)
    target_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
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
    closed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    closure_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    customer: Mapped[Customer | None] = relationship(back_populates="complaints")
    closer: Mapped[User | None] = relationship(foreign_keys=[closed_by])
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
    sla: Mapped[SlaRecord | None] = relationship(
        back_populates="complaint", uselist=False
    )


class SlaRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """SLA deadline store for a complaint (TASK-021 foundation).

    One row per complaint. Deadlines only — no timers or calculations.
    Complaint hard-delete is RESTRICTed while this row exists.
    """

    __tablename__ = "sla_records"
    __table_args__ = (
        UniqueConstraint("complaint_id", name="uq_sla_records_complaint_id"),
        Index("ix_sla_records_complaint_id", "complaint_id"),
        Index("ix_sla_records_overall_status", "overall_status"),
        Index("ix_sla_records_overall_due_at", "overall_due_at"),
    )

    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("complaints.id", ondelete="RESTRICT"),
        nullable=False,
    )
    assignment_due_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resolution_due_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    appointment_due_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    escalation_due_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    overall_due_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    assignment_status: Mapped[str] = mapped_column(String(32), nullable=False)
    resolution_status: Mapped[str] = mapped_column(String(32), nullable=False)
    appointment_status: Mapped[str] = mapped_column(String(32), nullable=False)
    escalation_status: Mapped[str] = mapped_column(String(32), nullable=False)
    overall_status: Mapped[str] = mapped_column(String(32), nullable=False)

    complaint: Mapped[Complaint] = relationship(back_populates="sla")


class SlaPolicy(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Configurable SLA target durations (TASK-022). Policy only — no calculations.

    Multiple policies may exist; at most one may be active. Policy changes
    affect future complaints only (no recalculation of existing SLA rows).
    """

    __tablename__ = "sla_policies"
    __table_args__ = (
        Index("ix_sla_policies_is_active", "is_active"),
        Index("ix_sla_policies_name", "name"),
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    assignment_target_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    appointment_target_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    resolution_target_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    escalation_target_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    overall_target_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=true()
    )


class ComplaintResolution(TimestampAuditSoftDeleteMixin, Base):
    """Resolution record required before CLOSED (TASK-010). One current row per complaint.

    Final Resolution fields (TASK-018 / DEC-011) are nullable until submitted;
    they do not close the complaint or escalation.
    """

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
        Index("ix_complaint_resolutions_final_resolution_at", "final_resolution_at"),
        Index("ix_complaint_resolutions_final_resolution_by", "final_resolution_by"),
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
    final_resolution_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    final_resolution_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    )
    final_resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    final_resolution_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    follow_up_required: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )

    complaint: Mapped[Complaint] = relationship(back_populates="resolutions")
    resolver: Mapped[User] = relationship(foreign_keys=[resolved_by])
    final_resolver: Mapped[User | None] = relationship(
        foreign_keys=[final_resolution_by]
    )


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
        Index("ix_complaint_escalations_closed_by", "closed_by"),
        Index("ix_complaint_escalations_closed_at", "closed_at"),
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
    # TASK-020 Escalation Closure fields (API-313)
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    closed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    closure_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

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
    closer: Mapped[User | None] = relationship(foreign_keys=[closed_by])
    appointments: Mapped[list[Appointment]] = relationship(
        back_populates="escalation"
    )


class Appointment(TimestampAuditSoftDeleteMixin, Base):
    """Head Office appointment booked against an APPROVED escalation (TASK-014)."""

    __tablename__ = "appointments"
    __table_args__ = (
        Index("ix_appointments_escalation_id", "escalation_id"),
        Index("ix_appointments_assigned_engineer_id", "assigned_engineer_id"),
        Index("ix_appointments_appointment_date", "appointment_date"),
        Index("ix_appointments_status", "status"),
        Index(
            "ix_appointments_engineer_date",
            "assigned_engineer_id",
            "appointment_date",
        ),
    )

    escalation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("complaint_escalations.id", ondelete="CASCADE"),
        nullable=False,
    )
    appointment_date: Mapped[date] = mapped_column(Date, nullable=False)
    appointment_start_time: Mapped[time] = mapped_column(Time, nullable=False)
    appointment_end_time: Mapped[time] = mapped_column(Time, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    assigned_engineer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # TASK-015 Customer Check-In
    checked_in_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    checked_in_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    checkin_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # TASK-016 Appointment Completion
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    completion_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    completion_result: Mapped[str] = mapped_column(
        String(50), nullable=False, default="COMPLETED", server_default="COMPLETED"
    )
    # TASK-017 Customer No Show
    no_show_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    no_show_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    no_show_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    escalation: Mapped[ComplaintEscalation] = relationship(
        back_populates="appointments"
    )
    assigned_engineer: Mapped[User] = relationship(
        foreign_keys=[assigned_engineer_id]
    )


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


class AuditLog(Base):
    """Legacy append-only audit trail for Complaint/Auth/Resolution writers.

    Physical table renamed to ``audit_logs_legacy`` in TASK-031 so the
    platform ``audit_logs`` table can use the new schema. Writer call sites
    are unchanged.
    """

    __tablename__ = "audit_logs_legacy"
    __table_args__ = (
        Index("ix_audit_logs_legacy_action", "action"),
        Index("ix_audit_logs_legacy_entity", "entity_type", "entity_id"),
        Index("ix_audit_logs_legacy_occurred_at", "occurred_at"),
        Index("ix_audit_logs_legacy_actor_user_id", "actor_user_id"),
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
    "Appointment",
    "Attachment",
    "AuditLog",
    "Branch",
    "Complaint",
    "ComplaintAssignment",
    "ComplaintEscalation",
    "ComplaintResolution",
    "ComplaintTimeline",
    "Customer",
    "DataScope",
    "NotificationQueue",
    "NotificationTemplate",
    "Permission",
    "RefreshToken",
    "Role",
    "RolePermission",
    "Setting",
    "SlaPolicy",
    "SlaRecord",
    "TimelineEntryORM",
    "User",
    "UserRole",
]
