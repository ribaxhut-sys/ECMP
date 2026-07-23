"""API error hierarchy → standard error envelope {code, message, details?}."""

from __future__ import annotations

from typing import Any


class ApiError(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)


class UnauthenticatedError(ApiError):
    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__(401, "UNAUTHENTICATED", message)


class ForbiddenError(ApiError):
    def __init__(self, message: str = "Permission denied") -> None:
        super().__init__(403, "FORBIDDEN", message)


class NotFoundError(ApiError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(404, "NOT_FOUND", message)


class ValidationAppError(ApiError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(400, "VALIDATION_ERROR", message, details)


class InvalidStateError(ApiError):
    """Action not applicable to current resource state — HTTP 409 INVALID_STATE."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(409, "INVALID_STATE", message, details)


class ConflictError(ApiError):
    """Resource conflict (e.g. unique constraint) — HTTP 409 CONFLICT."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(409, "CONFLICT", message, details)
