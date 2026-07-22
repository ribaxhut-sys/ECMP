"""Structured JSON logging (TS-OBS-001 §1). No PII in log lines (TS-001 §6)."""

from __future__ import annotations

import json
import logging
import logging.config
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any

SERVICE_NAME = "ecmp-case-service"

request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)
correlation_id_ctx: ContextVar[str | None] = ContextVar("correlation_id", default=None)


class JsonFormatter(logging.Formatter):
    """One JSON object per line — TS-OBS-001 §1."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc)
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z"),
            "level": record.levelname,
            "service": SERVICE_NAME,
            "message": record.getMessage(),
        }
        correlation_id = correlation_id_ctx.get() or getattr(
            record, "correlation_id", None
        )
        if correlation_id:
            payload["correlation_id"] = correlation_id
        request_id = request_id_ctx.get() or getattr(record, "request_id", None)
        if request_id:
            payload.setdefault("extra", {})
            payload["extra"]["request_id"] = request_id
        extra = getattr(record, "extra_fields", None)
        if isinstance(extra, dict) and extra:
            payload.setdefault("extra", {}).update(extra)
        if record.exc_info:
            payload.setdefault("extra", {})["exc_info"] = self.formatException(
                record.exc_info
            )
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: str = "INFO") -> None:
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {"()": "app.logging_config.JsonFormatter"},
            },
            "handlers": {
                "stdout": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "json",
                },
            },
            "root": {"level": level, "handlers": ["stdout"]},
            "loggers": {
                "uvicorn": {"level": level, "handlers": ["stdout"], "propagate": False},
                "uvicorn.error": {
                    "level": level,
                    "handlers": ["stdout"],
                    "propagate": False,
                },
                "uvicorn.access": {
                    "level": level,
                    "handlers": ["stdout"],
                    "propagate": False,
                },
                "app": {"level": level, "handlers": ["stdout"], "propagate": False},
            },
        }
    )


def get_logger(name: str = "app") -> logging.Logger:
    return logging.getLogger(name)
