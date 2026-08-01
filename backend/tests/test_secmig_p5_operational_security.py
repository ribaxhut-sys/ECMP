"""TASK-PLATFORM-SECMIG-P5-005 — Operational security hardening tests."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.datastructures import Headers

from app.core.client_ip import resolve_client_ip
from app.core.config import Settings, get_settings
from app.core.errors import RateLimitedError, UnauthenticatedError
from app.core.operational_security import (
    AUDIT_FLOOD_POLICY,
    RUNTIME_SECURITY_DEFAULTS,
    retry_after_header_value,
)
from app.core.schemas import ErrorResponse
from app.main import create_app
from app.modules.audit.hooks import client_ip
from app.modules.audit.security_events import SecurityEventType

pytestmark = pytest.mark.security

_REPO_ROOT = Path(__file__).resolve().parents[2]
_OPS_DOC = _REPO_ROOT / "docs" / "deployment" / "OPERATIONAL_SECURITY.md"


def _settings(**kwargs: object) -> Settings:
    return Settings(_env_file=None, **kwargs)  # type: ignore[arg-type]


def _request(
    *,
    headers: dict[str, str] | None = None,
    client_host: str | None = "127.0.0.1",
) -> MagicMock:
    req = MagicMock(spec=Request)
    req.headers = Headers(headers or {})
    if client_host is None:
        req.client = None
    else:
        req.client = SimpleNamespace(host=client_host)
    return req


# --- Audit flood policy documentation ---------------------------------------


def test_audit_flood_policy_forbids_sampling_and_async_workers() -> None:
    assert AUDIT_FLOOD_POLICY["sampling"] is False
    assert AUDIT_FLOOD_POLICY["asyncWorkers"] is False
    assert AUDIT_FLOOD_POLICY["semanticsUnchanged"] is True
    assert AUDIT_FLOOD_POLICY["writeMode"] == "synchronous_best_effort"
    assert AUDIT_FLOOD_POLICY["failOpenOnWriteError"] is True
    assert "edge" in str(AUDIT_FLOOD_POLICY["mitigation"]).lower()
    assert "sample" in AUDIT_FLOOD_POLICY["summary"].lower() or (
        AUDIT_FLOOD_POLICY["sampling"] is False
    )


def test_audit_flood_policy_documented_in_ops_doc() -> None:
    assert _OPS_DOC.is_file()
    text = _OPS_DOC.read_text(encoding="utf-8")
    assert "Audit flood" in text or "audit flood" in text.lower()
    assert "Sampling" in text
    assert "No" in text
    assert "async" in text.lower()
    assert "SECMIG-P5-005" in text


def test_security_event_taxonomy_unchanged() -> None:
    """Backward compatibility: P5-004 taxonomy strings remain stable."""
    assert SecurityEventType.LOGIN_FAILED == "security.login_failed"
    assert SecurityEventType.TOKEN_REJECTED == "security.token_rejected"
    assert SecurityEventType.PERMISSION_DENIED == "security.permission_denied"
    assert SecurityEventType.LOCKOUT == "security.lockout"


# --- Retry-After -------------------------------------------------------------


def test_retry_after_header_value_from_details() -> None:
    assert retry_after_header_value({"retryAfterSeconds": 42}) == "42"
    assert retry_after_header_value({"retryAfterSeconds": 3.9}) == "3"
    assert retry_after_header_value({"retryAfterSeconds": 0}) == "0"
    assert retry_after_header_value({"retryAfterSeconds": -1}) is None
    assert retry_after_header_value({"retryAfterSeconds": "30"}) is None
    assert retry_after_header_value({"retryAfterSeconds": True}) is None
    assert retry_after_header_value({}) is None
    assert retry_after_header_value(None) is None


def test_api_error_response_includes_retry_after_header() -> None:
    get_settings.cache_clear()
    app = create_app()

    @app.get("/__p5_005_rate_limited")
    def _rate_limited() -> None:
        raise RateLimitedError(
            "Terlalu banyak percobaan. Coba lagi nanti.",
            details={"retryAfterSeconds": 17, "enumerationOutcome": "blocked"},
        )

    with TestClient(app) as client:
        response = client.get("/__p5_005_rate_limited")

    assert response.status_code == 429
    assert response.headers.get("Retry-After") == "17"
    body = response.json()
    assert body["code"] == "RATE_LIMITED"
    assert body["details"]["retryAfterSeconds"] == 17
    assert body["details"]["enumerationOutcome"] == "blocked"
    # Envelope shape unchanged.
    ErrorResponse.model_validate(body)


def test_api_error_without_retry_after_seconds_omits_header() -> None:
    get_settings.cache_clear()
    app = create_app()

    @app.get("/__p5_005_unauthenticated")
    def _unauth() -> None:
        raise UnauthenticatedError("Autentikasi diperlukan.")

    with TestClient(app) as client:
        response = client.get("/__p5_005_unauthenticated")

    assert response.status_code == 401
    assert "Retry-After" not in response.headers
    assert response.json()["code"] == "UNAUTHENTICATED"


# --- Trusted client IP -------------------------------------------------------


def test_client_ip_ignores_xff_when_trust_disabled() -> None:
    settings = _settings(trust_forwarded_client_ip=False)
    req = _request(
        headers={"x-forwarded-for": "203.0.113.9, 10.0.0.1"},
        client_host="192.0.2.10",
    )
    assert resolve_client_ip(req, settings=settings) == "192.0.2.10"


def test_client_ip_honors_xff_when_trust_enabled() -> None:
    settings = _settings(trust_forwarded_client_ip=True)
    req = _request(
        headers={"x-forwarded-for": "203.0.113.9, 10.0.0.1"},
        client_host="192.0.2.10",
    )
    assert resolve_client_ip(req, settings=settings) == "203.0.113.9"


def test_client_ip_falls_back_to_peer_when_xff_empty() -> None:
    settings = _settings(trust_forwarded_client_ip=True)
    req = _request(headers={"x-forwarded-for": "  , "}, client_host="198.51.100.1")
    assert resolve_client_ip(req, settings=settings) == "198.51.100.1"


def test_hooks_client_ip_uses_shared_trust_boundary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("TRUST_FORWARDED_CLIENT_IP", "false")
    get_settings.cache_clear()
    req = _request(
        headers={"x-forwarded-for": "198.51.100.50"},
        client_host="127.0.0.1",
    )
    assert client_ip(req) == "127.0.0.1"
    get_settings.cache_clear()


def test_trust_forwarded_default_matches_runtime_defaults() -> None:
    settings = _settings()
    assert settings.trust_forwarded_client_ip is False
    assert (
        settings.trust_forwarded_client_ip
        == RUNTIME_SECURITY_DEFAULTS["trust_forwarded_client_ip"]
    )
    assert settings.forwarded_allow_ips == RUNTIME_SECURITY_DEFAULTS["forwarded_allow_ips"]
    assert settings.login_rate_limit_enabled == RUNTIME_SECURITY_DEFAULTS[
        "login_rate_limit_enabled"
    ]
    assert settings.login_max_failed_attempts == RUNTIME_SECURITY_DEFAULTS[
        "login_max_failed_attempts"
    ]
    assert settings.login_lockout_seconds == RUNTIME_SECURITY_DEFAULTS[
        "login_lockout_seconds"
    ]


# --- Backward compatibility --------------------------------------------------


def test_rate_limited_json_body_contract_unchanged() -> None:
    """Existing RATE_LIMITED envelope fields remain present with Retry-After."""
    app = FastAPI()

    @app.exception_handler(RateLimitedError)
    async def _handler(_: Request, exc: RateLimitedError):
        from fastapi.responses import JSONResponse

        from app.core.operational_security import retry_after_header_value

        headers: dict[str, str] = {}
        value = retry_after_header_value(exc.details)
        if value is not None:
            headers["Retry-After"] = value
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
            headers=headers,
        )

    @app.get("/limited")
    def _limited() -> None:
        raise RateLimitedError(
            "Terlalu banyak percobaan masuk. Coba lagi nanti.",
            details={"retryAfterSeconds": 9},
        )

    with TestClient(app) as client:
        response = client.get("/limited")

    assert response.status_code == 429
    assert response.headers["Retry-After"] == "9"
    assert response.json() == {
        "code": "RATE_LIMITED",
        "message": "Terlalu banyak percobaan masuk. Coba lagi nanti.",
        "details": {"retryAfterSeconds": 9},
    }
