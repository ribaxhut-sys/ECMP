"""Transport Adapter Foundation value objects (TASK-058).

Provider abstraction models. No network. No provider implementations.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping


class TransportCapability(StrEnum):
    """Channels a transport adapter may declare support for."""

    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"
    SMS = "SMS"
    PUSH = "PUSH"
    WEBHOOK = "WEBHOOK"


@dataclass(frozen=True, slots=True)
class TransportResult:
    """Outcome of transport selection / registry lookup. No send performed."""

    supported: bool
    adapter_found: bool
    adapter_name: str | None
    reason: str

    def as_dict(self) -> Mapping[str, object]:
        """Diagnostic serialization (not an HTTP / transport contract)."""
        return MappingProxyType(
            {
                "supported": self.supported,
                "adapterFound": self.adapter_found,
                "adapterName": self.adapter_name,
                "reason": self.reason,
            }
        )
