"""Complaint application errors (CAPABILITY-004). Not HTTP / API envelope errors."""

from __future__ import annotations


class ComplaintApplicationError(Exception):
    """Domain / application validation failure within Complaint BC."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


__all__ = ["ComplaintApplicationError"]
