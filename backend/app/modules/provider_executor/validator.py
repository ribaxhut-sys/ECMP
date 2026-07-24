"""ProviderExecutionValidator — validate provider-execution inputs (TASK-059).

Checks DeliveryRequest, TransportAdapter, and channel support.
Never calls send() / health() / network.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.modules.delivery.models import DeliveryChannel, DeliveryRequest
from app.modules.provider_executor.models import ProviderExecutionResult
from app.modules.transport.adapter import TransportAdapter
from app.modules.transport.models import TransportCapability

# DeliveryChannel → TransportCapability (WEBSOCKET has no transport capability yet)
_CHANNEL_MAP: dict[DeliveryChannel, TransportCapability] = {
    DeliveryChannel.EMAIL: TransportCapability.EMAIL,
    DeliveryChannel.WHATSAPP: TransportCapability.WHATSAPP,
    DeliveryChannel.SMS: TransportCapability.SMS,
    DeliveryChannel.PUSH: TransportCapability.PUSH,
}


@dataclass(frozen=True, slots=True)
class ProviderExecutionValidation:
    """Internal validation outcome with optional resolved capability."""

    result: ProviderExecutionResult
    capability: TransportCapability | None = None


class ProviderExecutionValidator:
    """Validate provider-execution inputs. Shape / compatibility only — never send."""

    def validate(
        self,
        delivery_request: DeliveryRequest | None,
        transport_adapter: TransportAdapter | None,
    ) -> ProviderExecutionValidation:
        if delivery_request is None:
            return ProviderExecutionValidation(
                result=ProviderExecutionResult(
                    success=False,
                    ready=False,
                    provider_name=None,
                    reason="MISSING_DELIVERY_REQUEST: delivery_request is required",
                )
            )

        if not isinstance(delivery_request, DeliveryRequest):
            return ProviderExecutionValidation(
                result=ProviderExecutionResult(
                    success=False,
                    ready=False,
                    provider_name=None,
                    reason=(
                        "INVALID_DELIVERY_REQUEST: expected DeliveryRequest, "
                        f"got {type(delivery_request).__name__}"
                    ),
                )
            )

        if transport_adapter is None:
            return ProviderExecutionValidation(
                result=ProviderExecutionResult(
                    success=False,
                    ready=False,
                    provider_name=None,
                    reason="MISSING_TRANSPORT_ADAPTER: transport_adapter is required",
                )
            )

        if not isinstance(transport_adapter, TransportAdapter):
            return ProviderExecutionValidation(
                result=ProviderExecutionResult(
                    success=False,
                    ready=False,
                    provider_name=None,
                    reason=(
                        "UNKNOWN_ADAPTER: expected TransportAdapter, "
                        f"got {type(transport_adapter).__name__}"
                    ),
                )
            )

        provider_name = (transport_adapter.name or "").strip() or None

        capability = _CHANNEL_MAP.get(delivery_request.channel)
        if capability is None:
            return ProviderExecutionValidation(
                result=ProviderExecutionResult(
                    success=False,
                    ready=False,
                    provider_name=provider_name,
                    reason=(
                        "UNSUPPORTED_CHANNEL: delivery channel="
                        f"{delivery_request.channel.value} has no "
                        "TransportCapability mapping"
                    ),
                )
            )

        # supports() only — never send() / health()
        if not transport_adapter.supports(capability):
            return ProviderExecutionValidation(
                result=ProviderExecutionResult(
                    success=False,
                    ready=False,
                    provider_name=provider_name,
                    reason=(
                        "ADAPTER_CHANNEL_MISMATCH: adapter="
                        f"{provider_name or '<unnamed>'} does not support "
                        f"channel={capability.value}"
                    ),
                )
            )

        return ProviderExecutionValidation(
            result=ProviderExecutionResult(
                success=True,
                ready=True,
                provider_name=provider_name,
                reason=(
                    f"EXECUTION_READY: provider={provider_name} "
                    f"channel={capability.value}"
                ),
            ),
            capability=capability,
        )
