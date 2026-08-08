"""Unit tests for fixed-window rate limiter."""

from __future__ import annotations

import pytest

from app.core.errors import RateLimitedError
from app.core.rate_limit import FixedWindowRateLimiter


def test_rate_limiter_allows_within_limit() -> None:
    limiter = FixedWindowRateLimiter(limit=3, window_seconds=60)
    limiter.check("ip-a")
    limiter.check("ip-a")
    limiter.check("ip-a")


def test_rate_limiter_blocks_over_limit() -> None:
    limiter = FixedWindowRateLimiter(limit=2, window_seconds=60)
    limiter.check("ip-b")
    limiter.check("ip-b")
    with pytest.raises(RateLimitedError) as exc:
        limiter.check("ip-b")
    assert exc.value.status_code == 429
    assert exc.value.code == "RATE_LIMITED"
    assert "retryAfterSeconds" in (exc.value.details or {})


def test_rate_limiter_keys_are_independent() -> None:
    limiter = FixedWindowRateLimiter(limit=1, window_seconds=60)
    limiter.check("one")
    limiter.check("two")
    with pytest.raises(RateLimitedError):
        limiter.check("one")


def test_rate_limiter_rejects_invalid_config() -> None:
    with pytest.raises(ValueError):
        FixedWindowRateLimiter(limit=0, window_seconds=60)
    with pytest.raises(ValueError):
        FixedWindowRateLimiter(limit=1, window_seconds=0)


def test_rate_limiter_reset_clears_buckets() -> None:
    limiter = FixedWindowRateLimiter(limit=1, window_seconds=60)
    limiter.check("a")
    with pytest.raises(RateLimitedError):
        limiter.check("a")
    limiter.reset("a")
    limiter.check("a")
    limiter.check("b")
    limiter.reset()
    limiter.check("a")
    limiter.check("b")


def test_rate_limiter_expires_hits_outside_window(monkeypatch: pytest.MonkeyPatch) -> None:
    limiter = FixedWindowRateLimiter(limit=1, window_seconds=10)
    clock = {"now": 100.0}

    def _mono() -> float:
        return clock["now"]

    monkeypatch.setattr("app.core.rate_limit.time.monotonic", _mono)
    limiter.check("k")
    clock["now"] = 111.0
    limiter.check("k")  # prior hit expired


def test_client_ip_from_request_prefers_forwarded_for() -> None:
    from types import SimpleNamespace

    from app.core.rate_limit import client_ip_from_request

    req = SimpleNamespace(
        headers={"x-forwarded-for": " 203.0.113.9, 10.0.0.1 "},
        client=SimpleNamespace(host="127.0.0.1"),
    )
    assert client_ip_from_request(req) == "203.0.113.9"
    req2 = SimpleNamespace(headers={}, client=SimpleNamespace(host="192.0.2.1"))
    assert client_ip_from_request(req2) == "192.0.2.1"
    assert client_ip_from_request(SimpleNamespace()) == "unknown"
