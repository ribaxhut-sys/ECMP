"""Provider Executor Foundation package (TASK-059).

Generic execution layer between TransportSelector and future ProviderAdapters.
Prepares execution contracts only. Never sends. Never invokes providers.
"""

from app.modules.provider_executor.executor import ProviderExecutor
from app.modules.provider_executor.models import (
    ProviderExecutionPolicy,
    ProviderExecutionRequest,
    ProviderExecutionResult,
    freeze_mapping,
)
from app.modules.provider_executor.validator import (
    ProviderExecutionValidation,
    ProviderExecutionValidator,
)

__all__ = [
    "ProviderExecutionPolicy",
    "ProviderExecutionRequest",
    "ProviderExecutionResult",
    "ProviderExecutionValidation",
    "ProviderExecutionValidator",
    "ProviderExecutor",
    "freeze_mapping",
]
