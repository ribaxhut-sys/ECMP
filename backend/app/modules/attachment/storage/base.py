"""Storage provider interface — business logic must not know file locations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageProvider(ABC):
    """Opaque blob storage contract for attachment bytes."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Stable provider identifier persisted on attachment rows."""

    @abstractmethod
    def save(self, *, stored_filename: str, data: bytes) -> str:
        """Persist bytes under a unique stored filename.

        Returns an opaque ``storage_path`` handle for later read/delete.
        ``stored_filename`` must already be unique and path-safe (no separators).
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
        """Best-effort physical delete (optional for soft-deleted records)."""
