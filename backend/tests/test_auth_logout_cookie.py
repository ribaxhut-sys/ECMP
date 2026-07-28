"""UAT-019: logout must clear refresh cookie on the returned Response.

These tests do not require PostgreSQL — they exercise the router helpers
and endpoint return path directly.
"""

from __future__ import annotations

from unittest.mock import MagicMock

from starlette.requests import Request
from starlette.responses import Response

from app.core.config import get_settings
from app.modules.auth.router import (
    _clear_refresh_cookie,
    _set_refresh_cookie,
    logout,
)


def _request_with_refresh_cookie(raw: str | None) -> Request:
    settings = get_settings()
    headers: list[tuple[bytes, bytes]] = []
    if raw is not None:
        headers.append(
            (b"cookie", f"{settings.refresh_cookie_name}={raw}".encode())
        )
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/api/v1/auth/logout",
        "raw_path": b"/api/v1/auth/logout",
        "query_string": b"",
        "headers": headers,
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
    }
    return Request(scope)


def _set_cookie_header(response: Response) -> str | None:
    # Starlette stores set-cookie as a raw header list entry.
    values = response.headers.getlist("set-cookie")
    if values:
        return values[0]
    return response.headers.get("set-cookie")


def test_clear_refresh_cookie_matches_set_cookie_attributes() -> None:
    settings = get_settings()
    set_response = Response()
    clear_response = Response()

    _set_refresh_cookie(set_response, raw_token="opaque-token", settings=settings)
    _clear_refresh_cookie(clear_response, settings=settings)

    set_header = _set_cookie_header(set_response)
    clear_header = _set_cookie_header(clear_response)
    assert set_header is not None
    assert clear_header is not None

    assert clear_header.startswith(f"{settings.refresh_cookie_name}=")
    assert f"Path={settings.refresh_cookie_path}" in set_header
    assert f"Path={settings.refresh_cookie_path}" in clear_header
    assert ("HttpOnly" in set_header) == ("HttpOnly" in clear_header)
    assert ("Secure" in set_header) == ("Secure" in clear_header)
    assert "samesite=lax" in set_header.lower()
    assert "samesite=lax" in clear_header.lower()
    assert "Max-Age=0" in clear_header


def test_logout_returns_same_response_with_deletion_header() -> None:
    """Cookie is cleared on the Response that is actually returned (UAT-019)."""
    settings = get_settings()
    request = _request_with_refresh_cookie("opaque-refresh")
    response = Response()
    service = MagicMock()

    result = logout(request, response, service, settings)

    assert result is response
    assert result.status_code == 204
    service.logout.assert_called_once_with("opaque-refresh")

    header = _set_cookie_header(result)
    assert header is not None
    assert header.startswith(f"{settings.refresh_cookie_name}=")
    assert "Max-Age=0" in header
    assert f"Path={settings.refresh_cookie_path}" in header


def test_logout_idempotent_without_cookie() -> None:
    settings = get_settings()
    request = _request_with_refresh_cookie(None)
    response = Response()
    service = MagicMock()

    first = logout(request, response, service, settings)
    second_response = Response()
    second = logout(request, second_response, service, settings)

    assert first.status_code == 204
    assert second.status_code == 204
    assert _set_cookie_header(first) is not None
    assert _set_cookie_header(second) is not None
    assert service.logout.call_count == 2
