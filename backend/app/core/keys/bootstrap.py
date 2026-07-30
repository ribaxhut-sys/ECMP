"""Bootstrap platform key registry from Settings (TASK-PLATFORM-SECMIG-P5-003)."""

from __future__ import annotations

from datetime import UTC, datetime

from app.core.config import Settings
from app.core.keys.models import (
    PLATFORM_HS256_KID,
    KeyAlgorithm,
    KeyPurpose,
    KeyStatus,
    ManagedKey,
)
from app.core.keys.registry import InMemoryKeyRegistry, KeyRegistry

_registry: KeyRegistry | None = None


def build_registry_from_settings(settings: Settings) -> InMemoryKeyRegistry:
    """Seed registry with the platform HS256 signing secret from Settings.

    RS256 / JWKS verification remains on ``JwksCache`` — unchanged. This registry
    only books the foundation HS256 material for internal key-management APIs.
    """
    registry = InMemoryKeyRegistry()
    secret = (settings.jwt_secret_key or "").strip()
    if secret:
        registry.register(
            ManagedKey(
                kid=PLATFORM_HS256_KID,
                purpose=KeyPurpose.JWT_HS256_SIGNING,
                algorithm=KeyAlgorithm.HS256,
                status=KeyStatus.ACTIVE,
                created_at=datetime.now(UTC),
                expires_at=None,
                material=secret,
            )
        )
    return registry


def configure_key_registry(registry: KeyRegistry) -> KeyRegistry:
    """Install the process-wide registry (call once at startup)."""
    global _registry
    _registry = registry
    return _registry


def get_key_registry() -> KeyRegistry:
    """Return the configured registry; lazy-build from Settings if needed."""
    global _registry
    if _registry is None:
        from app.core.config import get_settings

        _registry = build_registry_from_settings(get_settings())
    return _registry


def clear_key_registry() -> None:
    """Clear process-wide registry (tests / shutdown)."""
    global _registry
    _registry = None
