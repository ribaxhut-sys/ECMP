"""Persist Notification requests from ComplaintEvent (CAPABILITY-009).

Opens its own short-lived DB session so Complaint never imports Notification
and never passes a session into consumers.
"""

from __future__ import annotations

from typing import Any

from app.core.logging import get_logger
from app.db.session import get_session_factory
from app.modules.complaint_events.models import ComplaintEvent
from app.modules.event_dispatcher.handler import EventHandler
from app.modules.notification.factory import NotificationFactory
from app.modules.notification.repository import NotificationRepository
from app.modules.notification.service import NotificationService
from app.modules.settings.repository import SettingsRepository
from app.modules.settings.service import SettingsService

logger = get_logger(__name__)


class NotificationPersistenceHandler(EventHandler):
    """ComplaintEvent → PENDING notification_queue row (no transport send)."""

    def handle(self, event: Any) -> None:
        if not isinstance(event, ComplaintEvent):
            return
        if not NotificationFactory.supports(event):
            return

        notification = NotificationFactory.from_event(event)
        session = get_session_factory()()
        try:
            settings = SettingsService(SettingsRepository(session))
            service = NotificationService(
                repository=NotificationRepository(session),
                settings=settings,
            )
            if not service.is_enabled():
                logger.debug(
                    "Skipping notification persistence; notifications disabled",
                    extra={
                        "extra_fields": {
                            "eventType": event.event_type.value,
                            "complaintId": str(event.complaint_id),
                        }
                    },
                )
                return

            service.enqueue_domain_notification(
                notification_type=notification.notification_type.value,
                recipient=notification.recipient,
                subject=notification.title,
                message=notification.message,
                payload=dict(notification.payload),
                template_code=f"complaint.{event.event_type.value.lower()}",
                notification_id=notification.notification_id,
                commit=True,
            )
            logger.debug(
                "Notification request persisted from complaint event",
                extra={
                    "extra_fields": {
                        "notificationId": str(notification.notification_id),
                        "notificationType": notification.notification_type.value,
                        "complaintId": str(event.complaint_id),
                    }
                },
            )
        except Exception:
            session.rollback()
            logger.exception(
                "Failed to persist notification from complaint event",
                extra={
                    "extra_fields": {
                        "eventType": getattr(event, "event_type", None),
                        "complaintId": str(getattr(event, "complaint_id", "")),
                    }
                },
            )
            raise
        finally:
            session.close()
