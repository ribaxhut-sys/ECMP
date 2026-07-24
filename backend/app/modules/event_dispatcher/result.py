"""Dispatch result value objects (TASK-046)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HandlerResult:
    """Outcome of invoking a single registered handler."""

    handler_name: str
    success: bool
    error: str | None = None
    exception_type: str | None = None


@dataclass(frozen=True, slots=True)
class DispatchResult:
    """Aggregate outcome of a synchronous ``dispatch`` call.

    One handler failure does not stop remaining handlers; errors are
    collected here instead of being re-raised by default.
    """

    success_count: int
    failed_count: int
    handler_results: tuple[HandlerResult, ...]

    @property
    def ok(self) -> bool:
        """True when every invoked handler succeeded (or none registered)."""
        return self.failed_count == 0
