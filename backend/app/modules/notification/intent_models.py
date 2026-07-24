"""NotificationIntent — delivery intent value objects (TASK-048).

Describes WHAT should be delivered. Transport adapters (future) decide HOW.
No sending, no persistence, no queue.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping


class NotificationIntentChannel(StrEnum):
    """Preferred delivery channels for an intent (enum only — no adapters)."""

    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"
    PUSH = "PUSH"
    SMS = "SMS"
    WEBSOCKET = "WEBSOCKET"


class NotificationIntentPriority(StrEnum):
    """Intent priority — mirrors NotificationSeverity values."""

    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True, slots=True)
class NotificationIntent:
    """Immutable delivery intent derived from a Notification.

    Exists only in memory for this foundation. Not sent, not queued.
    """

    intent_id: uuid.UUID
    created_at: datetime
    notification_id: uuid.UUID
    recipient_key: str
    preferred_channels: tuple[NotificationIntentChannel, ...]
    priority: NotificationIntentPriority
    template_key: str
    variables: Mapping[str, Any]
    metadata: Mapping[str, Any]

    def as_dict(self) -> Mapping[str, object]:
        """Diagnostic serialization (not an API / transport contract)."""
        return MappingProxyType(
            {
                "intentId": str(self.intent_id),
                "createdAt": self.created_at.isoformat(),
                "notificationId": str(self.notification_id),
                "recipientKey": self.recipient_key,
                "preferredChannels": [c.value for c in self.preferred_channels],
                "priority": self.priority.value,
                "templateKey": self.template_key,
                "variables": dict(self.variables),
                "metadata": dict(self.metadata),
            }
        )
