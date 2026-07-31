"""Simple in-process fixed-window rate limiter (single-instance lab/prod compose)."""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque

from app.core.errors import RateLimitError


class FixedWindowRateLimiter:
    """Allow ``limit`` events per ``window_seconds`` for each key."""

    def __init__(self, *, limit: int, window_seconds: float) -> None:
        if limit < 1:
            raise ValueError("limit must be >= 1")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be > 0")
        self._limit = limit
        self._window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, key: str) -> None:
        now = time.monotonic()
        with self._lock:
            bucket = self._hits[key]
            cutoff = now - self._window
            while bucket and bucket[0] < cutoff:
                bucket.popleft()
            if len(bucket) >= self._limit:
                retry_after = max(1, int(self._window - (now - bucket[0])) + 1)
                raise RateLimitError(
                    "Too many login attempts. Try again later.",
                    details={"retryAfterSeconds": retry_after},
                )
            bucket.append(now)

    def reset(self, key: str | None = None) -> None:
        with self._lock:
            if key is None:
                self._hits.clear()
            else:
                self._hits.pop(key, None)


# Lab/shared single-VM default: 10 attempts / minute / client IP.
login_rate_limiter = FixedWindowRateLimiter(limit=10, window_seconds=60.0)


def client_ip_from_request(request: object) -> str:
    """Best-effort client IP behind Caddy (X-Forwarded-For) or direct socket."""
    headers = getattr(request, "headers", None)
    if headers is not None:
        forwarded = headers.get("x-forwarded-for") or headers.get("X-Forwarded-For")
        if forwarded:
            first = forwarded.split(",")[0].strip()
            if first:
                return first
    client = getattr(request, "client", None)
    host = getattr(client, "host", None) if client is not None else None
    return host or "unknown"
