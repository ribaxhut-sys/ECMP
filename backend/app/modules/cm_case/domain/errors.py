"""Domain / application error mapping to ECMP ApiError envelope codes."""

from __future__ import annotations

from typing import Any

from app.core.errors import ApiError, InvalidStateError, NotFoundError, ValidationAppError


def validation(message: str, details: dict[str, Any] | None = None) -> ValidationAppError:
    return ValidationAppError(message, details)


def not_found(message: str) -> NotFoundError:
    return NotFoundError(message)


def conflict(code: str, message: str, details: dict[str, Any] | None = None) -> ApiError:
    return ApiError(409, code, message, details)


def invalid_state(message: str, details: dict[str, Any] | None = None) -> InvalidStateError:
    return InvalidStateError(message, details)
