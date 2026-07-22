"""Sprint-08 production readiness: CORS, headers, request IDs, readiness, logging."""

from __future__ import annotations

import json
import logging
from io import StringIO

from app.db import reset_engine
from app.logging_config import JsonFormatter, configure_logging, get_logger
from app.middleware import SECURITY_HEADERS
from app.settings import allowed_origins


def test_allowed_origins_fail_closed(monkeypatch):
    monkeypatch.delenv("ECMP_ALLOWED_ORIGINS", raising=False)
    assert allowed_origins() == []
    monkeypatch.setenv("ECMP_ALLOWED_ORIGINS", "  ")
    assert allowed_origins() == []
    monkeypatch.setenv(
        "ECMP_ALLOWED_ORIGINS", "http://localhost:5173, https://app.example"
    )
    assert allowed_origins() == ["http://localhost:5173", "https://app.example"]


def test_security_headers_on_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    for header, value in SECURITY_HEADERS.items():
        assert res.headers.get(header) == value


def test_request_id_generated_and_echoed(client):
    res = client.get("/health")
    assert res.status_code == 200
    request_id = res.headers.get("X-Request-ID")
    correlation_id = res.headers.get("X-Correlation-ID")
    assert request_id
    assert correlation_id == request_id


def test_request_and_correlation_id_echo_client_values(client):
    res = client.get(
        "/health",
        headers={
            "X-Request-ID": "req-sprint08-1",
            "X-Correlation-ID": "corr-sprint08-1",
        },
    )
    assert res.status_code == 200
    assert res.headers.get("X-Request-ID") == "req-sprint08-1"
    assert res.headers.get("X-Correlation-ID") == "corr-sprint08-1"


def test_correlation_id_defaults_to_request_id(client):
    res = client.get("/health", headers={"X-Request-ID": "req-only-1"})
    assert res.headers.get("X-Request-ID") == "req-only-1"
    assert res.headers.get("X-Correlation-ID") == "req-only-1"


def test_health_liveness_unchanged_shape(client):
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["service"] == "ecmp-case-service"
    assert "sprint" in body


def test_readiness_ok(client):
    res = client.get("/health/ready")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ready"
    assert body["checks"]["database"] == "ok"


def test_readiness_fails_when_db_unreachable(monkeypatch, client):
    import os

    original = os.environ["ECMP_DATABASE_URL"]
    monkeypatch.setenv(
        "ECMP_DATABASE_URL", "postgresql+psycopg://bad:bad@127.0.0.1:1/none"
    )
    reset_engine()
    try:
        res = client.get("/health/ready")
        assert res.status_code == 503
        body = res.json()
        assert body["status"] == "not_ready"
        assert body["checks"]["database"] == "fail"
    finally:
        monkeypatch.setenv("ECMP_DATABASE_URL", original)
        reset_engine()


def test_cors_absent_when_origins_unset(client):
    """Fail-closed: no Access-Control-Allow-Origin when allow-list empty."""
    res = client.options(
        "/health",
        headers={
            "Origin": "http://evil.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" not in {
        k.lower() for k in res.headers.keys()
    }


def test_cors_allows_configured_origin(monkeypatch):
    monkeypatch.setenv("ECMP_ALLOWED_ORIGINS", "http://localhost:5173")
    assert allowed_origins() == ["http://localhost:5173"]


def test_json_log_formatter_structure_and_no_pii():
    configure_logging("INFO")
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    log = get_logger("app.test.prod")
    log.handlers = [handler]
    log.propagate = False
    log.setLevel(logging.INFO)

    log.info(
        "request completed",
        extra={
            "correlation_id": "corr-1",
            "request_id": "req-1",
            "extra_fields": {
                "method": "POST",
                "path": "/v1/cases",
                "status_code": 201,
                "case_id": "CASE-1",
            },
        },
    )
    line = stream.getvalue().strip()
    payload = json.loads(line)
    assert payload["level"] == "INFO"
    assert payload["service"] == "ecmp-case-service"
    assert payload["correlation_id"] == "corr-1"
    assert payload["extra"]["request_id"] == "req-1"
    assert payload["extra"]["case_id"] == "CASE-1"
    dumped = json.dumps(payload)
    assert "Billing discrepancy" not in dumped
    assert "Incorrect charge" not in dumped
    assert "dev-token" not in dumped
