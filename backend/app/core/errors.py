"""API error hierarchy → standard error envelope {code, message, details?}."""

from __future__ import annotations

from typing import Any

from app.core.user_messages import code_message


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

    def __init__(self, message: str | None = None) -> None:
        super().__init__(
            401, "UNAUTHENTICATED", message or code_message("UNAUTHENTICATED")
        )


class ForbiddenError(ApiError):
    """HTTP 403 — caller is authenticated but not allowed.

    Prefer :class:`PermissionDeniedError` or :class:`DataScopeDeniedError`
    for Authorization Middleware (TASK-040). ``FORBIDDEN`` remains the
    permission-denial envelope code for backward compatibility.
    """

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str = "FORBIDDEN",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            403, code, message or code_message(code), details
        )


class PermissionDeniedError(ForbiddenError):
    """HTTP 403 — missing permission or role (Authorization pipeline)."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message or code_message("FORBIDDEN"),
            code="FORBIDDEN",
            details=details,
        )


class DataScopeDeniedError(ForbiddenError):
    """HTTP 403 — effective data scope does not satisfy the check."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message or code_message("DATA_SCOPE_DENIED"),
            code="DATA_SCOPE_DENIED",
            details=details,
        )


class OrgScopeDeniedError(ForbiddenError):
    """HTTP 403 — principal org unit does not match resource org unit (SECMIG-P4)."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message or code_message("ORG_SCOPE_DENIED"),
            code="ORG_SCOPE_DENIED",
            details=details,
        )


class NotFoundError(ApiError):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(404, "NOT_FOUND", message or code_message("NOT_FOUND"))


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


class RateLimitedError(ApiError):
    """HTTP 429 — caller exceeded a temporary rate / lockout limit."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            429,
            "RATE_LIMITED",
            message or code_message("RATE_LIMITED"),
            details,
        )
