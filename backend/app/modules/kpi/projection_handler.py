"""KpiProjectionHandler — EventDispatcher consumer (TASK-051).

Updates the in-memory KPI projection from Complaint events only.
Does not call ComplaintService or query Complaint aggregates.
"""

from __future__ import annotations

from typing import Any

from app.core.logging import get_logger
from app.modules.complaint_events.models import ComplaintEvent
from app.modules.event_dispatcher.handler import EventHandler
from app.modules.kpi.projection_store import KpiProjectionStore

logger = get_logger(__name__)


class KpiProjectionHandler(EventHandler):
    """Consumes ComplaintEvent and applies it to KpiProjectionStore."""

    def __init__(self, store: KpiProjectionStore | None = None) -> None:
        self._store = store if store is not None else KpiProjectionStore()

    @property
    def store(self) -> KpiProjectionStore:
        return self._store

    def handle(self, event: Any) -> None:
        if not isinstance(event, ComplaintEvent):
            return

        snapshot = self._store.apply(event)
        logger.debug(
            "KPI projection updated",
            extra={
                "extra_fields": {
                    "eventType": event.event_type.value,
                    "complaintId": str(event.complaint_id),
                    "totalReceived": snapshot.total_received,
                    "currentOpen": snapshot.current_open,
                    "closureRate": snapshot.closure_rate,
                    "resolutionRate": snapshot.resolution_rate,
                    "updatedAt": snapshot.updated_at.isoformat(),
                }
            },
        )
