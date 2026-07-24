"""TransportSelector — choose a TransportAdapter for a DeliveryRequest (TASK-058).

Selection / registry lookup only. Never calls adapter.send() or health().
"""

from __future__ import annotations

from app.core.logging import get_logger
from app.modules.delivery.models import DeliveryChannel, DeliveryRequest
from app.modules.transport.adapter import TransportAdapter
from app.modules.transport.models import TransportCapability, TransportResult
from app.modules.transport.registry import TransportRegistry

logger = get_logger(__name__)

# DeliveryChannel → TransportCapability (WEBSOCKET has no transport capability yet)
_CHANNEL_MAP: dict[DeliveryChannel, TransportCapability] = {
    DeliveryChannel.EMAIL: TransportCapability.EMAIL,
    DeliveryChannel.WHATSAPP: TransportCapability.WHATSAPP,
    DeliveryChannel.SMS: TransportCapability.SMS,
    DeliveryChannel.PUSH: TransportCapability.PUSH,
}


class TransportSelector:
    """Select an adapter for a DeliveryRequest. Never sends."""

    def __init__(self, registry: TransportRegistry | None = None) -> None:
        self._registry = registry if registry is not None else TransportRegistry()

    @property
    def registry(self) -> TransportRegistry:
        return self._registry

    def select(
        self,
        request: DeliveryRequest,
        registry: TransportRegistry | None = None,
    ) -> tuple[TransportAdapter | None, TransportResult]:
        """Look up an adapter for the request channel. Never calls send()."""
        if not isinstance(request, DeliveryRequest):
            raise TypeError(
                f"request must be DeliveryRequest, got {type(request).__name__}"
            )

        reg = registry if registry is not None else self._registry
        capability = _CHANNEL_MAP.get(request.channel)

        if capability is None:
            result = TransportResult(
                supported=False,
                adapter_found=False,
                adapter_name=None,
                reason=(
                    f"UNKNOWN_CHANNEL: delivery channel={request.channel.value} "
                    "has no TransportCapability mapping"
                ),
            )
            logger.debug(
                "TransportSelector rejected unknown channel",
                extra={
                    "extra_fields": {
                        "channel": request.channel.value,
                        "reason": result.reason,
                    }
                },
            )
            return None, result

        adapter = reg.lookup(capability)
        if adapter is None:
            result = TransportResult(
                supported=True,
                adapter_found=False,
                adapter_name=None,
                reason=f"ADAPTER_NOT_FOUND: channel={capability.value}",
            )
            logger.debug(
                "TransportSelector found no adapter",
                extra={
                    "extra_fields": {
                        "channel": capability.value,
                        "reason": result.reason,
                    }
                },
            )
            return None, result

        result = TransportResult(
            supported=True,
            adapter_found=True,
            adapter_name=adapter.name,
            reason=f"ADAPTER_SELECTED: name={adapter.name} channel={capability.value}",
        )
        logger.debug(
            "TransportSelector selected adapter (no send)",
            extra={
                "extra_fields": {
                    "adapterName": adapter.name,
                    "channel": capability.value,
                    "requestId": str(request.request_id),
                }
            },
        )
        return adapter, result
