"""NotificationDeliveryFactory — build delivery plans from Intent (TASK-049).

No transport. No sending. No queue.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import MappingProxyType
from typing import Any, Mapping

from app.modules.notification.delivery_models import (
    NotificationDelivery,
    NotificationDeliveryStatus,
)
from app.modules.notification.intent_models import (
    NotificationIntent,
    NotificationIntentChannel,
)


def _metadata_for(
    intent: NotificationIntent,
    channel: NotificationIntentChannel,
) -> Mapping[str, Any]:
    base = dict(intent.metadata)
    base.update(
        {
            "intentId": str(intent.intent_id),
            "notificationId": str(intent.notification_id),
            "channel": channel.value,
            "preferredChannels": [c.value for c in intent.preferred_channels],
        }
    )
    return MappingProxyType(base)


class NotificationDeliveryFactory:
    """Creates immutable NotificationDelivery plans from NotificationIntent."""

    @classmethod
    def from_intent(
        cls,
        intent: NotificationIntent,
        *,
        created_at: datetime | None = None,
    ) -> tuple[NotificationDelivery, ...]:
        """Expand preferred channels into one PLANNED delivery per channel.

        Returns an empty tuple only when the intent has no preferred channels
        (should not occur for factory-built intents).
        """
        created = created_at or datetime.now(UTC)
        if created.tzinfo is None:
            created = created.replace(tzinfo=UTC)

        channels = intent.preferred_channels
        if not channels:
            channels = (NotificationIntentChannel.EMAIL,)

        return tuple(
            NotificationDelivery(
                delivery_id=uuid.uuid4(),
                created_at=created,
                intent_id=intent.intent_id,
                channel=channel,
                recipient_key=intent.recipient_key,
                priority=intent.priority,
                template_key=intent.template_key,
                variables=MappingProxyType(dict(intent.variables)),
                status=NotificationDeliveryStatus.PLANNED,
                metadata=_metadata_for(intent, channel),
            )
            for channel in channels
        )
