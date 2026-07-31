"""CAPABILITY-010 reusable Activity Timeline / History.

Append-only ``timeline_entries``. Domains emit events; Timeline records.
Does not replace API-209 ``complaint_timelines`` (module ``timelines``).
"""

from app.modules.timeline.domain import (
    ActorType,
    AggregateType,
    TimelineEntry,
    TimelineEventType,
)
from app.modules.timeline.handler import TimelineEventHandler
from app.modules.timeline.registration import register_timeline_handler

__all__ = [
    "AggregateType",
    "ActorType",
    "TimelineEntry",
    "TimelineEventHandler",
    "TimelineEventType",
    "register_timeline_handler",
]
