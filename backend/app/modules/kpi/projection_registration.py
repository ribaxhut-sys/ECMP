"""Register KPI projection consumer on EventDispatcher (TASK-051).

ComplaintService must never import this module.
Composition roots (routers / dependencies) perform registration.
"""

from __future__ import annotations

from app.modules.event_dispatcher import EventDispatcher
from app.modules.kpi.projection_handler import KpiProjectionHandler
from app.modules.kpi.projection_store import KpiProjectionStore


def register_kpi_projection_handler(
    dispatcher: EventDispatcher,
    *,
    store: KpiProjectionStore | None = None,
    handler: KpiProjectionHandler | None = None,
) -> KpiProjectionHandler:
    """Register KpiProjectionHandler if not already present."""
    existing = [
        h
        for h in dispatcher.registered_handlers()
        if isinstance(h, KpiProjectionHandler)
    ]
    if existing:
        return existing[0]

    resolved = handler or KpiProjectionHandler(store=store)
    dispatcher.register(resolved)
    return resolved
