"""Bidirectional Complaint domain ↔ ORM mapping (CAPABILITY-004 / 005)."""

from __future__ import annotations

from app.modules.complaint.domain.models import (
    Complaint,
    ComplaintPriority,
    ComplaintStatus,
    Resolution,
)
from app.modules.complaint.infrastructure.orm.models import ComplaintORM


class ComplaintMapper:
    """Map Complaint domain ↔ ComplaintORM."""

    @staticmethod
    def to_domain(row: ComplaintORM) -> Complaint:
        resolution: Resolution | None = None
        if (
            row.resolution_summary is not None
            and row.resolution_resolved_by is not None
            and row.resolution_resolved_at is not None
        ):
            resolution = Resolution(
                summary=row.resolution_summary,
                resolved_by=row.resolution_resolved_by,
                resolved_at=row.resolution_resolved_at,
            )
        return Complaint(
            complaint_id=row.complaint_id,
            organization_id=row.organization_id,
            branch_id=row.branch_id,
            queue_ticket_id=row.queue_ticket_id,
            category=row.category,
            title=row.title,
            description=row.description,
            priority=ComplaintPriority(row.priority),
            status=ComplaintStatus(row.status),
            created_at=row.created_at,
            updated_at=row.updated_at,
            resolution=resolution,
        )

    @staticmethod
    def to_orm(domain: Complaint) -> ComplaintORM:
        resolution = domain.resolution
        return ComplaintORM(
            complaint_id=domain.complaint_id,
            organization_id=domain.organization_id,
            branch_id=domain.branch_id,
            queue_ticket_id=domain.queue_ticket_id,
            category=domain.category,
            title=domain.title,
            description=domain.description,
            priority=domain.priority.value,
            status=domain.status.value,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
            resolution_summary=None if resolution is None else resolution.summary,
            resolution_resolved_by=(
                None if resolution is None else resolution.resolved_by
            ),
            resolution_resolved_at=(
                None if resolution is None else resolution.resolved_at
            ),
        )

    @staticmethod
    def apply_to_orm(domain: Complaint, row: ComplaintORM) -> ComplaintORM:
        """Copy domain fields onto an existing ORM row (no identity change)."""
        resolution = domain.resolution
        row.organization_id = domain.organization_id
        row.branch_id = domain.branch_id
        row.queue_ticket_id = domain.queue_ticket_id
        row.category = domain.category
        row.title = domain.title
        row.description = domain.description
        row.priority = domain.priority.value
        row.status = domain.status.value
        row.created_at = domain.created_at
        row.updated_at = domain.updated_at
        row.resolution_summary = None if resolution is None else resolution.summary
        row.resolution_resolved_by = (
            None if resolution is None else resolution.resolved_by
        )
        row.resolution_resolved_at = (
            None if resolution is None else resolution.resolved_at
        )
        return row


__all__ = ["ComplaintMapper"]
