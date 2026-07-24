"""Map Complaint application errors → ApiError HTTP envelopes (CAPABILITY-004…007)."""

from __future__ import annotations

from typing import NoReturn

from app.core.errors import (
    ApiError,
    ConflictError,
    InvalidStateError,
    NotFoundError,
    ValidationAppError,
)
from app.modules.complaint.application.services.errors import ComplaintApplicationError

_NOT_FOUND = frozenset(
    {
        "COMPLAINT_NOT_FOUND",
        "ASSIGNMENT_NOT_FOUND",
        "ESCALATION_NOT_FOUND",
        "SLA_NOT_FOUND",
        "SLA_POLICY_NOT_FOUND",
    }
)

_INVALID_STATE = frozenset(
    {
        "INVALID_COMPLAINT_STATUS",
        "INVALID_COMPLAINT_TRANSITION",
        "INVALID_RESOLUTION_STATE",
        "RESOLUTION_IMMUTABLE",
        "INVALID_ASSIGNMENT_STATE",
        "NO_ACTIVE_ASSIGNMENT",
        "INVALID_ESCALATION_STATE",
        "NO_CURRENT_ESCALATION",
        "ESCALATION_LEVEL_REGRESSION",
        "INVALID_SLA_STATE",
        "NO_ACTIVE_SLA",
    }
)

_CONFLICT = frozenset({"ACTIVE_ASSIGNMENT_EXISTS", "ACTIVE_SLA_EXISTS"})

_VALIDATION = frozenset(
    {
        "INVALID_PRIORITY",
        "VALIDATION_ERROR",
        "UNSUPPORTED_ASSIGNEE_TYPE",
    }
)


def map_complaint_error(exc: ComplaintApplicationError) -> ApiError:
    """Translate ComplaintApplicationError into platform ApiError."""
    if exc.code in _NOT_FOUND:
        return NotFoundError(exc.message)
    if exc.code in _CONFLICT:
        return ConflictError(exc.message, details={"code": exc.code})
    if exc.code in _INVALID_STATE:
        return InvalidStateError(exc.message, details={"code": exc.code})
    if exc.code in _VALIDATION:
        return ValidationAppError(exc.message, details={"code": exc.code})
    return ValidationAppError(exc.message, details={"code": exc.code})


def raise_as_api_error(exc: ComplaintApplicationError) -> NoReturn:
    """Raise the mapped ApiError (never returns)."""
    raise map_complaint_error(exc) from exc


__all__ = ["map_complaint_error", "raise_as_api_error"]
