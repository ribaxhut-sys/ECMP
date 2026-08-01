"""Identity masking helpers (shared; not transport-specific)."""

from __future__ import annotations


def mask_identity(value: str) -> str:
    if len(value) <= 4:
        return "****"
    return f"{'*' * (len(value) - 4)}{value[-4:]}"
