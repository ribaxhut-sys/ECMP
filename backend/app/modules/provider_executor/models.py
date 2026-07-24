"""Provider Executor Foundation value objects (TASK-059).

Immutable execution-contract models. No network. No provider invocation.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping

from app.modules.delivery.models import DeliveryContext, DeliveryRequest, freeze_mapping
from app.modules.transport.adapter import TransportAdapter


class ProviderExecutionPolicy(StrEnum):
    """Provider execution policy. Foundation supports SYNC_PREPARE only."""

    SYNC_PREPARE = "SYNC_PREPARE"


@dataclass(frozen=True, slots=True)
class ProviderExecutionRequest:
    """Immutable prepared provider-execution contract. Not a send / provider call."""

    execution_id: uuid.UUID
    delivery_request: DeliveryRequest
    transport_adapter: TransportAdapter
    context: DeliveryContext
    metadata: Mapping[str, Any]

    def as_dict(self) -> Mapping[str, object]:
        """Diagnostic serialization (not an HTTP / transport contract)."""
        return MappingProxyType(
            {
                "executionId": str(self.execution_id),
                "deliveryRequestId": str(self.delivery_request.request_id),
                "providerName": self.transport_adapter.name,
                "channel": self.delivery_request.channel.value,
                "context": dict(self.context.as_dict()),
                "metadata": dict(self.metadata),
            }
        )


@dataclass(frozen=True, slots=True)
class ProviderExecutionResult:
    """Outcome of provider-execution preparation. No provider invocation."""

    success: bool
    ready: bool
    provider_name: str | None
    reason: str

    def as_dict(self) -> Mapping[str, object]:
        """Diagnostic serialization (not an HTTP / transport contract)."""
        return MappingProxyType(
            {
                "success": self.success,
                "ready": self.ready,
                "providerName": self.provider_name,
                "reason": self.reason,
            }
        )


__all__ = [
    "ProviderExecutionPolicy",
    "ProviderExecutionRequest",
    "ProviderExecutionResult",
    "freeze_mapping",
]
