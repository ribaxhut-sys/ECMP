"""In-process key registry (TASK-PLATFORM-SECMIG-P5-003).

Manual rotation only — no scheduler, Vault, or KMS.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime

from app.core.keys.models import (
    KeyPurpose,
    KeyStatus,
    ManagedKey,
    validate_key_metadata,
)


class KeyNotFoundError(LookupError):
    """Requested kid is not present in the registry."""


class NoActiveKeyError(LookupError):
    """No ACTIVE key exists for the requested purpose."""


class KeyRegistry(ABC):
    """Internal key registry abstraction."""

    @abstractmethod
    def get_active_key(self, purpose: KeyPurpose) -> ManagedKey:
        """Return the single ACTIVE key for ``purpose``."""

    @abstractmethod
    def get_key(self, kid: str) -> ManagedKey:
        """Return a key by ``kid`` regardless of status."""


class InMemoryKeyRegistry(KeyRegistry):
    """Process-local registry with explicit manual rotation helpers."""

    def __init__(self) -> None:
        self._keys: dict[str, ManagedKey] = {}

    def get_active_key(self, purpose: KeyPurpose) -> ManagedKey:
        active = [
            key
            for key in self._keys.values()
            if key.purpose == purpose and key.status == KeyStatus.ACTIVE
        ]
        if not active:
            raise NoActiveKeyError(f"No active key for purpose '{purpose.value}'")
        if len(active) > 1:
            kids = ", ".join(sorted(k.kid for k in active))
            raise RuntimeError(
                f"Multiple active keys for purpose '{purpose.value}': {kids}"
            )
        return active[0]

    def get_key(self, kid: str) -> ManagedKey:
        try:
            return self._keys[kid]
        except KeyError as exc:
            raise KeyNotFoundError(f"Unknown kid '{kid}'") from exc

    def list_keys(self, purpose: KeyPurpose | None = None) -> tuple[ManagedKey, ...]:
        values = self._keys.values()
        if purpose is None:
            return tuple(values)
        return tuple(k for k in values if k.purpose == purpose)

    def register(self, key: ManagedKey) -> None:
        """Insert or replace an entry after metadata validation."""
        validate_key_metadata(key)
        if key.status == KeyStatus.ACTIVE:
            for existing in self._keys.values():
                if (
                    existing.kid != key.kid
                    and existing.purpose == key.purpose
                    and existing.status == KeyStatus.ACTIVE
                ):
                    raise ValueError(
                        f"Purpose '{key.purpose.value}' already has active kid "
                        f"'{existing.kid}'; retire it before activating '{key.kid}'"
                    )
        self._keys[key.kid] = key

    def retire(self, kid: str, *, at: datetime | None = None) -> ManagedKey:
        """Mark a key RETIRED (manual rotation step)."""
        current = self.get_key(kid)
        retired = ManagedKey(
            kid=current.kid,
            purpose=current.purpose,
            algorithm=current.algorithm,
            status=KeyStatus.RETIRED,
            created_at=current.created_at,
            expires_at=at or current.expires_at,
            material=current.material,
        )
        self._keys[kid] = retired
        return retired

    def activate(self, kid: str) -> ManagedKey:
        """Promote ``kid`` to ACTIVE; retire any other ACTIVE key of same purpose."""
        target = self.get_key(kid)
        validate_key_metadata(
            ManagedKey(
                kid=target.kid,
                purpose=target.purpose,
                algorithm=target.algorithm,
                status=KeyStatus.ACTIVE,
                created_at=target.created_at,
                expires_at=target.expires_at,
                material=target.material,
            )
        )
        for other in list(self._keys.values()):
            if (
                other.kid != kid
                and other.purpose == target.purpose
                and other.status == KeyStatus.ACTIVE
            ):
                self.retire(other.kid)
        activated = ManagedKey(
            kid=target.kid,
            purpose=target.purpose,
            algorithm=target.algorithm,
            status=KeyStatus.ACTIVE,
            created_at=target.created_at,
            expires_at=target.expires_at,
            material=target.material,
        )
        self._keys[kid] = activated
        return activated

    def rotate(
        self,
        new_key: ManagedKey,
        *,
        retire_at: datetime | None = None,
    ) -> ManagedKey:
        """Manual rotation: retire current ACTIVE for purpose, then register ``new_key``.

        ``new_key`` must have ``status=ACTIVE``. No scheduler — caller invokes explicitly.
        """
        if new_key.status != KeyStatus.ACTIVE:
            raise ValueError("rotate() requires new_key.status == ACTIVE")
        validate_key_metadata(new_key)
        try:
            current = self.get_active_key(new_key.purpose)
        except NoActiveKeyError:
            current = None
        if current is not None:
            if current.kid == new_key.kid:
                raise ValueError("rotate() new_key.kid must differ from the active kid")
            self.retire(current.kid, at=retire_at or datetime.now(UTC))
        self.register(new_key)
        return new_key
