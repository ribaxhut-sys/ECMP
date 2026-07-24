"""Complaint ORM models — separate from domain models (CAPABILITY-004…008).

Never expose outside infrastructure / repositories / mappers.
No FK to Queue tables — ``queue_ticket_id`` is a cross-BC reference only.
Assignment / Escalation / SLA tables are ``complaint_case_*`` (CA BC); legacy
ECMF keeps ``complaint_assignments`` / ``complaint_escalations`` / ``sla_*``
on ``complaints``.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ComplaintORM(Base):
    """Persistence row for Complaint aggregate root."""

    __tablename__ = "complaint_cases"
    __table_args__ = (
        Index("ix_complaint_cases_organization_id", "organization_id"),
        Index("ix_complaint_cases_branch_id", "branch_id"),
        Index("ix_complaint_cases_queue_ticket_id", "queue_ticket_id"),
        Index("ix_complaint_cases_status", "status"),
        Index("ix_complaint_cases_priority", "priority"),
        Index(
            "ix_complaint_cases_org_status",
            "organization_id",
            "status",
        ),
    )

    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    branch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    queue_ticket_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    # CAPABILITY-005 — nullable for backward-compatible resolution snapshot
    resolution_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolution_resolved_by: Mapped[str | None] = mapped_column(
        String(200), nullable=True
    )
    resolution_resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class AssignmentORM(Base):
    """Persistence row for Assignment child entity (append-only history)."""

    __tablename__ = "complaint_case_assignments"
    __table_args__ = (
        Index("ix_complaint_case_assignments_complaint_id", "complaint_id"),
        Index(
            "ix_complaint_case_assignments_complaint_active",
            "complaint_id",
            unique=True,
            postgresql_where=text("is_active = true"),
        ),
        Index("ix_complaint_case_assignments_assignee", "assignee_type", "assignee_id"),
    )

    assignment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("complaint_cases.complaint_id", ondelete="CASCADE"),
        nullable=False,
    )
    assignee_type: Mapped[str] = mapped_column(String(32), nullable=False)
    assignee_id: Mapped[str] = mapped_column(String(200), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    assigned_by: Mapped[str] = mapped_column(String(200), nullable=False)
    released_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    release_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class EscalationORM(Base):
    """Persistence row for Escalation child entity (append-only history)."""

    __tablename__ = "complaint_case_escalations"
    __table_args__ = (
        Index("ix_complaint_case_escalations_complaint_id", "complaint_id"),
        Index(
            "ix_complaint_case_escalations_complaint_current",
            "complaint_id",
            unique=True,
            postgresql_where=text("is_current = true"),
        ),
        Index("ix_complaint_case_escalations_level", "level"),
    )

    escalation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("complaint_cases.complaint_id", ondelete="CASCADE"),
        nullable=False,
    )
    level: Mapped[str] = mapped_column(String(32), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    escalated_by: Mapped[str] = mapped_column(String(200), nullable=False)
    escalated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    released_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class SLAPolicyORM(Base):
    """Persistence row for CA Complaint SLAPolicy (CAPABILITY-008).

    Table ``complaint_sla_policies`` — distinct from legacy ECMF ``sla_policies``.
    """

    __tablename__ = "complaint_sla_policies"
    __table_args__ = (
        Index("ix_complaint_sla_policies_name", "name"),
        Index(
            "ix_complaint_sla_policies_default",
            "is_default",
            unique=True,
            postgresql_where=text("is_default = true"),
        ),
    )

    policy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    target_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class ComplaintSlaORM(Base):
    """Persistence row for ComplaintSLA child entity (CAPABILITY-008)."""

    __tablename__ = "complaint_case_slas"
    __table_args__ = (
        Index("ix_complaint_case_slas_complaint_id", "complaint_id"),
        Index(
            "ix_complaint_case_slas_complaint_active",
            "complaint_id",
            unique=True,
            postgresql_where=text("is_active = true"),
        ),
        Index("ix_complaint_case_slas_policy_id", "policy_id"),
    )

    sla_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("complaint_cases.complaint_id", ondelete="CASCADE"),
        nullable=False,
    )
    policy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("complaint_sla_policies.policy_id", ondelete="RESTRICT"),
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    due_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    breached_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_breached: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


__all__ = [
    "AssignmentORM",
    "ComplaintORM",
    "ComplaintSlaORM",
    "EscalationORM",
    "SLAPolicyORM",
]
