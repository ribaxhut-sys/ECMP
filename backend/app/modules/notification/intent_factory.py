"""NotificationIntentFactory — build intents from Notification (TASK-048).

No transport. No sending.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import MappingProxyType
from typing import Any, Mapping

from app.modules.notification.event_models import (
    Notification,
    NotificationSeverity,
    NotificationType,
)
from app.modules.notification.intent_models import (
    NotificationIntent,
    NotificationIntentChannel,
    NotificationIntentPriority,
)

_SEVERITY_TO_PRIORITY: Mapping[NotificationSeverity, NotificationIntentPriority] = {
    NotificationSeverity.INFO: NotificationIntentPriority.INFO,
    NotificationSeverity.LOW: NotificationIntentPriority.LOW,
    NotificationSeverity.MEDIUM: NotificationIntentPriority.MEDIUM,
    NotificationSeverity.HIGH: NotificationIntentPriority.HIGH,
    NotificationSeverity.CRITICAL: NotificationIntentPriority.CRITICAL,
}

_TYPE_TO_TEMPLATE: Mapping[NotificationType, str] = {
    NotificationType.COMPLAINT_CREATED: "complaint.created",
    NotificationType.COMPLAINT_ASSIGNED: "complaint.assigned",
    NotificationType.COMPLAINT_ACCEPTED: "complaint.accepted",
    NotificationType.COMPLAINT_IN_PROGRESS: "complaint.in_progress",
    NotificationType.COMPLAINT_RESOLVED: "complaint.resolved",
    NotificationType.COMPLAINT_CLOSED: "complaint.closed",
    NotificationType.COMPLAINT_ESCALATED: "complaint.escalated",
}

_PRIORITY_CHANNELS: Mapping[
    NotificationIntentPriority, tuple[NotificationIntentChannel, ...]
] = {
    NotificationIntentPriority.INFO: (NotificationIntentChannel.EMAIL,),
    NotificationIntentPriority.LOW: (NotificationIntentChannel.EMAIL,),
    NotificationIntentPriority.MEDIUM: (
        NotificationIntentChannel.EMAIL,
        NotificationIntentChannel.WEBSOCKET,
    ),
    NotificationIntentPriority.HIGH: (
        NotificationIntentChannel.EMAIL,
        NotificationIntentChannel.PUSH,
        NotificationIntentChannel.WEBSOCKET,
    ),
    NotificationIntentPriority.CRITICAL: (
        NotificationIntentChannel.EMAIL,
        NotificationIntentChannel.PUSH,
        NotificationIntentChannel.WHATSAPP,
        NotificationIntentChannel.SMS,
        NotificationIntentChannel.WEBSOCKET,
    ),
}


def _priority_for(notification: Notification) -> NotificationIntentPriority:
    return _SEVERITY_TO_PRIORITY.get(
        notification.severity,
        NotificationIntentPriority.INFO,
    )


def _channels_for(
    priority: NotificationIntentPriority,
) -> tuple[NotificationIntentChannel, ...]:
    return _PRIORITY_CHANNELS.get(
        priority,
        (NotificationIntentChannel.EMAIL,),
    )


def _variables_for(notification: Notification) -> Mapping[str, Any]:
    data: dict[str, Any] = {
        "title": notification.title,
        "message": notification.message,
        "notificationType": notification.notification_type.value,
        "severity": notification.severity.value,
    }
    # Flatten known payload keys for template variables.
    for key, value in dict(notification.payload).items():
        if key == "eventPayload" and isinstance(value, Mapping):
            for nested_key, nested_value in value.items():
                data[f"event.{nested_key}"] = nested_value
        else:
            data[key] = value
    return MappingProxyType(data)


def _metadata_for(notification: Notification) -> Mapping[str, Any]:
    return MappingProxyType(
        {
            "sourceEvent": str(notification.source_event),
            "notificationType": notification.notification_type.value,
            "severity": notification.severity.value,
            "recipient": notification.recipient,
            "createdAt": notification.created_at.isoformat(),
        }
    )


class NotificationIntentFactory:
    """Creates immutable NotificationIntent from Notification domain objects."""

    @classmethod
    def template_key_for(cls, notification_type: NotificationType) -> str:
        try:
            return _TYPE_TO_TEMPLATE[notification_type]
        except KeyError as exc:
            raise ValueError(
                f"No template mapping for notification type: {notification_type}"
            ) from exc

    @classmethod
    def from_notification(
        cls,
        notification: Notification,
        *,
        intent_id: uuid.UUID | None = None,
        created_at: datetime | None = None,
    ) -> NotificationIntent:
        priority = _priority_for(notification)
        created = created_at or datetime.now(UTC)
        if created.tzinfo is None:
            created = created.replace(tzinfo=UTC)

        return NotificationIntent(
            intent_id=intent_id or uuid.uuid4(),
            created_at=created,
            notification_id=notification.notification_id,
            recipient_key=notification.recipient,
            preferred_channels=_channels_for(priority),
            priority=priority,
            template_key=cls.template_key_for(notification.notification_type),
            variables=_variables_for(notification),
            metadata=_metadata_for(notification),
        )
