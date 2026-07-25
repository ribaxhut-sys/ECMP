"""Storage provider interface — physical storage is replaceable."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageProvider(ABC):
    """Opaque blob storage contract for attachment bytes.

    Business / domain code must not know absolute file locations.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Stable provider identifier persisted on attachment rows."""

    @abstractmethod
    def save(self, *, relative_path: str, data: bytes) -> str:
        """Persist bytes under a relative path (e.g. ``yyyy/mm/uuid.ext``).

        Returns the opaque ``storage_path`` handle for later read/delete.
        ``relative_path`` must be path-safe (no traversal).
        """

    @abstractmethod
    def open(self, storage_path: str) -> BinaryIO:
        """Open a readable binary stream for the given storage path."""

    @abstractmethod
    def read(self, storage_path: str) -> bytes:
        """Read all bytes for the given storage path."""

    @abstractmethod
    def exists(self, storage_path: str) -> bool:
        """Return True when the blob exists."""

    @abstractmethod
    def delete(self, storage_path: str) -> None:
        """Best-effort physical delete (optional for logically deleted rows)."""
