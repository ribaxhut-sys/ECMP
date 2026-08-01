"""Async SQLAlchemy session helpers for ECMP persistence foundation (TASK-063).

Reusable by Queue and future domains. Does not replace the sync session API.
No UnitOfWork. Callers own commit / rollback boundaries.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.db.session import build_connect_args, build_pool_kwargs

_async_engine: AsyncEngine | None = None
_AsyncSessionLocal: async_sessionmaker[AsyncSession] | None = None

# Keep readiness probes under Docker/K8s probe timeouts (compose timeout=5s).
DEFAULT_PING_TIMEOUT_SECONDS = 2.0
_CONNECT_TIMEOUT_SECONDS = 5


def _to_async_url(url: str) -> str:
    """Normalize sync psycopg URL to an async-capable SQLAlchemy URL."""
    if "+psycopg_async" in url or "+asyncpg" in url:
        return url
    if url.startswith("postgresql+psycopg://"):
        return url.replace("postgresql+psycopg://", "postgresql+psycopg_async://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg_async://", 1)
    if url.startswith("sqlite+aiosqlite://") or url.startswith("sqlite+aiosqlite:"):
        return url
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    return url


def _engine_kwargs(url: str) -> dict:
    kwargs: dict = {
        "pool_pre_ping": True,
        "future": True,
    }
    # connect_timeout / pool sizing are libpq + QueuePool concerns; sqlite test
    # URLs use a different pool implementation and must not receive them.
    if "sqlite" not in url:
        settings = get_settings()
        kwargs["connect_args"] = build_connect_args(
            settings,
            connect_timeout=_CONNECT_TIMEOUT_SECONDS,
        )
        # Defaults reproduce prior behaviour; see Settings.db_pool_* (audit).
        kwargs.update(build_pool_kwargs(settings))
    return kwargs


def get_async_engine(url: str | None = None) -> AsyncEngine:
    """Return a process-local AsyncEngine (created once unless ``url`` is given)."""
    global _async_engine, _AsyncSessionLocal
    if url is not None:
        async_url = _to_async_url(url)
        return create_async_engine(async_url, **_engine_kwargs(async_url))
    if _async_engine is None:
        settings = get_settings()
        async_url = _to_async_url(settings.database_url)
        _async_engine = create_async_engine(async_url, **_engine_kwargs(async_url))
        _AsyncSessionLocal = async_sessionmaker(
            bind=_async_engine,
            autoflush=False,
            expire_on_commit=False,
            class_=AsyncSession,
        )
    return _async_engine


def get_async_session_factory(
    url: str | None = None,
) -> async_sessionmaker[AsyncSession]:
    """Return async_sessionmaker bound to the shared (or ad-hoc) engine."""
    if url is not None:
        engine = get_async_engine(url)
        return async_sessionmaker(
            bind=engine,
            autoflush=False,
            expire_on_commit=False,
            class_=AsyncSession,
        )
    get_async_engine()
    assert _AsyncSessionLocal is not None
    return _AsyncSessionLocal


async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an AsyncSession; caller controls commit. Closes on exit."""
    session = get_async_session_factory()()
    try:
        yield session
    finally:
        await session.close()


async def ping_database_async(
    *,
    timeout_seconds: float = DEFAULT_PING_TIMEOUT_SECONDS,
) -> bool:
    """Lightweight async DB connectivity check (`SELECT 1`), timeout-protected."""

    async def _ping() -> None:
        engine = get_async_engine()
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

    try:
        await asyncio.wait_for(_ping(), timeout=timeout_seconds)
        return True
    except Exception:
        return False


async def reset_async_engine() -> None:
    """Dispose cached async engine (tests that change DATABASE_URL)."""
    global _async_engine, _AsyncSessionLocal
    if _async_engine is not None:
        await _async_engine.dispose()
    _async_engine = None
    _AsyncSessionLocal = None


__all__ = [
    "DEFAULT_PING_TIMEOUT_SECONDS",
    "get_async_db_session",
    "get_async_engine",
    "get_async_session_factory",
    "ping_database_async",
    "reset_async_engine",
]
