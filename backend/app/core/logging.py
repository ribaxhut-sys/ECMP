"""Structured logging configuration (JSON or plaintext)."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Literal

from app.core.secrets import SecretRedactingFilter

LogFormat = Literal["json", "text"]


class JsonLogFormatter(logging.Formatter):
    """Single-line JSON logs for compose / SIEM shipping readiness."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        extra_fields = getattr(record, "extra_fields", None)
        if isinstance(extra_fields, dict) and extra_fields:
            payload["extra"] = extra_fields
        request_id = getattr(record, "request_id", None)
        if request_id:
            payload["requestId"] = request_id
        return json.dumps(payload, ensure_ascii=False, default=str)


def _build_formatter(log_format: LogFormat) -> logging.Formatter:
    if log_format == "json":
        return JsonLogFormatter()
    return logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )


def configure_logging(
    level: str = "INFO",
    *,
    log_format: LogFormat = "json",
) -> None:
    """Configure root logging for the application.

    Default format is JSON (ops / audit readiness). Set ``LOG_FORMAT=text`` for
    local human-readable output. Secret redaction remains active either way.
    """
    root = logging.getLogger()
    secret_filter = SecretRedactingFilter()
    fmt = _build_formatter(log_format)

    if not any(isinstance(f, SecretRedactingFilter) for f in root.filters):
        root.addFilter(secret_filter)

    if root.handlers:
        root.setLevel(level.upper())
        for handler in root.handlers:
            handler.setFormatter(fmt)
            if not any(isinstance(f, SecretRedactingFilter) for f in handler.filters):
                handler.addFilter(secret_filter)
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(fmt)
    handler.addFilter(secret_filter)
    root.addHandler(handler)
    root.setLevel(level.upper())


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_extra(**fields: Any) -> dict[str, Any]:
    """Helper for consistent structured extra fields."""
    return {"extra_fields": fields}
