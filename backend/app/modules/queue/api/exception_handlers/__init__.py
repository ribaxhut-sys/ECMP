"""Map Queue application errors → ApiError HTTP envelopes (TASK-064)."""

from __future__ import annotations

from typing import NoReturn

from app.core.errors import (
    ApiError,
    ConflictError,
    InvalidStateError,
    NotFoundError,
    ValidationAppError,
)
from app.modules.queue.application.services.errors import QueueApplicationError

_NOT_FOUND = frozenset(
    {
        "QUEUE_NOT_FOUND",
        "TICKET_NOT_FOUND",
        "COUNTER_NOT_FOUND",
    }
)

_CONFLICT = frozenset(
    {
        "DUPLICATE_TICKET_NUMBER",
    }
)

_INVALID_STATE = frozenset(
    {
        "QUEUE_CLOSED",
        "QUEUE_PAUSED",
        "INVALID_QUEUE_STATUS",
        "INVALID_TICKET_STATUS",
        "INVALID_TICKET_TRANSITION",
        "TICKET_CANCELLED",
        "TICKET_COMPLETED",
        "TICKET_SKIPPED",
    }
)

_VALIDATION = frozenset(
    {
        "INVALID_QUEUE_POLICY",
        "INVALID_PRIORITY",
        "INVALID_TICKET_SEQUENCE",
    }
)


def map_queue_error(exc: QueueApplicationError) -> ApiError:
    """Translate QueueApplicationError into platform ApiError."""
    if exc.code in _NOT_FOUND:
        return NotFoundError(exc.message)
    if exc.code in _CONFLICT:
        return ConflictError(exc.message, details={"code": exc.code})
    if exc.code in _INVALID_STATE:
        return InvalidStateError(exc.message, details={"code": exc.code})
    if exc.code in _VALIDATION:
        return ValidationAppError(exc.message, details={"code": exc.code})
    return ValidationAppError(exc.message, details={"code": exc.code})


def raise_as_api_error(exc: QueueApplicationError) -> NoReturn:
    """Raise the mapped ApiError (never returns)."""
    raise map_queue_error(exc) from exc


__all__ = ["map_queue_error", "raise_as_api_error"]
