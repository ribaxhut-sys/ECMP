"""Structured logging configuration."""

from __future__ import annotations

import logging
import sys
from typing import Any


def configure_logging(level: str = "INFO") -> None:
    """Configure root logging for the application."""
    root = logging.getLogger()
    if root.handlers:
        root.setLevel(level.upper())
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
    )
    root.addHandler(handler)
    root.setLevel(level.upper())


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_extra(**fields: Any) -> dict[str, Any]:
    """Helper for consistent structured extra fields."""
    return {"extra_fields": fields}
