"""In-memory NotificationDelivery buffer for diagnostics/testing (TASK-049).

No database, queue, broker, scheduler, or transport.
"""

from __future__ import annotations

from app.modules.notification.delivery_models import NotificationDelivery


class InMemoryNotificationDeliveryStore:
    """Process-local list of planned deliveries (discarded on process end)."""

    def __init__(self) -> None:
        self._items: list[NotificationDelivery] = []

    def add(self, delivery: NotificationDelivery) -> None:
        self._items.append(delivery)

    def add_many(self, deliveries: tuple[NotificationDelivery, ...] | list[NotificationDelivery]) -> None:
        self._items.extend(deliveries)

    def all(self) -> list[NotificationDelivery]:
        return list(self._items)

    def clear(self) -> None:
        self._items.clear()

    def __len__(self) -> int:
        return len(self._items)
