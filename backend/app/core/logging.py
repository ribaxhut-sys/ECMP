"""Structured logging configuration."""

from __future__ import annotations

import logging
import sys
from typing import Any

from app.core.secrets import SecretRedactingFilter


def configure_logging(level: str = "INFO") -> None:
    """Configure root logging for the application."""
    root = logging.getLogger()
    secret_filter = SecretRedactingFilter()

    if not any(isinstance(f, SecretRedactingFilter) for f in root.filters):
        root.addFilter(secret_filter)

    if root.handlers:
        root.setLevel(level.upper())
        for handler in root.handlers:
            if not any(isinstance(f, SecretRedactingFilter) for f in handler.filters):
                handler.addFilter(secret_filter)
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
    )
    handler.addFilter(secret_filter)
    root.addHandler(handler)
    root.setLevel(level.upper())


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_extra(**fields: Any) -> dict[str, Any]:
    """Helper for consistent structured extra fields."""
    return {"extra_fields": fields}
