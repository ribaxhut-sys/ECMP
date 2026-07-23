"""Global domain enums — single source of truth for complaint lifecycle."""

from __future__ import annotations

from enum import StrEnum


class ComplaintStatus(StrEnum):
    """Valid complaint lifecycle statuses (v1)."""

    NEW = "NEW"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


INITIAL_COMPLAINT_STATUS = ComplaintStatus.NEW


class TimelineEvent(StrEnum):
    """Allowed complaint timeline event names."""

    CREATED = "complaint.created"
    UPDATED = "complaint.updated"
    ASSIGNED = "complaint.assigned"
    REASSIGNED = "complaint.reassigned"
    ESCALATED = "complaint.escalated"
    RESOLVED = "complaint.resolved"
    CLOSED = "complaint.closed"
