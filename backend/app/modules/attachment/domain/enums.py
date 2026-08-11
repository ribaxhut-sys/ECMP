"""CAPABILITY-011 Attachment domain enums (extensible string enums)."""

from __future__ import annotations

from enum import StrEnum


class AggregateType(StrEnum):
    """Aggregate that owns attachments (future-safe)."""

    COMPLAINT = "Complaint"
    QUEUE = "Queue"
    NOTIFICATION = "Notification"
    ANNOUNCEMENT = "Announcement"
    KNOWLEDGE = "Knowledge"


class AttachmentStatus(StrEnum):
    """Attachment lifecycle — logical delete via DELETED."""

    UPLOADED = "UPLOADED"
    AVAILABLE = "AVAILABLE"
    DELETED = "DELETED"
    FAILED = "FAILED"
