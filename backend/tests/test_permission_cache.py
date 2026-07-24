"""Unit tests for IAM cache service (TASK-038 / TASK-041)."""

from __future__ import annotations

import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.modules.iam.permission_cache import (
    IamCacheService,
    PermissionCache,
    UserScopedTtlCache,
    get_iam_cache,
    invalidate_iam_all,
    invalidate_iam_user,
    reset_iam_cache_for_tests,
)


def test_cache_hit() -> None:
    cache = PermissionCache(ttl_seconds=300)
    user_id = uuid.uuid4()
    perms = frozenset({"complaints:read", "kpi:read"})
    cache.set(user_id, perms)
    assert cache.get(user_id) == perms
    stats = cache.stats()
    assert stats.hit == 1
    assert stats.miss == 0
    assert stats.entry_count == 1


def test_cache_miss() -> None:
    cache = PermissionCache(ttl_seconds=300)
    user_id = uuid.uuid4()
    assert cache.get(user_id) is None
    stats = cache.stats()
    assert stats.hit == 0
    assert stats.miss == 1
    assert stats.entry_count == 0


def test_cache_set_get() -> None:
    cache = PermissionCache(ttl_seconds=300)
    user_id = uuid.uuid4()
    perms = frozenset({"complaints:read", "kpi:read"})
    assert cache.get(user_id) is None
    cache.set(user_id, perms)
    assert cache.get(user_id) == perms


def test_cache_invalidate_user() -> None:
    cache = PermissionCache(ttl_seconds=300)
    user_id = uuid.uuid4()
    cache.set(user_id, frozenset({"a"}))
    cache.invalidate(user_id)
    assert cache.get(user_id) is None
    assert cache.stats().invalidated == 1


def test_cache_delete() -> None:
    cache = UserScopedTtlCache[str](ttl_seconds=300)
    user_id = uuid.uuid4()
    cache.set(user_id, "v")
    assert cache.delete(user_id) is True
    assert cache.delete(user_id) is False
    assert cache.get(user_id) is None


def test_cache_invalidate_all() -> None:
    cache = PermissionCache(ttl_seconds=300)
    a = uuid.uuid4()
    b = uuid.uuid4()
    cache.set(a, frozenset({"a"}))
    cache.set(b, frozenset({"b"}))
    removed = cache.invalidate_all()
    assert removed == 2
    assert cache.get(a) is None
    assert cache.get(b) is None
    assert len(cache) == 0
    assert cache.stats().invalidated == 2


def test_cache_expiration() -> None:
    cache = PermissionCache(ttl_seconds=1)
    user_id = uuid.uuid4()
    cache.set(user_id, frozenset({"x"}))
    assert cache.get(user_id) == frozenset({"x"})
    time.sleep(1.05)
    assert cache.get(user_id) is None
    stats = cache.stats()
    assert stats.expired == 1
    assert stats.miss >= 1
    assert stats.entry_count == 0


def test_cleanup_expired() -> None:
    cache = UserScopedTtlCache[int](ttl_seconds=1)
    live = uuid.uuid4()
    stale = uuid.uuid4()
    cache.set(stale, 1)
    time.sleep(1.05)
    cache.set(live, 2)
    removed = cache.cleanup_expired()
    assert removed == 1
    assert cache.get(live) == 2
    assert cache.get(stale) is None
    assert cache.stats().expired == 1


def test_cache_entry_fields() -> None:
    cache = UserScopedTtlCache[str](ttl_seconds=60)
    user_id = uuid.uuid4()
    before = time.monotonic()
    cache.set(user_id, "payload")
    after = time.monotonic()
    with cache._lock:  # noqa: SLF001 — inspect entry for contract test
        entry = cache._store[user_id]
    assert entry.value == "payload"
    assert entry.ttl == 60.0
    assert before <= entry.created_at <= after
    assert entry.expires_at == entry.created_at + entry.ttl


def test_iam_service_invalidate_user_all_namespaces() -> None:
    service = IamCacheService(ttl_seconds=300)
    user_id = uuid.uuid4()
    other = uuid.uuid4()
    service.permissions.set(user_id, frozenset({"p"}))
    service.data_scopes.set(user_id, {"scope": "BRANCH"})
    service.principals.set(user_id, {"id": str(user_id)})
    service.permissions.set(other, frozenset({"q"}))

    service.invalidate(user_id)

    assert service.permissions.get(user_id) is None
    assert service.data_scopes.get(user_id) is None
    assert service.principals.get(user_id) is None
    assert service.permissions.get(other) == frozenset({"q"})


def test_iam_service_invalidate_all_and_stats() -> None:
    service = IamCacheService(ttl_seconds=300)
    service.permissions.set(uuid.uuid4(), frozenset({"a"}))
    service.data_scopes.set(uuid.uuid4(), "scope")
    service.principals.set(uuid.uuid4(), "principal")
    removed = service.invalidate_all()
    assert removed == 3
    stats = service.stats()
    assert stats["permissions"].entry_count == 0
    assert stats["data_scopes"].entry_count == 0
    assert stats["principals"].entry_count == 0
    assert stats["permissions"].invalidated == 1
    assert stats["data_scopes"].invalidated == 1
    assert stats["principals"].invalidated == 1


def test_global_invalidate_helpers() -> None:
    reset_iam_cache_for_tests()
    user_id = uuid.uuid4()
    iam = get_iam_cache()
    iam.permissions.set(user_id, frozenset({"x"}))
    iam.data_scopes.set(user_id, "y")
    invalidate_iam_user(user_id)
    assert iam.permissions.get(user_id) is None
    assert iam.data_scopes.get(user_id) is None

    iam.permissions.set(user_id, frozenset({"z"}))
    iam.data_scopes.set(uuid.uuid4(), "s")
    assert invalidate_iam_all() >= 2
    assert len(iam.permissions) == 0
    assert len(iam.data_scopes) == 0
    reset_iam_cache_for_tests()


def test_concurrent_access() -> None:
    cache = UserScopedTtlCache[int](ttl_seconds=300)
    user_ids = [uuid.uuid4() for _ in range(32)]
    barrier = threading.Barrier(8)
    errors: list[BaseException] = []

    def worker(worker_id: int) -> None:
        try:
            barrier.wait(timeout=5)
            for i in range(100):
                uid = user_ids[(worker_id + i) % len(user_ids)]
                cache.set(uid, worker_id * 1000 + i)
                _ = cache.get(uid)
                if i % 17 == 0:
                    cache.invalidate(uid)
                if i % 41 == 0:
                    cache.cleanup_expired()
            _ = cache.stats()
        except BaseException as exc:  # noqa: BLE001 — collect for assertion
            errors.append(exc)

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(worker, i) for i in range(8)]
        for fut in as_completed(futures):
            fut.result()

    assert not errors
    stats = cache.stats()
    assert stats.hit + stats.miss > 0
    assert stats.entry_count == len(cache)
