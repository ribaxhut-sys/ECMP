"""Error envelope coverage for paths OUTSIDE route handlers (TS-001 §2.2).

Unknown routes (404), wrong method (405), and unhandled exceptions (500) must
all return {code, message, details?} — never FastAPI's default {"detail": ...}.
"""

from __future__ import annotations

import subprocess
import sys

from conftest import BACKEND_DIR, HEADERS, VALID_PAYLOAD

from app import service


def _assert_envelope(body: dict, code: str) -> None:
    assert body["code"] == code
    assert "message" in body
    assert "detail" not in body


def test_unknown_route_404_uses_envelope(client):
    res = client.get("/v1/nonexistent", headers=HEADERS)
    assert res.status_code == 404
    _assert_envelope(res.json(), "NOT_FOUND")


def test_method_not_allowed_405_uses_envelope(client):
    res = client.delete("/v1/cases", headers=HEADERS)
    assert res.status_code == 405
    _assert_envelope(res.json(), "METHOD_NOT_ALLOWED")


def test_unhandled_exception_500_uses_envelope(tolerant_client, monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("injected failure")

    monkeypatch.setattr(service, "register_case", boom)
    res = tolerant_client.post("/v1/cases", json=VALID_PAYLOAD, headers=HEADERS)
    assert res.status_code == 500
    body = res.json()
    _assert_envelope(body, "INTERNAL_ERROR")
    # No leakage of exception internals (10 Security standards).
    assert "injected" not in str(body)


def test_dev_endpoints_and_docs_absent_when_flag_off():
    """Default-off guarantee: without the flag, /_dev/* and interactive docs don't exist."""
    code = (
        "import os;"
        "os.environ['ECMP_ENABLE_DEV_ENDPOINTS']='false';"
        "os.environ.setdefault('ECMP_DATABASE_URL','sqlite:///./ecmp_flagcheck.db');"
        "from app.main import app;"
        "paths=[getattr(r,'path','') for r in app.routes];"
        "assert '/_dev/events' not in paths, paths;"
        "assert '/_dev/outbox/drain' not in paths, paths;"
        "assert app.docs_url is None and app.redoc_url is None and app.openapi_url is None"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=BACKEND_DIR,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_docs_urls_are_dev_prefixed_when_flag_on():
    """With the flag on (test env), docs live under the exempted /_dev/ prefix."""
    from app.main import app

    assert app.docs_url == "/_dev/docs"
    assert app.openapi_url == "/_dev/openapi.json"
