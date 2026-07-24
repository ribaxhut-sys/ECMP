"""In-memory notification buffer for diagnostics/testing (TASK-047).

No database, queue, or broker.
"""

from __future__ import annotations

from app.modules.notification.event_models import Notification


class InMemoryNotificationStore:
    """Process-local list of built notifications (discarded on process end)."""

    def __init__(self) -> None:
        self._items: list[Notification] = []

    def add(self, notification: Notification) -> None:
        self._items.append(notification)

    def all(self) -> list[Notification]:
        return list(self._items)

    def clear(self) -> None:
        self._items.clear()

    def __len__(self) -> int:
        return len(self._items)
