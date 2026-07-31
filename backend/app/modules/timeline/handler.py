"""Record TimelineEntry from ComplaintEvent (CAPABILITY-010).

Opens its own DB session. Complaint / Queue / Notification modules are
never imported for business logic — Timeline only records what happened.
"""

from __future__ import annotations

from typing import Any

from app.core.logging import get_logger
from app.db.session import get_session_factory
from app.modules.complaint_events.models import ComplaintEvent, ComplaintEventType
from app.modules.event_dispatcher.handler import EventHandler
from app.modules.timeline.domain.enums import ActorType, AggregateType, TimelineEventType
from app.modules.timeline.repository import TimelineRepository
from app.modules.timeline.service import ActivityTimelineService

logger = get_logger(__name__)

_EVENT_TO_TIMELINE: dict[ComplaintEventType, TimelineEventType] = {
    ComplaintEventType.CREATED: TimelineEventType.COMPLAINT_CREATED,
    ComplaintEventType.ASSIGNED: TimelineEventType.COMPLAINT_ASSIGNED,
    ComplaintEventType.ACCEPTED: TimelineEventType.COMPLAINT_ACCEPTED,
    ComplaintEventType.IN_PROGRESS: TimelineEventType.COMPLAINT_IN_PROGRESS,
    ComplaintEventType.RESOLVED: TimelineEventType.COMPLAINT_RESOLVED,
    ComplaintEventType.CLOSED: TimelineEventType.COMPLAINT_CLOSED,
    ComplaintEventType.ESCALATED: TimelineEventType.COMPLAINT_ESCALATED,
}

_TITLES: dict[ComplaintEventType, str] = {
    ComplaintEventType.CREATED: "Complaint created",
    ComplaintEventType.ASSIGNED: "Complaint assigned",
    ComplaintEventType.ACCEPTED: "Complaint accepted",
    ComplaintEventType.IN_PROGRESS: "Complaint in progress",
    ComplaintEventType.RESOLVED: "Complaint resolved",
    ComplaintEventType.CLOSED: "Complaint closed",
    ComplaintEventType.ESCALATED: "Complaint escalated",
}


class TimelineEventHandler(EventHandler):
    """ComplaintEvent → append-only timeline_entries row."""

    def handle(self, event: Any) -> None:
        if not isinstance(event, ComplaintEvent):
            return
        timeline_type = _EVENT_TO_TIMELINE.get(event.event_type)
        if timeline_type is None:
            return

        title = _TITLES[event.event_type]
        description = (
            f"{title}: {event.complaint_number} "
            f"(status={event.current_status}, priority={event.priority})"
        )
        metadata: dict[str, Any] = {
            "complaintNumber": event.complaint_number,
            "currentStatus": event.current_status,
            "priority": event.priority,
            "sourceEventId": str(event.event_id),
            "contextReference": event.context_reference,
        }
        if event.payload:
            metadata["eventPayload"] = dict(event.payload)

        session = get_session_factory()()
        try:
            service = ActivityTimelineService(TimelineRepository(session))
            service.record(
                aggregate_type=AggregateType.COMPLAINT.value,
                aggregate_id=event.complaint_id,
                event_type=timeline_type.value,
                title=title,
                description=description,
                actor_type=ActorType.SYSTEM.value,
                actor_id=None,
                actor_name="EventDispatcher",
                metadata=metadata,
                commit=True,
            )
            logger.debug(
                "Timeline entry recorded from complaint event",
                extra={
                    "extra_fields": {
                        "eventType": event.event_type.value,
                        "complaintId": str(event.complaint_id),
                    }
                },
            )
        except Exception:
            session.rollback()
            logger.exception(
                "Failed to record timeline entry from complaint event",
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
