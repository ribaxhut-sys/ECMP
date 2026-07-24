"""Pluggable ticket-number generators (CAPABILITY-003).

Default format: A001, A002, A003, …
Generators are domain policy — never hardcode in controllers.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class TicketNumberGenerator(Protocol):
    """Replaceable strategy for display ticket numbers."""

    def generate(self, sequence: int) -> str:
        """Return a ticket number for a positive per-queue sequence."""
        ...


class PrefixSequenceTicketNumberGenerator:
    """Prefix + zero-padded sequence (default A001).

    Swappable later (daily reset, branch prefix, etc.) without touching API.
    """

    def __init__(self, *, prefix: str = "A", width: int = 3) -> None:
        token = (prefix or "").strip()
        if not token:
            raise ValueError("ticket number prefix must be a non-empty string")
        if width < 1:
            raise ValueError("ticket number width must be a positive integer")
        self._prefix = token
        self._width = width

    @property
    def prefix(self) -> str:
        return self._prefix

    @property
    def width(self) -> int:
        return self._width

    def generate(self, sequence: int) -> str:
        if not isinstance(sequence, int) or sequence < 1:
            raise ValueError("ticket sequence must be a positive integer")
        return f"{self._prefix}{sequence:0{self._width}d}"


__all__ = [
    "PrefixSequenceTicketNumberGenerator",
    "TicketNumberGenerator",
]
