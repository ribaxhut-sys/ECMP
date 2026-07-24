"""NotificationEventHandler — EventDispatcher consumer (TASK-047/048/049).

Builds Notification → Intent → Delivery plans. Does not send via any channel.
"""

from __future__ import annotations

from typing import Any

from app.core.logging import get_logger
from app.modules.complaint_events.models import ComplaintEvent
from app.modules.event_dispatcher.handler import EventHandler
from app.modules.notification.delivery_factory import NotificationDeliveryFactory
from app.modules.notification.delivery_memory import InMemoryNotificationDeliveryStore
from app.modules.notification.factory import NotificationFactory
from app.modules.notification.intent_factory import NotificationIntentFactory
from app.modules.notification.intent_memory import InMemoryNotificationIntentStore
from app.modules.notification.memory import InMemoryNotificationStore

logger = get_logger(__name__)


class NotificationEventHandler(EventHandler):
    """Consumes ComplaintEvent; builds Notification, Intent, and Delivery plans."""

    def __init__(
        self,
        store: InMemoryNotificationStore | None = None,
        intent_store: InMemoryNotificationIntentStore | None = None,
        delivery_store: InMemoryNotificationDeliveryStore | None = None,
    ) -> None:
        self._store = store if store is not None else InMemoryNotificationStore()
        self._intent_store = (
            intent_store
            if intent_store is not None
            else InMemoryNotificationIntentStore()
        )
        self._delivery_store = (
            delivery_store
            if delivery_store is not None
            else InMemoryNotificationDeliveryStore()
        )

    @property
    def store(self) -> InMemoryNotificationStore:
        return self._store

    @property
    def intent_store(self) -> InMemoryNotificationIntentStore:
        return self._intent_store

    @property
    def delivery_store(self) -> InMemoryNotificationDeliveryStore:
        return self._delivery_store

    def handle(self, event: Any) -> None:
        if not isinstance(event, ComplaintEvent):
            return
        if not NotificationFactory.supports(event):
            logger.debug(
                "Skipping unsupported event for notification",
                extra={
                    "extra_fields": {
                        "eventType": getattr(event, "event_type", None),
                    }
                },
            )
            return

        notification = NotificationFactory.from_event(event)
        self._store.add(notification)

        intent = NotificationIntentFactory.from_notification(notification)
        self._intent_store.add(intent)

        deliveries = NotificationDeliveryFactory.from_intent(intent)
        self._delivery_store.add_many(deliveries)

        logger.debug(
            "Notification, intent, and delivery plans built",
            extra={
                "extra_fields": {
                    "notificationId": str(notification.notification_id),
                    "notificationType": notification.notification_type.value,
                    "sourceEvent": str(notification.source_event),
                    "intentId": str(intent.intent_id),
                    "templateKey": intent.template_key,
                    "priority": intent.priority.value,
                    "deliveryCount": len(deliveries),
                    "channels": [d.channel.value for d in deliveries],
                }
            },
        )
