"""Register Notification consumers on an EventDispatcher (TASK-047/048/049 + CAPABILITY-009).

ComplaintService must never import this module.
Composition roots (routers / dependencies) perform registration.
"""

from __future__ import annotations

from app.modules.event_dispatcher import EventDispatcher
from app.modules.notification.delivery_memory import InMemoryNotificationDeliveryStore
from app.modules.notification.handler import NotificationEventHandler
from app.modules.notification.intent_memory import InMemoryNotificationIntentStore
from app.modules.notification.memory import InMemoryNotificationStore
from app.modules.notification.persistence_handler import NotificationPersistenceHandler


def register_notification_handler(
    dispatcher: EventDispatcher,
    *,
    store: InMemoryNotificationStore | None = None,
    intent_store: InMemoryNotificationIntentStore | None = None,
    delivery_store: InMemoryNotificationDeliveryStore | None = None,
    handler: NotificationEventHandler | None = None,
    persist: bool = False,
) -> NotificationEventHandler:
    """Register in-memory NotificationEventHandler.

    Pass ``persist=True`` from the composition root (CAPABILITY-009) to also
    register ``NotificationPersistenceHandler``. Unit tests keep the default.
    """
    existing = [
        h
        for h in dispatcher.registered_handlers()
        if isinstance(h, NotificationEventHandler)
    ]
    if existing:
        resolved = existing[0]
    else:
        resolved = handler or NotificationEventHandler(
            store=store,
            intent_store=intent_store,
            delivery_store=delivery_store,
        )
        dispatcher.register(resolved)

    if persist:
        persist_existing = [
            h
            for h in dispatcher.registered_handlers()
            if isinstance(h, NotificationPersistenceHandler)
        ]
        if not persist_existing:
            dispatcher.register(NotificationPersistenceHandler())

    return resolved
