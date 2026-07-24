"""EventHandler — generic in-process consumer contract (TASK-046).

Handlers are registered with EventDispatcher. Complaint Service never
imports or names concrete handlers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class EventHandler(ABC):
    """Synchronous in-process event consumer.

    Implementations must not assume broker/async delivery. ``handle`` runs
    on the caller's thread in registration order.
    """

    @abstractmethod
    def handle(self, event: Any) -> None:
        """Process one event. Exceptions are caught by the dispatcher."""
