"""Delivery Engine foundation value objects (TASK-057).

Immutable delivery planning models. Never sends, never calls providers.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping


class DeliveryChannel(StrEnum):
    """Known delivery channels. Unknown values are rejected by the validator."""

    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"
    PUSH = "PUSH"
    SMS = "SMS"
    WEBSOCKET = "WEBSOCKET"


class DeliveryPolicy(StrEnum):
    """Delivery planning policy. Foundation supports DIRECT only."""

    DIRECT = "DIRECT"


def freeze_mapping(data: Mapping[str, Any] | None) -> Mapping[str, Any]:
    """Freeze a mapping for immutable value objects."""
    return MappingProxyType(dict(data or {}))


@dataclass(frozen=True, slots=True)
class DeliveryContext:
    """Generic delivery context. Domain-agnostic (TASK-057)."""

    trace_id: str
    correlation_id: str
    tenant_id: str | None = None
    user_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    def as_dict(self) -> Mapping[str, object]:
        """Diagnostic serialization (not an HTTP / transport contract)."""
        return MappingProxyType(
            {
                "traceId": self.trace_id,
                "correlationId": self.correlation_id,
                "tenantId": self.tenant_id,
                "userId": self.user_id,
                "metadata": dict(self.metadata),
            }
        )


@dataclass(frozen=True, slots=True)
class DeliveryRequest:
    """Immutable prepared delivery unit. Not a send / provider call."""

    request_id: uuid.UUID
    dispatch_request_id: uuid.UUID
    channel: DeliveryChannel
    recipient: str
    template_id: str
    payload: Mapping[str, Any]
    context: DeliveryContext
    metadata: Mapping[str, Any]

    def as_dict(self) -> Mapping[str, object]:
        """Diagnostic serialization (not an HTTP / transport contract)."""
        return MappingProxyType(
            {
                "requestId": str(self.request_id),
                "dispatchRequestId": str(self.dispatch_request_id),
                "channel": self.channel.value,
                "recipient": self.recipient,
                "templateId": self.template_id,
                "payload": dict(self.payload),
                "context": dict(self.context.as_dict()),
                "metadata": dict(self.metadata),
            }
        )


@dataclass(frozen=True, slots=True)
class DeliveryResult:
    """Outcome of delivery preparation / validation. No provider invocation."""

    success: bool
    reason: str
    provider_selected: str | None = None

    def as_dict(self) -> Mapping[str, object]:
        """Diagnostic serialization (not an HTTP / transport contract)."""
        return MappingProxyType(
            {
                "success": self.success,
                "reason": self.reason,
                "providerSelected": self.provider_selected,
            }
        )
