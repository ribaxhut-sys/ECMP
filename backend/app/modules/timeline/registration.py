"""Register TimelineEventHandler on EventDispatcher (CAPABILITY-010).

ComplaintService must never import this module.
"""

from __future__ import annotations

from app.modules.event_dispatcher import EventDispatcher
from app.modules.timeline.handler import TimelineEventHandler


def register_timeline_handler(
    dispatcher: EventDispatcher,
    *,
    handler: TimelineEventHandler | None = None,
) -> TimelineEventHandler:
    """Idempotently register TimelineEventHandler."""
    existing = [
        h
        for h in dispatcher.registered_handlers()
        if isinstance(h, TimelineEventHandler)
    ]
    if existing:
        return existing[0]

    resolved = handler or TimelineEventHandler()
    dispatcher.register(resolved)
    return resolved
