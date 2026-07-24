"""ProviderException — abstract base for provider contract failures (TASK-060).

No provider-specific exceptions. Contracts only.
"""

from __future__ import annotations

from abc import ABC
from typing import Any

from app.modules.provider_contract.models import ProviderError, ProviderStatus


class ProviderException(ABC, Exception):
    """Abstract base exception for provider contract failures.

    Concrete provider implementations (future) may subclass this base.
    TASK-060 ships no provider-specific exception types.
    """

    def __init__(
        self,
        message: str,
        *,
        provider_name: str | None = None,
        status: ProviderStatus | None = None,
        error: ProviderError | None = None,
        correlation_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        if type(self) is ProviderException:
            raise TypeError(
                "ProviderException is abstract and cannot be instantiated directly"
            )
        msg = (message or "").strip()
        if not msg:
            raise ValueError("ProviderException message must be a non-empty string")
        super().__init__(msg)
        self.message = msg
        self.provider_name = (
            None if provider_name is None else str(provider_name).strip() or None
        )
        self.status = status
        self.error = error
        self.correlation_id = (
            None
            if correlation_id is None
            else str(correlation_id).strip() or None
        )
        # Reject unexpected side-channel kwargs to keep the contract closed
        if kwargs:
            raise TypeError(
                f"ProviderException does not accept unexpected kwargs: "
                f"{sorted(kwargs.keys())}"
            )

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(message={self.message!r}, "
            f"provider_name={self.provider_name!r}, status={self.status!r})"
        )


__all__ = ["ProviderException"]
