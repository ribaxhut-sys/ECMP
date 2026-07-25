"""Unit tests for in-memory login brute-force protection (R2-03)."""

from __future__ import annotations

import pytest

from app.core.errors import RateLimitedError
from app.modules.auth.login_protection import (
    LoginAttemptGuard,
    reset_login_attempt_guard_for_tests,
)


@pytest.fixture(autouse=True)
def _reset_guard() -> None:
    reset_login_attempt_guard_for_tests()
    yield
    reset_login_attempt_guard_for_tests()


def test_lockout_after_max_failures() -> None:
    guard = LoginAttemptGuard(max_failures=3, lockout_seconds=60)
    key = "127.0.0.1:alice"

    guard.check(key)
    guard.record_failure(key)
    guard.record_failure(key)
    guard.check(key)  # still under threshold

    guard.record_failure(key)
    with pytest.raises(RateLimitedError) as exc:
        guard.check(key)

    assert exc.value.status_code == 429
    assert exc.value.code == "RATE_LIMITED"
    assert exc.value.details is not None
    assert exc.value.details["retryAfterSeconds"] >= 1


def test_success_resets_failures() -> None:
    guard = LoginAttemptGuard(max_failures=2, lockout_seconds=60)
    key = "127.0.0.1:bob"

    guard.record_failure(key)
    guard.reset(key)
    guard.record_failure(key)
    guard.check(key)  # one failure after reset — not locked


def test_disabled_path_is_caller_responsibility() -> None:
    """Guard itself always enforces; enable/disable is settings-gated in the router."""
    guard = LoginAttemptGuard(max_failures=1, lockout_seconds=30)
    key = "10.0.0.1:carol"
    guard.record_failure(key)
    with pytest.raises(RateLimitedError):
        guard.check(key)
