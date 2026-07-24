"""Complaint domain errors (CAPABILITY-005).

Pure domain exceptions — no HTTP status codes, no FastAPI, no infrastructure.
Application layer maps these to ``ComplaintApplicationError``.
"""

from __future__ import annotations


class ComplaintDomainError(Exception):
    """Business rule violation inside the Complaint aggregate / lifecycle."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


__all__ = ["ComplaintDomainError"]
