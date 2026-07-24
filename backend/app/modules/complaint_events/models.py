"""Complaint domain events — immutable in-memory value objects (TASK-045).

No persistence, no event bus. Factory creates events; EventDispatcher
(TASK-046) delivers them in-process to registered handlers.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping

from app.modules.routing import ComplaintRoute


class ComplaintEventType(StrEnum):
    """Significant Complaint lifecycle event types (TASK-045)."""

    CREATED = "ComplaintCreated"
    ASSIGNED = "ComplaintAssigned"
    ACCEPTED = "ComplaintAccepted"
    IN_PROGRESS = "ComplaintInProgress"
    RESOLVED = "ComplaintResolved"
    CLOSED = "ComplaintClosed"
    ESCALATED = "ComplaintEscalated"


@dataclass(frozen=True, slots=True)
class EventSourceRef:
    """Polymorphic origin snapshot carried on the event."""

    source_type: str
    source_id: uuid.UUID


@dataclass(frozen=True, slots=True)
class EventTargetRef:
    """Polymorphic destination snapshot carried on the event."""

    target_type: str
    target_id: uuid.UUID | None


@dataclass(frozen=True, slots=True)
class ComplaintEvent:
    """Immutable Complaint domain event.

    Exists only in memory for this foundation. Not stored, not published.
    """

    event_id: uuid.UUID
    event_type: ComplaintEventType
    occurred_at: datetime
    complaint_id: uuid.UUID
    complaint_number: str
    current_status: str
    priority: str
    source: EventSourceRef
    target: EventTargetRef
    routing: ComplaintRoute | None
    context_reference: str | None
    payload: Mapping[str, Any]

    def as_dict(self) -> Mapping[str, object]:
        """Diagnostic serialization (not an API / bus contract)."""
        route = self.routing
        return MappingProxyType(
            {
                "eventId": str(self.event_id),
                "eventType": self.event_type.value,
                "occurredAt": self.occurred_at.isoformat(),
                "complaintId": str(self.complaint_id),
                "complaintNumber": self.complaint_number,
                "currentStatus": self.current_status,
                "priority": self.priority,
                "sourceType": self.source.source_type,
                "sourceId": str(self.source.source_id),
                "targetType": self.target.target_type,
                "targetId": (
                    str(self.target.target_id)
                    if self.target.target_id is not None
                    else None
                ),
                "routing": (
                    {
                        "receiverType": route.receiver_type.value,
                        "receiverId": (
                            str(route.receiver_id)
                            if route.receiver_id is not None
                            else None
                        ),
                        "assignmentContext": dict(route.assignment_context),
                        "routingReason": route.routing_reason,
                    }
                    if route is not None
                    else None
                ),
                "contextReference": self.context_reference,
                "payload": dict(self.payload),
            }
        )
