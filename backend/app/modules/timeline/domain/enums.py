"""CAPABILITY-010 Timeline domain enums (extensible string enums)."""

from __future__ import annotations

from enum import StrEnum


class AggregateType(StrEnum):
    """Aggregate owning a timeline stream (future-safe)."""

    COMPLAINT = "Complaint"
    QUEUE = "Queue"
    NOTIFICATION = "Notification"


class TimelineEventType(StrEnum):
    """Known timeline event types — store as VARCHAR; new values allowed."""

    COMPLAINT_CREATED = "ComplaintCreated"
    COMPLAINT_ASSIGNED = "ComplaintAssigned"
    COMPLAINT_ESCALATED = "ComplaintEscalated"
    COMPLAINT_RESOLVED = "ComplaintResolved"
    COMPLAINT_CLOSED = "ComplaintClosed"
    COMPLAINT_CANCELLED = "ComplaintCancelled"
    COMPLAINT_ACCEPTED = "ComplaintAccepted"
    COMPLAINT_IN_PROGRESS = "ComplaintInProgress"
    SLA_STARTED = "SLAStarted"
    SLA_BREACHED = "SLABreached"
    NOTIFICATION_CREATED = "NotificationCreated"
    NOTIFICATION_SENT = "NotificationSent"
    NOTIFICATION_FAILED = "NotificationFailed"


class ActorType(StrEnum):
    """Who produced the activity."""

    USER = "USER"
    SYSTEM = "SYSTEM"
    SERVICE = "SERVICE"
