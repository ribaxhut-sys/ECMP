"""Immutable in-memory Notification domain object (TASK-047).

Transport-independent. No email / WhatsApp / SMS / Push / WebSocket.
Not persisted — diagnostics/testing only.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping


class NotificationSeverity(StrEnum):
    """Relative urgency for a built notification (not a delivery channel)."""

    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class NotificationType(StrEnum):
    """Notification kinds derived from Complaint lifecycle events."""

    COMPLAINT_CREATED = "ComplaintCreated"
    COMPLAINT_ASSIGNED = "ComplaintAssigned"
    COMPLAINT_ACCEPTED = "ComplaintAccepted"
    COMPLAINT_IN_PROGRESS = "ComplaintInProgress"
    COMPLAINT_RESOLVED = "ComplaintResolved"
    COMPLAINT_CLOSED = "ComplaintClosed"
    COMPLAINT_ESCALATED = "ComplaintEscalated"


@dataclass(frozen=True, slots=True)
class Notification:
    """Immutable notification built from a domain event.

    Exists only in memory for this foundation. Not delivered, not stored.
    """

    notification_id: uuid.UUID
    notification_type: NotificationType
    created_at: datetime
    recipient: str
    title: str
    message: str
    severity: NotificationSeverity
    source_event: uuid.UUID
    payload: Mapping[str, Any]

    def as_dict(self) -> Mapping[str, object]:
        """Diagnostic serialization (not an API / delivery contract)."""
        return MappingProxyType(
            {
                "notificationId": str(self.notification_id),
                "notificationType": self.notification_type.value,
                "createdAt": self.created_at.isoformat(),
                "recipient": self.recipient,
                "title": self.title,
                "message": self.message,
                "severity": self.severity.value,
                "sourceEvent": str(self.source_event),
                "payload": dict(self.payload),
            }
        )
