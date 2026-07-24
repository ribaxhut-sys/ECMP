"""DashboardProjectionHandler — EventDispatcher consumer (TASK-050).

Updates the in-memory dashboard projection from Complaint events only.
Does not call ComplaintService or query Complaint aggregates.
"""

from __future__ import annotations

from typing import Any

from app.core.logging import get_logger
from app.modules.complaint_events.models import ComplaintEvent
from app.modules.dashboard.projection_store import DashboardProjectionStore
from app.modules.event_dispatcher.handler import EventHandler

logger = get_logger(__name__)


class DashboardProjectionHandler(EventHandler):
    """Consumes ComplaintEvent and applies it to DashboardProjectionStore."""

    def __init__(self, store: DashboardProjectionStore | None = None) -> None:
        self._store = store if store is not None else DashboardProjectionStore()

    @property
    def store(self) -> DashboardProjectionStore:
        return self._store

    def handle(self, event: Any) -> None:
        if not isinstance(event, ComplaintEvent):
            return

        snapshot = self._store.apply(event)
        logger.debug(
            "Dashboard projection updated",
            extra={
                "extra_fields": {
                    "eventType": event.event_type.value,
                    "complaintId": str(event.complaint_id),
                    "totalComplaints": snapshot.total_complaints,
                    "openComplaints": snapshot.open_complaints,
                    "updatedAt": snapshot.updated_at.isoformat(),
                }
            },
        )
