"""JSON logging formatter tests (Mode A ops readiness)."""

from __future__ import annotations

import json
import logging

from app.core.logging import JsonLogFormatter, configure_logging


def test_json_log_formatter_emits_parseable_object() -> None:
    record = logging.LogRecord(
        name="ecmp.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello %s",
        args=("world",),
        exc_info=None,
    )
    payload = json.loads(JsonLogFormatter().format(record))
    assert payload["level"] == "INFO"
    assert payload["logger"] == "ecmp.test"
    assert payload["message"] == "hello world"
    assert "ts" in payload


def test_configure_logging_json_replaces_formatter_on_existing_handlers() -> None:
    root = logging.getLogger()
    # Ensure at least one handler exists from prior tests / configure_logging.
    configure_logging("INFO", log_format="text")
    configure_logging("INFO", log_format="json")
    assert root.handlers
    assert any(isinstance(h.formatter, JsonLogFormatter) for h in root.handlers)
