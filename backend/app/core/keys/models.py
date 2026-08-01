"""Managed-key metadata models (TASK-PLATFORM-SECMIG-P5-003).

Infrastructure only — does not alter JWT payload or API contracts.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class KeyPurpose(str, Enum):
    """Logical use of a managed key."""

    JWT_HS256_SIGNING = "jwt_hs256_signing"
    JWT_RS256_VERIFY = "jwt_rs256_verify"


class KeyAlgorithm(str, Enum):
    HS256 = "HS256"
    RS256 = "RS256"


class KeyStatus(str, Enum):
    """Lifecycle status for manual rotation (no scheduler)."""

    ACTIVE = "active"
    RETIRED = "retired"
    PENDING = "pending"


# Stable internal kid for the platform HS256 secret from Settings.
# Not written into JWT headers (JWT external behavior unchanged).
PLATFORM_HS256_KID = "ecmp-hs256-v1"


@dataclass(frozen=True, slots=True)
class ManagedKey:
    """One registry entry: metadata plus optional key material."""

    kid: str
    purpose: KeyPurpose
    algorithm: KeyAlgorithm
    status: KeyStatus
    created_at: datetime
    expires_at: datetime | None = None
    material: str | None = None

    def __repr__(self) -> str:
        mat = "***REDACTED***" if (self.material or "").strip() else None
        return (
            "ManagedKey("
            f"kid={self.kid!r}, purpose={self.purpose!r}, "
            f"algorithm={self.algorithm!r}, status={self.status!r}, "
            f"created_at={self.created_at!r}, expires_at={self.expires_at!r}, "
            f"material={mat!r})"
        )

    def metadata_dict(self) -> dict[str, Any]:
        """Public metadata only — never includes material."""
        return {
            "kid": self.kid,
            "purpose": self.purpose.value,
            "algorithm": self.algorithm.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }


def validate_key_metadata(key: ManagedKey) -> None:
    """Raise ``ValueError`` when metadata is incomplete or inconsistent."""
    if not (key.kid or "").strip():
        raise ValueError("kid is required")
    if not isinstance(key.purpose, KeyPurpose):
        raise ValueError("purpose must be a KeyPurpose")
    if not isinstance(key.algorithm, KeyAlgorithm):
        raise ValueError("algorithm must be a KeyAlgorithm")
    if not isinstance(key.status, KeyStatus):
        raise ValueError("status must be a KeyStatus")
    if key.created_at is None:
        raise ValueError("created_at is required")
    if key.expires_at is not None and key.expires_at <= key.created_at:
        raise ValueError("expires_at must be after created_at")

    if key.purpose == KeyPurpose.JWT_HS256_SIGNING:
        if key.algorithm != KeyAlgorithm.HS256:
            raise ValueError("jwt_hs256_signing requires algorithm HS256")
        if key.status == KeyStatus.ACTIVE and not (key.material or "").strip():
            raise ValueError("active HS256 signing key requires material")

    if key.purpose == KeyPurpose.JWT_RS256_VERIFY:
        if key.algorithm != KeyAlgorithm.RS256:
            raise ValueError("jwt_rs256_verify requires algorithm RS256")
