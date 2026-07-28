"""Process-level runtime readiness flags for operational probes."""

from __future__ import annotations

_startup_complete: bool = False


def mark_startup_complete() -> None:
    """Record that required application startup initialization finished."""
    global _startup_complete
    _startup_complete = True


def mark_startup_incomplete() -> None:
    """Record that the application is shutting down or not yet started."""
    global _startup_complete
    _startup_complete = False


def is_startup_complete() -> bool:
    """Return True when lifespan startup initialization has completed."""
    return _startup_complete
