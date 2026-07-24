"""In-memory NotificationIntent buffer for diagnostics/testing (TASK-048).

No database, queue, broker, or transport.
"""

from __future__ import annotations

from app.modules.notification.intent_models import NotificationIntent


class InMemoryNotificationIntentStore:
    """Process-local list of built intents (discarded on process end)."""

    def __init__(self) -> None:
        self._items: list[NotificationIntent] = []

    def add(self, intent: NotificationIntent) -> None:
        self._items.append(intent)

    def all(self) -> list[NotificationIntent]:
        return list(self._items)

    def clear(self) -> None:
        self._items.clear()

    def __len__(self) -> int:
        return len(self._items)
