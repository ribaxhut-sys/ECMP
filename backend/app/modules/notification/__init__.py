"""Notification platform module.

TASK-030: templates + queue foundation.
TASK-047/048/049: in-memory Notification → Intent → Delivery via EventDispatcher.
CAPABILITY-009: persisted Notification domain lifecycle + stub providers
(retry / process; no real SMTP / WhatsApp / SMS / Push / webhook).
"""

from app.modules.notification.delivery_factory import NotificationDeliveryFactory
from app.modules.notification.delivery_memory import InMemoryNotificationDeliveryStore
from app.modules.notification.delivery_models import (
    NotificationDelivery,
    NotificationDeliveryStatus,
)
from app.modules.notification.domain import NotificationRecord
from app.modules.notification.event_models import (
    Notification,
    NotificationSeverity,
    NotificationType,
)
from app.modules.notification.factory import NotificationFactory
from app.modules.notification.handler import NotificationEventHandler
from app.modules.notification.infrastructure import (
    NotificationProvider,
    ProviderResult,
    StubNotificationProvider,
)
from app.modules.notification.intent_factory import NotificationIntentFactory
from app.modules.notification.intent_memory import InMemoryNotificationIntentStore
from app.modules.notification.intent_models import (
    NotificationIntent,
    NotificationIntentChannel,
    NotificationIntentPriority,
)
from app.modules.notification.memory import InMemoryNotificationStore
from app.modules.notification.persistence_handler import NotificationPersistenceHandler
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
    "NotificationPersistenceHandler",
    "NotificationProvider",
    "NotificationRecord",
    "NotificationSeverity",
    "NotificationType",
    "ProviderResult",
    "StubNotificationProvider",
    "register_notification_handler",
]
