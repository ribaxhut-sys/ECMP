"""Unit tests for fixed-window rate limiter."""

from __future__ import annotations

import pytest

from app.core.errors import RateLimitError
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
    with pytest.raises(RateLimitError) as exc:
        limiter.check("ip-b")
    assert exc.value.status_code == 429
    assert exc.value.code == "RATE_LIMITED"
    assert "retryAfterSeconds" in (exc.value.details or {})


def test_rate_limiter_keys_are_independent() -> None:
    limiter = FixedWindowRateLimiter(limit=1, window_seconds=60)
    limiter.check("one")
    limiter.check("two")
    with pytest.raises(RateLimitError):
        limiter.check("one")
