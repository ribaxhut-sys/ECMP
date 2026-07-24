"""Complaint Event Foundation — public exports (TASK-045)."""

from app.modules.complaint_events.factory import (
    ComplaintEventFactory,
    context_ref_for,
)
from app.modules.complaint_events.models import (
    ComplaintEvent,
    ComplaintEventType,
    EventSourceRef,
    EventTargetRef,
)

__all__ = [
    "ComplaintEvent",
    "ComplaintEventFactory",
    "ComplaintEventType",
    "EventSourceRef",
    "EventTargetRef",
    "context_ref_for",
]
