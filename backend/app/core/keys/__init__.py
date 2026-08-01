"""Internal key management foundation (TASK-PLATFORM-SECMIG-P5-003)."""

from __future__ import annotations

from app.core.keys.bootstrap import (
    build_registry_from_settings,
    clear_key_registry,
    configure_key_registry,
    get_key_registry,
)
from app.core.keys.models import (
    PLATFORM_HS256_KID,
    KeyAlgorithm,
    KeyPurpose,
    KeyStatus,
    ManagedKey,
    validate_key_metadata,
)
from app.core.keys.registry import (
    InMemoryKeyRegistry,
    KeyNotFoundError,
    KeyRegistry,
    NoActiveKeyError,
)

__all__ = [
    "PLATFORM_HS256_KID",
    "InMemoryKeyRegistry",
    "KeyAlgorithm",
    "KeyNotFoundError",
    "KeyPurpose",
    "KeyRegistry",
    "KeyStatus",
    "ManagedKey",
    "NoActiveKeyError",
    "build_registry_from_settings",
    "clear_key_registry",
    "configure_key_registry",
    "get_key_registry",
    "validate_key_metadata",
]
