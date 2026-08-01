"""In-memory login brute-force protection (R2-03). No Redis dependency."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass

from app.core.config import Settings
from app.core.errors import RateLimitedError
from app.core.user_messages import m


@dataclass
class _AttemptState:
    failures: int = 0
    locked_until: float = 0.0


class LoginAttemptGuard:
    """Track failed logins per key (typically IP + username) with temporary lockout."""

    def __init__(self, *, max_failures: int, lockout_seconds: int) -> None:
        self.max_failures = max(1, max_failures)
        self.lockout_seconds = max(1, lockout_seconds)
        self._states: dict[str, _AttemptState] = {}
        self._lock = threading.Lock()

    def check(self, key: str) -> None:
        now = time.monotonic()
        with self._lock:
            state = self._states.get(key)
            if state is None:
                return
            if state.locked_until > now:
                retry_after = max(1, int(state.locked_until - now))
                raise RateLimitedError(
                    m("auth.rate_limited_login"),
                    details={"retryAfterSeconds": retry_after},
                )
            if state.locked_until and state.locked_until <= now:
                # Lock expired — reset counter for a fresh window.
                self._states.pop(key, None)

    def record_failure(self, key: str) -> bool:
        """Record a failed attempt. Returns True when this call starts a lockout."""
        now = time.monotonic()
        with self._lock:
            state = self._states.get(key)
            if state is None:
                state = _AttemptState()
                self._states[key] = state
            if state.locked_until > now:
                return False
            state.failures += 1
            if state.failures >= self.max_failures:
                state.locked_until = now + self.lockout_seconds
                return True
            return False

    def reset(self, key: str) -> None:
        with self._lock:
            self._states.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._states.clear()


_guard: LoginAttemptGuard | None = None
_guard_lock = threading.Lock()


def get_login_attempt_guard(settings: Settings) -> LoginAttemptGuard:
    """Process-wide guard sized from current settings (recreated if limits change)."""
    global _guard
    with _guard_lock:
        if (
            _guard is None
            or _guard.max_failures != max(1, settings.login_max_failed_attempts)
            or _guard.lockout_seconds != max(1, settings.login_lockout_seconds)
        ):
            _guard = LoginAttemptGuard(
                max_failures=settings.login_max_failed_attempts,
                lockout_seconds=settings.login_lockout_seconds,
            )
        return _guard


def reset_login_attempt_guard_for_tests() -> None:
    """Clear singleton state between unit tests."""
    global _guard
    with _guard_lock:
        if _guard is not None:
            _guard.clear()
        _guard = None
