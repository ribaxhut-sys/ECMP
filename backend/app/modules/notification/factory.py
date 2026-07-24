"""NotificationFactory — build immutable Notification from domain events (TASK-047).

No delivery. Transport-independent.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import MappingProxyType
from typing import Any, Mapping

from app.modules.complaint_events.models import ComplaintEvent, ComplaintEventType
from app.modules.notification.event_models import (
    Notification,
    NotificationSeverity,
    NotificationType,
)

_EVENT_TO_TYPE: Mapping[ComplaintEventType, NotificationType] = {
    ComplaintEventType.CREATED: NotificationType.COMPLAINT_CREATED,
    ComplaintEventType.ASSIGNED: NotificationType.COMPLAINT_ASSIGNED,
    ComplaintEventType.ACCEPTED: NotificationType.COMPLAINT_ACCEPTED,
    ComplaintEventType.IN_PROGRESS: NotificationType.COMPLAINT_IN_PROGRESS,
    ComplaintEventType.RESOLVED: NotificationType.COMPLAINT_RESOLVED,
    ComplaintEventType.CLOSED: NotificationType.COMPLAINT_CLOSED,
    ComplaintEventType.ESCALATED: NotificationType.COMPLAINT_ESCALATED,
}

_TITLES: Mapping[ComplaintEventType, str] = {
    ComplaintEventType.CREATED: "Complaint created",
    ComplaintEventType.ASSIGNED: "Complaint assigned",
    ComplaintEventType.ACCEPTED: "Complaint accepted",
    ComplaintEventType.IN_PROGRESS: "Complaint in progress",
    ComplaintEventType.RESOLVED: "Complaint resolved",
    ComplaintEventType.CLOSED: "Complaint closed",
    ComplaintEventType.ESCALATED: "Complaint escalated",
}

_PRIORITY_SEVERITY: Mapping[str, NotificationSeverity] = {
    "LOW": NotificationSeverity.LOW,
    "MEDIUM": NotificationSeverity.MEDIUM,
    "HIGH": NotificationSeverity.HIGH,
    "CRITICAL": NotificationSeverity.CRITICAL,
}


def _resolve_recipient(event: ComplaintEvent) -> str:
    """Diagnostic recipient key — not a delivery address."""
    route = event.routing
    if route is not None:
        receiver_id = (
            str(route.receiver_id) if route.receiver_id is not None else "none"
        )
        return f"receiver:{route.receiver_type.value}:{receiver_id}"
    target_id = (
        str(event.target.target_id) if event.target.target_id is not None else "none"
    )
    return f"target:{event.target.target_type}:{target_id}"


def _resolve_severity(event: ComplaintEvent) -> NotificationSeverity:
    if event.event_type == ComplaintEventType.ESCALATED:
        return NotificationSeverity.CRITICAL
    return _PRIORITY_SEVERITY.get(
        (event.priority or "").upper(),
        NotificationSeverity.INFO,
    )


def _resolve_message(event: ComplaintEvent) -> str:
    title = _TITLES[event.event_type]
    return (
        f"{title}: {event.complaint_number} "
        f"(status={event.current_status}, priority={event.priority})"
    )


def _freeze_payload(event: ComplaintEvent) -> Mapping[str, Any]:
    base: dict[str, Any] = {
        "complaintId": str(event.complaint_id),
        "complaintNumber": event.complaint_number,
        "eventType": event.event_type.value,
        "currentStatus": event.current_status,
        "priority": event.priority,
        "contextReference": event.context_reference,
        "sourceType": event.source.source_type,
        "sourceId": str(event.source.source_id),
        "targetType": event.target.target_type,
        "targetId": (
            str(event.target.target_id) if event.target.target_id is not None else None
        ),
    }
    if event.payload:
        base["eventPayload"] = dict(event.payload)
    return MappingProxyType(base)


class NotificationFactory:
    """Creates immutable Notification instances from ComplaintEvent."""

    @classmethod
    def supports(cls, event: ComplaintEvent) -> bool:
        return event.event_type in _EVENT_TO_TYPE

    @classmethod
    def from_event(
        cls,
        event: ComplaintEvent,
        *,
        notification_id: uuid.UUID | None = None,
        created_at: datetime | None = None,
    ) -> Notification:
        """Build a Notification from a supported ComplaintEvent.

        Raises:
            ValueError: when the event type is not supported.
        """
        notification_type = _EVENT_TO_TYPE.get(event.event_type)
        if notification_type is None:
            raise ValueError(
                f"Unsupported complaint event type for notification: {event.event_type}"
            )

        created = created_at or datetime.now(UTC)
        if created.tzinfo is None:
            created = created.replace(tzinfo=UTC)

        return Notification(
            notification_id=notification_id or uuid.uuid4(),
            notification_type=notification_type,
            created_at=created,
            recipient=_resolve_recipient(event),
            title=_TITLES[event.event_type],
            message=_resolve_message(event),
            severity=_resolve_severity(event),
            source_event=event.event_id,
            payload=_freeze_payload(event),
        )
