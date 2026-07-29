"""In-process JWKS cache (TASK-PLATFORM-SECMIG-P2-001).

Fetches the IdP JWKS document and caches keys by ``kid``. Refresh occurs on
cache miss / TTL expiry only (fail-closed if the key remains unknown).
"""

from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any

import jwt
from jwt.algorithms import RSAAlgorithm

JwksFetcher = Callable[[str], dict[str, Any]]


def _default_fetch_jwks(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, method="GET", headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=5) as response:  # noqa: S310 — URL from config
            body = response.read()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise ValueError(f"JWKS fetch failed: {exc}") from exc
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("JWKS response is not valid JSON") from exc
    if not isinstance(payload, dict) or "keys" not in payload:
        raise ValueError("JWKS response missing keys array")
    return payload


class JwksCache:
    """Thread-safe JWKS key cache keyed by ``kid``."""

    def __init__(
        self,
        jwks_url: str,
        *,
        ttl_seconds: int = 600,
        fetcher: JwksFetcher | None = None,
    ) -> None:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        self._jwks_url = jwks_url
        self._ttl_seconds = ttl_seconds
        self._fetcher = fetcher or _default_fetch_jwks
        self._lock = threading.RLock()
        self._keys: dict[str, Any] = {}
        self._expires_at = 0.0
        self._fetch_count = 0

    @property
    def fetch_count(self) -> int:
        return self._fetch_count

    def get_key(self, kid: str) -> Any:
        """Return a PyJWT-compatible signing key for ``kid`` (fail-closed)."""
        if not kid:
            raise ValueError("JWT header missing kid")
        with self._lock:
            now = time.monotonic()
            if kid in self._keys and now < self._expires_at:
                return self._keys[kid]
            self._refresh_locked()
            key = self._keys.get(kid)
            if key is None:
                raise ValueError(f"Unknown kid '{kid}'")
            return key

    def clear(self) -> None:
        with self._lock:
            self._keys.clear()
            self._expires_at = 0.0

    def _refresh_locked(self) -> None:
        document = self._fetcher(self._jwks_url)
        keys_raw = document.get("keys")
        if not isinstance(keys_raw, list):
            raise ValueError("JWKS keys must be a list")
        parsed: dict[str, Any] = {}
        for entry in keys_raw:
            if not isinstance(entry, dict):
                continue
            kid = entry.get("kid")
            if not kid or not isinstance(kid, str):
                continue
            kty = entry.get("kty")
            if kty != "RSA":
                continue
            try:
                parsed[kid] = RSAAlgorithm.from_jwk(json.dumps(entry))
            except (ValueError, TypeError, jwt.InvalidKeyError):
                continue
        if not parsed:
            raise ValueError("JWKS contained no usable RSA keys")
        self._keys = parsed
        self._expires_at = time.monotonic() + self._ttl_seconds
        self._fetch_count += 1
