"""DeliveryEngine — delivery preparation foundation (TASK-057).

Converts DispatchRequest into DeliveryRequest planning artifacts.
Validates inputs. NEVER sends messages or invokes providers/transports.
"""

from __future__ import annotations

import uuid

from app.core.logging import get_logger
from app.modules.delivery.models import (
    DeliveryContext,
    DeliveryPolicy,
    DeliveryRequest,
    DeliveryResult,
    freeze_mapping,
)
from app.modules.delivery.validator import DeliveryValidator
from app.modules.execution.dispatch_models import DispatchRequest

logger = get_logger(__name__)


class DeliveryEngine:
    """Prepare DeliveryRequest / DeliveryResult. No send, no provider call."""

    def __init__(
        self,
        validator: DeliveryValidator | None = None,
        policy: DeliveryPolicy = DeliveryPolicy.DIRECT,
    ) -> None:
        if policy is not DeliveryPolicy.DIRECT:
            raise ValueError(
                f"Unsupported delivery policy for TASK-057: {policy!r} "
                "(only DIRECT is allowed)"
            )
        self._validator = validator if validator is not None else DeliveryValidator()
        self._policy = policy

    @property
    def policy(self) -> DeliveryPolicy:
        return self._policy

    @property
    def validator(self) -> DeliveryValidator:
        return self._validator

    def prepare(
        self,
        dispatch: DispatchRequest,
    ) -> tuple[DeliveryRequest | None, DeliveryResult]:
        """Validate and build a DeliveryRequest. Never sends or calls providers."""
        validation = self._validator.validate(dispatch)
        result = validation.result

        if (
            not result.success
            or validation.channel is None
            or validation.recipient is None
            or validation.template_id is None
            or validation.payload is None
        ):
            logger.debug(
                "DeliveryEngine rejected delivery plan",
                extra={
                    "extra_fields": {
                        "dispatchTaskId": str(dispatch.task_id)
                        if isinstance(dispatch, DispatchRequest)
                        else None,
                        "reason": result.reason,
                        "providerSelected": result.provider_selected,
                    }
                },
            )
            return None, result

        exec_ctx = dispatch.context
        context = DeliveryContext(
            trace_id=exec_ctx.trace_id,
            correlation_id=exec_ctx.correlation_id,
            tenant_id=exec_ctx.tenant_id,
            user_id=exec_ctx.user_id,
            metadata=freeze_mapping(dict(exec_ctx.metadata)),
        )

        request = DeliveryRequest(
            request_id=uuid.uuid4(),
            dispatch_request_id=dispatch.task_id,
            channel=validation.channel,
            recipient=validation.recipient,
            template_id=validation.template_id,
            payload=freeze_mapping(dict(validation.payload)),
            context=context,
            metadata=freeze_mapping(
                {
                    "runId": str(dispatch.run_id),
                    "taskType": dispatch.task_type,
                    "target": dispatch.target,
                    "policy": self._policy.value,
                }
            ),
        )

        logger.debug(
            "DeliveryEngine prepared DeliveryRequest (no delivery)",
            extra={
                "extra_fields": {
                    "requestId": str(request.request_id),
                    "dispatchRequestId": str(request.dispatch_request_id),
                    "channel": request.channel.value,
                    "policy": self._policy.value,
                }
            },
        )
        return request, result
