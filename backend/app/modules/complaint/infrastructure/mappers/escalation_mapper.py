"""Bidirectional Escalation domain ↔ ORM mapping (CAPABILITY-007)."""

from __future__ import annotations

from app.modules.complaint.domain.models import Escalation, EscalationLevel
from app.modules.complaint.infrastructure.orm.models import EscalationORM


class EscalationMapper:
    """Map Escalation domain ↔ EscalationORM."""

    @staticmethod
    def to_domain(row: EscalationORM) -> Escalation:
        return Escalation(
            escalation_id=row.escalation_id,
            complaint_id=row.complaint_id,
            level=EscalationLevel(row.level),
            reason=row.reason,
            escalated_by=row.escalated_by,
            escalated_at=row.escalated_at,
            released_at=row.released_at,
            is_current=row.is_current,
        )

    @staticmethod
    def to_orm(domain: Escalation) -> EscalationORM:
        return EscalationORM(
            escalation_id=domain.escalation_id,
            complaint_id=domain.complaint_id,
            level=domain.level.value,
            reason=domain.reason,
            escalated_by=domain.escalated_by,
            escalated_at=domain.escalated_at,
            released_at=domain.released_at,
            is_current=domain.is_current,
        )

    @staticmethod
    def apply_to_orm(domain: Escalation, row: EscalationORM) -> EscalationORM:
        """Copy domain fields onto an existing ORM row (no identity change).

        Used for release (is_current / released_at). Level, reason, escalated_by,
        and escalated_at are not rewritten (append-only history).
        """
        row.level = domain.level.value
        row.reason = domain.reason
        row.escalated_by = domain.escalated_by
        row.escalated_at = domain.escalated_at
        row.released_at = domain.released_at
        row.is_current = domain.is_current
        return row


__all__ = ["EscalationMapper"]
