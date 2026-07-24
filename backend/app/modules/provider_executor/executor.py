"""ProviderExecutor — provider execution contract foundation (TASK-059).

Validates and builds ProviderExecutionRequest. NEVER invokes adapters.
NEVER calls send() / health() / network.
"""

from __future__ import annotations

import uuid

from app.core.logging import get_logger
from app.modules.delivery.models import DeliveryRequest, freeze_mapping
from app.modules.provider_executor.models import (
    ProviderExecutionPolicy,
    ProviderExecutionRequest,
    ProviderExecutionResult,
)
from app.modules.provider_executor.validator import ProviderExecutionValidator
from app.modules.transport.adapter import TransportAdapter

logger = get_logger(__name__)


class ProviderExecutor:
    """Prepare ProviderExecutionRequest / Result. No send, no provider call."""

    def __init__(
        self,
        validator: ProviderExecutionValidator | None = None,
        policy: ProviderExecutionPolicy = ProviderExecutionPolicy.SYNC_PREPARE,
    ) -> None:
        if policy is not ProviderExecutionPolicy.SYNC_PREPARE:
            raise ValueError(
                f"Unsupported provider execution policy for TASK-059: {policy!r} "
                "(only SYNC_PREPARE is allowed)"
            )
        self._validator = (
            validator if validator is not None else ProviderExecutionValidator()
        )
        self._policy = policy

    @property
    def policy(self) -> ProviderExecutionPolicy:
        return self._policy

    @property
    def validator(self) -> ProviderExecutionValidator:
        return self._validator

    def prepare(
        self,
        delivery_request: DeliveryRequest | None,
        transport_adapter: TransportAdapter | None,
    ) -> tuple[ProviderExecutionRequest | None, ProviderExecutionResult]:
        """Validate and build a ProviderExecutionRequest. Never invokes adapter."""
        validation = self._validator.validate(delivery_request, transport_adapter)
        result = validation.result

        if (
            not result.success
            or not result.ready
            or delivery_request is None
            or transport_adapter is None
            or not isinstance(delivery_request, DeliveryRequest)
            or not isinstance(transport_adapter, TransportAdapter)
        ):
            logger.debug(
                "ProviderExecutor rejected execution contract",
                extra={
                    "extra_fields": {
                        "reason": result.reason,
                        "providerName": result.provider_name,
                        "ready": result.ready,
                    }
                },
            )
            return None, result

        request = ProviderExecutionRequest(
            execution_id=uuid.uuid4(),
            delivery_request=delivery_request,
            transport_adapter=transport_adapter,
            context=delivery_request.context,
            metadata=freeze_mapping(
                {
                    "policy": self._policy.value,
                    "channel": delivery_request.channel.value,
                    "providerName": transport_adapter.name,
                    "deliveryRequestId": str(delivery_request.request_id),
                    "capability": (
                        validation.capability.value
                        if validation.capability is not None
                        else None
                    ),
                    **dict(delivery_request.metadata),
                }
            ),
        )

        logger.debug(
            "ProviderExecutor prepared ProviderExecutionRequest (no send)",
            extra={
                "extra_fields": {
                    "executionId": str(request.execution_id),
                    "deliveryRequestId": str(delivery_request.request_id),
                    "providerName": transport_adapter.name,
                    "channel": delivery_request.channel.value,
                    "policy": self._policy.value,
                }
            },
        )
        return request, result
