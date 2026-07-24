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
    """HTTP 401 — caller is not authenticated."""

    def __init__(self, message: str = "Unauthenticated") -> None:
        super().__init__(401, "UNAUTHENTICATED", message)


class ForbiddenError(ApiError):
    """HTTP 403 — caller is authenticated but not allowed.

    Prefer :class:`PermissionDeniedError` or :class:`DataScopeDeniedError`
    for Authorization Middleware (TASK-040). ``FORBIDDEN`` remains the
    permission-denial envelope code for backward compatibility.
    """

    def __init__(
        self,
        message: str = "Permission denied",
        *,
        code: str = "FORBIDDEN",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(403, code, message, details)


class PermissionDeniedError(ForbiddenError):
    """HTTP 403 — missing permission or role (Authorization pipeline)."""

    def __init__(
        self,
        message: str = "Permission denied",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, code="FORBIDDEN", details=details)


class DataScopeDeniedError(ForbiddenError):
    """HTTP 403 — effective data scope does not satisfy the check."""

    def __init__(
        self,
        message: str = "Data scope denied",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, code="DATA_SCOPE_DENIED", details=details)


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
