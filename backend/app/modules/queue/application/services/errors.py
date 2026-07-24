"""Queue application errors (TASK-062). Not HTTP / API envelope errors."""

from __future__ import annotations


class QueueApplicationError(Exception):
    """Domain / application validation failure within Queue BC."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


__all__ = ["QueueApplicationError"]
