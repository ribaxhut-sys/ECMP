"""Provider Contract Foundation package (TASK-060).

Reusable response / error / metadata contracts for future providers.
No provider implementations. No network.
"""

from app.modules.provider_contract.exceptions import ProviderException
from app.modules.provider_contract.models import (
    ProviderError,
    ProviderErrorCategory,
    ProviderMetadata,
    ProviderResponse,
    ProviderStatus,
    freeze_mapping,
    freeze_tags,
)

__all__ = [
    "ProviderError",
    "ProviderErrorCategory",
    "ProviderException",
    "ProviderMetadata",
    "ProviderResponse",
    "ProviderStatus",
    "freeze_mapping",
    "freeze_tags",
]
