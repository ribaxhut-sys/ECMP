"""Enumeration protection (CTO D-04) — in-process enforcement for Batch 1."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class _Bucket:
    failures: int = 0
    window_start: float = field(default_factory=time.monotonic)
    blocked_until: float = 0.0
    delay_seconds: float = 0.0


class EnumerationGuard:
    """Per-principal rate limit + progressive delay + block.

    Fail-closed when disabled=False and policy says unavailable is handled by caller.
    """

    def __init__(
        self,
        *,
        max_failures: int = 5,
        window_seconds: float = 60.0,
        block_seconds: float = 30.0,
    ) -> None:
        self._max_failures = max_failures
        self._window_seconds = window_seconds
        self._block_seconds = block_seconds
        self._buckets: dict[str, _Bucket] = {}
        self._lock = Lock()
        self.enabled = True

    def reset(self) -> None:
        with self._lock:
            self._buckets.clear()

    def check(self, principal_key: str) -> tuple[str, float]:
        """Return (outcome, delay_seconds). outcome: allowed|delayed|blocked|alerted."""
        if not self.enabled:
            return "allowed", 0.0
        now = time.monotonic()
        with self._lock:
            bucket = self._buckets.setdefault(principal_key, _Bucket())
            if bucket.blocked_until > now:
                return "blocked", max(0.0, bucket.blocked_until - now)
            if now - bucket.window_start > self._window_seconds:
                bucket.failures = 0
                bucket.window_start = now
                bucket.delay_seconds = 0.0
            if bucket.failures >= self._max_failures:
                bucket.blocked_until = now + self._block_seconds
                return "alerted", self._block_seconds
            if bucket.delay_seconds > 0:
                return "delayed", bucket.delay_seconds
            return "allowed", 0.0

    def record_failure(self, principal_key: str) -> None:
        if not self.enabled:
            return
        with self._lock:
            bucket = self._buckets.setdefault(principal_key, _Bucket())
            now = time.monotonic()
            if now - bucket.window_start > self._window_seconds:
                bucket.failures = 0
                bucket.window_start = now
            bucket.failures += 1
            bucket.delay_seconds = min(8.0, 0.25 * (2 ** max(0, bucket.failures - 1)))
            if bucket.failures >= self._max_failures:
                bucket.blocked_until = now + self._block_seconds

    def record_success(self, principal_key: str) -> None:
        if not self.enabled:
            return
        with self._lock:
            bucket = self._buckets.setdefault(principal_key, _Bucket())
            bucket.failures = 0
            bucket.delay_seconds = 0.0
            bucket.blocked_until = 0.0
