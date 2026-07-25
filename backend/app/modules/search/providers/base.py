"""CAPABILITY-012 SearchProvider contract — replaceable per aggregate."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

F = TypeVar("F")
R = TypeVar("R")


class SearchProvider(ABC, Generic[F, R]):
    """Read-only search over an aggregate. No mutations."""

    @abstractmethod
    def search(self, filters: F) -> tuple[list[R], int]:
        """Return (page items, total matching rows). Pagination is DB-side."""
