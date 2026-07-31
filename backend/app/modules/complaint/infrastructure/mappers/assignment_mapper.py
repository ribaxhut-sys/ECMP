"""Bidirectional Assignment domain ↔ ORM mapping (CAPABILITY-006)."""

from __future__ import annotationsfrom app.modules.complaint.domain.models import AssigneeType, Assignmentfrom app.modules.complaint.infrastructure.orm.models import AssignmentORMclass AssignmentMapper:
    """Map Assignment domain ↔ AssignmentORM."""

    @staticmethod
    def to_domain(row: AssignmentORM) -> Assignment:
        return Assignment(
            assignment_id=row.assignment_id,
            complaint_id=row.complaint_id,
            assignee_type=AssigneeType(row.assignee_type),
            assignee_id=row.assignee_id,
            assigned_at=row.assigned_at,
            assigned_by=row.assigned_by,
            released_at=row.released_at,
            release_reason=row.release_reason,
            is_active=row.is_active,
        )

    @staticmethod
    def to_orm(domain: Assignment) -> AssignmentORM:
        return AssignmentORM(
            assignment_id=domain.assignment_id,
            complaint_id=domain.complaint_id,
            assignee_type=domain.assignee_type.value,
            assignee_id=domain.assignee_id,
            assigned_at=domain.assigned_at,
            assigned_by=domain.assigned_by,
            released_at=domain.released_at,
            release_reason=domain.release_reason,
            is_active=domain.is_active,
        )

    @staticmethod
    def apply_to_orm(domain: Assignment, row: AssignmentORM) -> AssignmentORM:
        """Copy domain fields onto an existing ORM row (no identity change).

        Used for release (is_active / released_at / release_reason). Assignee
        identity and assigned_at are not rewritten (append-only history).
        """
        row.assignee_type = domain.assignee_type.value
        row.assignee_id = domain.assignee_id
        row.assigned_at = domain.assigned_at
        row.assigned_by = domain.assigned_by
        row.released_at = domain.released_at
        row.release_reason = domain.release_reason
        row.is_active = domain.is_active
        return row


__all__ = ["AssignmentMapper"]
