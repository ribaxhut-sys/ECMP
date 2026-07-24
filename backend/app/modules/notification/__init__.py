"""Notification platform module.

TASK-030: templates + queue foundation (no provider delivery).
TASK-047: in-memory Notification domain consumer for EventDispatcher.
TASK-048: NotificationIntent — what to deliver (no transport adapters).
TASK-049: NotificationDelivery — planned delivery action (no sending).
"""

from app.modules.notification.delivery_factory import NotificationDeliveryFactory
from app.modules.notification.delivery_memory import InMemoryNotificationDeliveryStore
from app.modules.notification.delivery_models import (
    NotificationDelivery,
    NotificationDeliveryStatus,
)
from app.modules.notification.event_models import (
    Notification,
    NotificationSeverity,
    NotificationType,
)
from app.modules.notification.factory import NotificationFactory
from app.modules.notification.handler import NotificationEventHandler
from app.modules.notification.intent_factory import NotificationIntentFactory
from app.modules.notification.intent_memory import InMemoryNotificationIntentStore
from app.modules.notification.intent_models import (
    NotificationIntent,
    NotificationIntentChannel,
    NotificationIntentPriority,
)
from app.modules.notification.memory import InMemoryNotificationStore
from app.modules.notification.registration import register_notification_handler

__all__ = [
    "InMemoryNotificationDeliveryStore",
    "InMemoryNotificationIntentStore",
    "InMemoryNotificationStore",
    "Notification",
    "NotificationDelivery",
    "NotificationDeliveryFactory",
    "NotificationDeliveryStatus",
    "NotificationEventHandler",
    "NotificationFactory",
    "NotificationIntent",
    "NotificationIntentChannel",
    "NotificationIntentFactory",
    "NotificationIntentPriority",
    "NotificationSeverity",
    "NotificationType",
    "register_notification_handler",
]
