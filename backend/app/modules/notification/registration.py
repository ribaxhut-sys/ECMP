"""Register Notification consumer on an EventDispatcher (TASK-047/048/049).

ComplaintService must never import this module.
Composition roots (routers / dependencies) perform registration.
"""

from __future__ import annotations

from app.modules.event_dispatcher import EventDispatcher
from app.modules.notification.delivery_memory import InMemoryNotificationDeliveryStore
from app.modules.notification.handler import NotificationEventHandler
from app.modules.notification.intent_memory import InMemoryNotificationIntentStore
from app.modules.notification.memory import InMemoryNotificationStore


def register_notification_handler(
    dispatcher: EventDispatcher,
    *,
    store: InMemoryNotificationStore | None = None,
    intent_store: InMemoryNotificationIntentStore | None = None,
    delivery_store: InMemoryNotificationDeliveryStore | None = None,
    handler: NotificationEventHandler | None = None,
) -> NotificationEventHandler:
    """Register NotificationEventHandler if not already present on ``dispatcher``."""
    existing = [
        h
        for h in dispatcher.registered_handlers()
        if isinstance(h, NotificationEventHandler)
    ]
    if existing:
        return existing[0]

    resolved = handler or NotificationEventHandler(
        store=store,
        intent_store=intent_store,
        delivery_store=delivery_store,
    )
    dispatcher.register(resolved)
    return resolved
