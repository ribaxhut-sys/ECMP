"""Delivery Engine Foundation package (TASK-057).

Shared delivery preparation infrastructure.
Converts DispatchRequest → DeliveryRequest. Never sends. Never calls providers.
"""

from app.modules.delivery.engine import DeliveryEngine
from app.modules.delivery.models import (
    DeliveryChannel,
    DeliveryContext,
    DeliveryPolicy,
    DeliveryRequest,
    DeliveryResult,
    freeze_mapping,
)
from app.modules.delivery.validator import DeliveryValidation, DeliveryValidator

__all__ = [
    "DeliveryChannel",
    "DeliveryContext",
    "DeliveryEngine",
    "DeliveryPolicy",
    "DeliveryRequest",
    "DeliveryResult",
    "DeliveryValidation",
    "DeliveryValidator",
    "freeze_mapping",
]
