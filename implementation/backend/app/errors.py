"""Error envelope per OpenAPI contract: Error{code, message, details?}."""

from __future__ import annotations


class ApiError(Exception):
    def __init__(self, status_code: int, code: str, message: str, details: dict | None = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)


class UnauthenticatedError(ApiError):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(401, "UNAUTHENTICATED", message)


class ForbiddenError(ApiError):
    def __init__(self, message: str = "Permission denied"):
        super().__init__(403, "FORBIDDEN", message)


class NotFoundError(ApiError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(404, "NOT_FOUND", message)
