"""Register Dashboard projection consumer on EventDispatcher (TASK-050).

ComplaintService must never import this module.
Composition roots (routers / dependencies) perform registration.
"""

from __future__ import annotations

from app.modules.dashboard.projection_handler import DashboardProjectionHandler
from app.modules.dashboard.projection_store import DashboardProjectionStore
from app.modules.event_dispatcher import EventDispatcher


def register_dashboard_projection_handler(
    dispatcher: EventDispatcher,
    *,
    store: DashboardProjectionStore | None = None,
    handler: DashboardProjectionHandler | None = None,
) -> DashboardProjectionHandler:
    """Register DashboardProjectionHandler if not already present."""
    existing = [
        h
        for h in dispatcher.registered_handlers()
        if isinstance(h, DashboardProjectionHandler)
    ]
    if existing:
        return existing[0]

    resolved = handler or DashboardProjectionHandler(store=store)
    dispatcher.register(resolved)
    return resolved
