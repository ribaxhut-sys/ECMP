"""User directory integration — read-only (ADR-015; ECMP is not identity SoR)."""

from __future__ import annotations

from app.integrations.directory.local_adapter import LocalUserDirectory
from app.integrations.directory.null_adapter import NullUserDirectory
from app.integrations.directory.provider import UserDirectory

__all__ = [
    "LocalUserDirectory",
    "NullUserDirectory",
    "UserDirectory",
]
