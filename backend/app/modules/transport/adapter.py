"""TransportAdapter — abstract provider contract (TASK-058).

Interface only. Concrete providers are out of scope.
Registry / Selector must never call send().
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.modules.delivery.models import DeliveryRequest
from app.modules.transport.models import TransportCapability


class TransportAdapter(ABC):
    """Abstract transport / provider adapter. No default provider behavior."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Stable adapter identity for registry / diagnostics."""

    @abstractmethod
    def supports(self, channel: TransportCapability | str) -> bool:
        """Return True if this adapter can handle the channel. No I/O."""

    @abstractmethod
    def send(self, request: DeliveryRequest) -> Any:
        """Provider send contract — MUST NOT be invoked by TASK-058 foundation."""

    @abstractmethod
    def health(self) -> bool:
        """Provider health contract — MUST NOT be invoked by TASK-058 foundation."""
