"""Bidirectional SLAPolicy / ComplaintSLA domain ↔ ORM mapping (CAPABILITY-008)."""

from __future__ import annotations

from app.modules.complaint.domain.models import ComplaintSLA, SLAPolicy
from app.modules.complaint.infrastructure.orm.models import (
    ComplaintSlaORM,
    SLAPolicyORM,
)


class SLAPolicyMapper:
    """Map SLAPolicy domain ↔ SLAPolicyORM."""

    @staticmethod
    def to_domain(row: SLAPolicyORM) -> SLAPolicy:
        return SLAPolicy(
            policy_id=row.policy_id,
            name=row.name,
            target_minutes=row.target_minutes,
            is_default=row.is_default,
            description=row.description,
        )

    @staticmethod
    def to_orm(domain: SLAPolicy) -> SLAPolicyORM:
        return SLAPolicyORM(
            policy_id=domain.policy_id,
            name=domain.name,
            target_minutes=domain.target_minutes,
            is_default=domain.is_default,
            description=domain.description,
        )


class ComplaintSlaMapper:
    """Map ComplaintSLA domain ↔ ComplaintSlaORM."""

    @staticmethod
    def to_domain(row: ComplaintSlaORM) -> ComplaintSLA:
        return ComplaintSLA(
            sla_id=row.sla_id,
            complaint_id=row.complaint_id,
            policy_id=row.policy_id,
            started_at=row.started_at,
            due_at=row.due_at,
            completed_at=row.completed_at,
            breached_at=row.breached_at,
            is_active=row.is_active,
            is_breached=row.is_breached,
        )

    @staticmethod
    def to_orm(domain: ComplaintSLA) -> ComplaintSlaORM:
        return ComplaintSlaORM(
            sla_id=domain.sla_id,
            complaint_id=domain.complaint_id,
            policy_id=domain.policy_id,
            started_at=domain.started_at,
            due_at=domain.due_at,
            completed_at=domain.completed_at,
            breached_at=domain.breached_at,
            is_active=domain.is_active,
            is_breached=domain.is_breached,
        )

    @staticmethod
    def apply_to_orm(domain: ComplaintSLA, row: ComplaintSlaORM) -> ComplaintSlaORM:
        """Copy mutable SLA fields onto an existing ORM row."""
        row.due_at = domain.due_at
        row.completed_at = domain.completed_at
        row.breached_at = domain.breached_at
        row.is_active = domain.is_active
        row.is_breached = domain.is_breached
        return row


__all__ = ["ComplaintSlaMapper", "SLAPolicyMapper"]
