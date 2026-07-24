"""NotificationDelivery — planned delivery action (TASK-049).

Represents one executable delivery plan. Not transport, not sending, not a queue.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping

from app.modules.notification.intent_models import (
    NotificationIntentChannel,
    NotificationIntentPriority,
)


class NotificationDeliveryStatus(StrEnum):
    """Delivery plan lifecycle for TASK-049 (planned only)."""

    PLANNED = "PLANNED"


@dataclass(frozen=True, slots=True)
class NotificationDelivery:
    """Immutable planned delivery derived from a NotificationIntent.

    Exists only in memory for this foundation. Not sent, not queued.
    """

    delivery_id: uuid.UUID
    created_at: datetime
    intent_id: uuid.UUID
    channel: NotificationIntentChannel
    recipient_key: str
    priority: NotificationIntentPriority
    template_key: str
    variables: Mapping[str, Any]
    status: NotificationDeliveryStatus
    metadata: Mapping[str, Any]

    def as_dict(self) -> Mapping[str, object]:
        """Diagnostic serialization (not an API / transport contract)."""
        return MappingProxyType(
            {
                "deliveryId": str(self.delivery_id),
                "createdAt": self.created_at.isoformat(),
                "intentId": str(self.intent_id),
                "channel": self.channel.value,
                "recipientKey": self.recipient_key,
                "priority": self.priority.value,
                "templateKey": self.template_key,
                "variables": dict(self.variables),
                "status": self.status.value,
                "metadata": dict(self.metadata),
            }
        )
