"""Provider Contract Foundation value objects (TASK-060).

Standard response models every future provider must return.
No network. No provider implementations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping


class ProviderStatus(StrEnum):
    """Canonical provider outcome statuses."""

    READY = "READY"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RETRYABLE = "RETRYABLE"
    UNSUPPORTED = "UNSUPPORTED"


class ProviderErrorCategory(StrEnum):
    """Error classification for provider failures (contract-level only)."""

    VALIDATION = "VALIDATION"
    AUTHENTICATION = "AUTHENTICATION"
    AUTHORIZATION = "AUTHORIZATION"
    RATE_LIMIT = "RATE_LIMIT"
    TIMEOUT = "TIMEOUT"
    PROVIDER = "PROVIDER"
    NETWORK = "NETWORK"
    UNSUPPORTED = "UNSUPPORTED"
    UNKNOWN = "UNKNOWN"


def freeze_mapping(data: Mapping[str, Any] | None) -> Mapping[str, Any]:
    """Freeze a mapping for immutable value objects."""
    return MappingProxyType(dict(data or {}))


def freeze_tags(tags: Mapping[str, str] | None) -> Mapping[str, str]:
    """Freeze tag map (string keys/values only)."""
    return MappingProxyType({str(k): str(v) for k, v in dict(tags or {}).items()})


@dataclass(frozen=True, slots=True)
class ProviderError:
    """Immutable provider error contract."""

    code: str
    message: str
    retryable: bool
    category: ProviderErrorCategory | str

    def __post_init__(self) -> None:
        code = (self.code or "").strip()
        message = (self.message or "").strip()
        if not code:
            raise ValueError("ProviderError.code must be a non-empty string")
        if not message:
            raise ValueError("ProviderError.message must be a non-empty string")
        if isinstance(self.category, ProviderErrorCategory):
            category: ProviderErrorCategory | str = self.category
        else:
            token = str(self.category or "").strip().upper()
            if not token:
                raise ValueError("ProviderError.category must be a non-empty string")
            try:
                category = ProviderErrorCategory(token)
            except ValueError:
                category = token
        object.__setattr__(self, "code", code)
        object.__setattr__(self, "message", message)
        object.__setattr__(self, "category", category)
        object.__setattr__(self, "retryable", bool(self.retryable))

    def as_dict(self) -> Mapping[str, object]:
        """Diagnostic serialization (not an HTTP / transport contract)."""
        category = (
            self.category.value
            if isinstance(self.category, ProviderErrorCategory)
            else str(self.category)
        )
        return MappingProxyType(
            {
                "code": self.code,
                "message": self.message,
                "retryable": self.retryable,
                "category": category,
            }
        )


@dataclass(frozen=True, slots=True)
class ProviderMetadata:
    """Immutable provider telemetry / diagnostic metadata."""

    latency_ms: int | None = None
    provider_version: str | None = None
    region: str | None = None
    tags: Mapping[str, str] = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if self.latency_ms is not None:
            if not isinstance(self.latency_ms, int) or isinstance(self.latency_ms, bool):
                raise TypeError("ProviderMetadata.latency_ms must be int | None")
            if self.latency_ms < 0:
                raise ValueError("ProviderMetadata.latency_ms must be >= 0")
        version = (
            None
            if self.provider_version is None
            else str(self.provider_version).strip() or None
        )
        region = None if self.region is None else str(self.region).strip() or None
        object.__setattr__(self, "provider_version", version)
        object.__setattr__(self, "region", region)
        object.__setattr__(self, "tags", freeze_tags(self.tags))

    def as_dict(self) -> Mapping[str, object]:
        """Diagnostic serialization (not an HTTP / transport contract)."""
        return MappingProxyType(
            {
                "latencyMs": self.latency_ms,
                "providerVersion": self.provider_version,
                "region": self.region,
                "tags": dict(self.tags),
            }
        )


@dataclass(frozen=True, slots=True)
class ProviderResponse:
    """Immutable standard provider response. All providers must return this shape."""

    provider_name: str
    status: ProviderStatus
    correlation_id: str
    provider_reference: str | None = None
    error: ProviderError | None = None
    metadata: ProviderMetadata = field(
        default_factory=lambda: ProviderMetadata()
    )

    def __post_init__(self) -> None:
        name = (self.provider_name or "").strip()
        correlation = (self.correlation_id or "").strip()
        if not name:
            raise ValueError("ProviderResponse.provider_name must be a non-empty string")
        if not correlation:
            raise ValueError(
                "ProviderResponse.correlation_id must be a non-empty string"
            )
        if not isinstance(self.status, ProviderStatus):
            raise TypeError(
                f"status must be ProviderStatus, got {type(self.status).__name__}"
            )
        if self.error is not None and not isinstance(self.error, ProviderError):
            raise TypeError(
                f"error must be ProviderError | None, got {type(self.error).__name__}"
            )
        if not isinstance(self.metadata, ProviderMetadata):
            raise TypeError(
                f"metadata must be ProviderMetadata, got {type(self.metadata).__name__}"
            )
        reference = (
            None
            if self.provider_reference is None
            else str(self.provider_reference).strip() or None
        )
        object.__setattr__(self, "provider_name", name)
        object.__setattr__(self, "correlation_id", correlation)
        object.__setattr__(self, "provider_reference", reference)

    def as_dict(self) -> Mapping[str, object]:
        """Diagnostic serialization (not an HTTP / transport contract)."""
        return MappingProxyType(
            {
                "providerName": self.provider_name,
                "status": self.status.value,
                "correlationId": self.correlation_id,
                "providerReference": self.provider_reference,
                "error": None if self.error is None else dict(self.error.as_dict()),
                "metadata": dict(self.metadata.as_dict()),
            }
        )


__all__ = [
    "ProviderError",
    "ProviderErrorCategory",
    "ProviderMetadata",
    "ProviderResponse",
    "ProviderStatus",
    "freeze_mapping",
    "freeze_tags",
]
