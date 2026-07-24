"""In-memory IAM cache service (TASK-041).

Reusable TTL cache for Permission, Data Scope, and optional Principal
namespaces. Process-local only — no Redis.

Public helpers used by TASK-038/039 resolvers remain stable:
  get_permission_cache / get_data_scope_cache / invalidate_iam_user
PermissionCache keeps the same get/set/invalidate/invalidate_all API.
"""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")

DEFAULT_TTL_SECONDS = 5 * 60


@dataclass(frozen=True, slots=True)
class CacheEntry(Generic[T]):
    """Single cache record with absolute timestamps (monotonic clock)."""

    value: T
    created_at: float
    expires_at: float
    ttl: float


@dataclass(frozen=True, slots=True)
class CacheStats:
    """Snapshot of cache counters for one namespace."""

    hit: int
    miss: int
    entry_count: int
    expired: int
    invalidated: int


class UserScopedTtlCache(Generic[T]):
    """Thread-safe in-memory cache keyed by userId with TTL + metrics."""

    def __init__(self, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> None:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        self._ttl_seconds = ttl_seconds
        self._store: dict[uuid.UUID, CacheEntry[T]] = {}
        self._lock = threading.RLock()
        self._hit = 0
        self._miss = 0
        self._expired = 0
        self._invalidated = 0

    @property
    def ttl_seconds(self) -> int:
        return self._ttl_seconds

    def get(self, user_id: uuid.UUID) -> T | None:
        now = time.monotonic()
        with self._lock:
            entry = self._store.get(user_id)
            if entry is None:
                self._miss += 1
                return None
            if entry.expires_at <= now:
                del self._store[user_id]
                self._expired += 1
                self._miss += 1
                return None
            self._hit += 1
            return entry.value

    def set(self, user_id: uuid.UUID, value: T) -> None:
        now = time.monotonic()
        ttl = float(self._ttl_seconds)
        with self._lock:
            self._store[user_id] = CacheEntry(
                value=value,
                created_at=now,
                expires_at=now + ttl,
                ttl=ttl,
            )

    def delete(self, user_id: uuid.UUID) -> bool:
        """Remove one key. Returns True if an entry was present."""
        with self._lock:
            removed = self._store.pop(user_id, None) is not None
            if removed:
                self._invalidated += 1
            return removed

    def invalidate(self, user_id: uuid.UUID) -> None:
        self.delete(user_id)

    def invalidate_all(self) -> int:
        """Clear all entries. Returns number of entries removed."""
        with self._lock:
            count = len(self._store)
            self._store.clear()
            self._invalidated += count
            return count

    def cleanup_expired(self) -> int:
        """Eagerly drop expired entries. Returns number removed."""
        now = time.monotonic()
        with self._lock:
            stale = [
                key
                for key, entry in self._store.items()
                if entry.expires_at <= now
            ]
            for key in stale:
                del self._store[key]
            self._expired += len(stale)
            return len(stale)

    def stats(self) -> CacheStats:
        with self._lock:
            return CacheStats(
                hit=self._hit,
                miss=self._miss,
                entry_count=len(self._store),
                expired=self._expired,
                invalidated=self._invalidated,
            )

    def __len__(self) -> int:
        with self._lock:
            return len(self._store)


DataScopeCache = UserScopedTtlCache  # alias for clarity at call sites


class PermissionCache:
    """Typed facade over UserScopedTtlCache[frozenset[str]].

    Preserves TASK-038 PermissionResolver public API while sharing the
    IAM cache service implementation and metrics.
    """

    def __init__(
        self,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
        *,
        backend: UserScopedTtlCache[frozenset[str]] | None = None,
    ) -> None:
        self._backend = (
            backend
            if backend is not None
            else UserScopedTtlCache[frozenset[str]](ttl_seconds=ttl_seconds)
        )

    @property
    def ttl_seconds(self) -> int:
        return self._backend.ttl_seconds

    @property
    def backend(self) -> UserScopedTtlCache[frozenset[str]]:
        return self._backend

    def get(self, user_id: uuid.UUID) -> frozenset[str] | None:
        return self._backend.get(user_id)

    def set(self, user_id: uuid.UUID, permissions: frozenset[str]) -> None:
        self._backend.set(user_id, frozenset(permissions))

    def delete(self, user_id: uuid.UUID) -> bool:
        return self._backend.delete(user_id)

    def invalidate(self, user_id: uuid.UUID) -> None:
        self._backend.invalidate(user_id)

    def invalidate_all(self) -> int:
        return self._backend.invalidate_all()

    def cleanup_expired(self) -> int:
        return self._backend.cleanup_expired()

    def stats(self) -> CacheStats:
        return self._backend.stats()

    def __len__(self) -> int:
        return len(self._backend)


class IamCacheService:
    """Process-local IAM cache: permissions, data scopes, principals."""

    def __init__(self, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> None:
        self._ttl_seconds = ttl_seconds
        self._permissions = UserScopedTtlCache[frozenset[str]](
            ttl_seconds=ttl_seconds
        )
        self._data_scopes = UserScopedTtlCache[object](ttl_seconds=ttl_seconds)
        self._principals = UserScopedTtlCache[object](ttl_seconds=ttl_seconds)
        self._permission_facade = PermissionCache(backend=self._permissions)

    @property
    def ttl_seconds(self) -> int:
        return self._ttl_seconds

    @property
    def permissions(self) -> PermissionCache:
        return self._permission_facade

    @property
    def data_scopes(self) -> UserScopedTtlCache[object]:
        return self._data_scopes

    @property
    def principals(self) -> UserScopedTtlCache[object]:
        """Optional principal cache namespace (unused by resolvers today)."""
        return self._principals

    def invalidate(self, user_id: uuid.UUID) -> None:
        """Invalidate all IAM namespaces for one user."""
        self._permissions.invalidate(user_id)
        self._data_scopes.invalidate(user_id)
        self._principals.invalidate(user_id)

    def invalidate_all(self) -> int:
        """Invalidate every IAM namespace. Returns total entries removed."""
        return (
            self._permissions.invalidate_all()
            + self._data_scopes.invalidate_all()
            + self._principals.invalidate_all()
        )

    def cleanup_expired(self) -> int:
        return (
            self._permissions.cleanup_expired()
            + self._data_scopes.cleanup_expired()
            + self._principals.cleanup_expired()
        )

    def stats(self) -> dict[str, CacheStats]:
        return {
            "permissions": self._permissions.stats(),
            "data_scopes": self._data_scopes.stats(),
            "principals": self._principals.stats(),
        }


_GLOBAL_IAM_CACHE = IamCacheService()


def get_iam_cache() -> IamCacheService:
    """Process-wide IAM cache service singleton."""
    return _GLOBAL_IAM_CACHE


def get_permission_cache() -> PermissionCache:
    """Process-wide permission cache (TASK-038 compatible)."""
    return _GLOBAL_IAM_CACHE.permissions


def get_data_scope_cache() -> UserScopedTtlCache[object]:
    """Process-wide data-scope cache singleton."""
    return _GLOBAL_IAM_CACHE.data_scopes


def get_principal_cache() -> UserScopedTtlCache[object]:
    """Optional principal cache namespace."""
    return _GLOBAL_IAM_CACHE.principals


def invalidate_iam_user(user_id: uuid.UUID) -> None:
    """Invalidate all IAM user-scoped caches for one user."""
    _GLOBAL_IAM_CACHE.invalidate(user_id)


def invalidate_iam_all() -> int:
    """Invalidate all IAM caches (permissions + scopes + principals)."""
    return _GLOBAL_IAM_CACHE.invalidate_all()


def reset_iam_cache_for_tests(
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
) -> IamCacheService:
    """Replace the process IAM cache service (tests only)."""
    global _GLOBAL_IAM_CACHE
    _GLOBAL_IAM_CACHE = IamCacheService(ttl_seconds=ttl_seconds)
    return _GLOBAL_IAM_CACHE


def reset_permission_cache_for_tests(
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
) -> PermissionCache:
    """Replace the process IAM cache (tests only); return permission facade."""
    return reset_iam_cache_for_tests(ttl_seconds=ttl_seconds).permissions


def reset_data_scope_cache_for_tests(
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
) -> UserScopedTtlCache[object]:
    """Replace the process IAM cache (tests only); return data-scope store."""
    return reset_iam_cache_for_tests(ttl_seconds=ttl_seconds).data_scopes
