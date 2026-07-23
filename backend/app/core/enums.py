"""Global domain enums — single source of truth for complaint lifecycle."""

from __future__ import annotations

from enum import StrEnum


class ComplaintStatus(StrEnum):
    """Valid complaint lifecycle statuses (v1)."""

    NEW = "NEW"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    PENDING = "PENDING"
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
    ESCALATION_REQUESTED = "complaint.escalation_requested"
    RESOLVED = "complaint.resolved"
    CLOSED = "complaint.closed"


class EscalationRequestStatus(StrEnum):
    """Escalation Request lifecycle (TASK-011 — request only; no review yet)."""

    REQUESTED = "REQUESTED"


class EscalationReasonCode(StrEnum):
    """Minimum reason codes for Branch → HO Escalation Request."""

    SPECIALIST_REQUIRED = "SPECIALIST_REQUIRED"
    COMPLEX_CASE = "COMPLEX_CASE"
    POLICY_EXCEPTION = "POLICY_EXCEPTION"
    CUSTOMER_REQUEST = "CUSTOMER_REQUEST"
    OTHER = "OTHER"
