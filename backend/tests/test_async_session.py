"""Coverage for async session helpers (TASK-PLATFORM-CI-COV-001)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.db import async_session as mod


def _clear_engine_cache() -> None:
    mod._async_engine = None
    mod._AsyncSessionLocal = None


@pytest.fixture(autouse=True)
def _reset_engine_sync() -> None:
    _clear_engine_cache()
    yield
    _clear_engine_cache()


def test_to_async_url_variants() -> None:
    assert (
        mod._to_async_url("postgresql+psycopg://u:p@h/db")
        == "postgresql+psycopg_async://u:p@h/db"
    )
    assert (
        mod._to_async_url("postgresql://u:p@h/db")
        == "postgresql+psycopg_async://u:p@h/db"
    )
    assert mod._to_async_url("postgresql+psycopg_async://u:p@h/db").startswith(
        "postgresql+psycopg_async://"
    )
    assert mod._to_async_url("postgresql+asyncpg://u:p@h/db").startswith(
        "postgresql+asyncpg://"
    )
    assert (
        mod._to_async_url("sqlite:///tmp.db") == "sqlite+aiosqlite:///tmp.db"
    )
    assert mod._to_async_url("sqlite+aiosqlite:///tmp.db").startswith(
        "sqlite+aiosqlite://"
    )
    assert mod._to_async_url("other://x") == "other://x"


def test_engine_kwargs_sqlite_skips_connect_timeout() -> None:
    kwargs = mod._engine_kwargs("sqlite+aiosqlite:///x")
    assert "connect_args" not in kwargs
    assert kwargs["pool_pre_ping"] is True


def test_engine_kwargs_postgres_includes_connect_timeout() -> None:
    kwargs = mod._engine_kwargs("postgresql+psycopg_async://u:p@h/db")
    assert kwargs["connect_args"]["connect_timeout"] == mod._CONNECT_TIMEOUT_SECONDS


def test_get_async_engine_with_explicit_url() -> None:
    fake = MagicMock(name="engine")
    with patch.object(mod, "create_async_engine", return_value=fake) as create:
        eng = mod.get_async_engine("postgresql+psycopg://u:p@h/db")
    assert eng is fake
    create.assert_called_once()
    assert "psycopg_async" in create.call_args.args[0]


def test_get_async_engine_caches_from_settings() -> None:
    fake = MagicMock(name="engine")
    settings = MagicMock()
    settings.database_url = "postgresql+psycopg://u:p@h/db"
    with (
        patch.object(mod, "get_settings", return_value=settings),
        patch.object(mod, "create_async_engine", return_value=fake),
        patch.object(mod, "async_sessionmaker", return_value=MagicMock()),
    ):
        first = mod.get_async_engine()
        second = mod.get_async_engine()
    assert first is fake
    assert second is fake


def test_get_async_session_factory_explicit_url() -> None:
    engine = MagicMock()
    factory = MagicMock(name="factory")
    with (
        patch.object(mod, "get_async_engine", return_value=engine),
        patch.object(mod, "async_sessionmaker", return_value=factory) as maker,
    ):
        result = mod.get_async_session_factory("postgresql+psycopg://u:p@h/db")
    assert result is factory
    maker.assert_called_once()


def test_get_async_session_factory_uses_cached() -> None:
    factory = MagicMock(name="factory")
    mod._AsyncSessionLocal = factory
    mod._async_engine = MagicMock()
    with patch.object(mod, "get_async_engine", return_value=MagicMock()):
        assert mod.get_async_session_factory() is factory


@pytest.mark.asyncio
async def test_get_async_db_session_closes() -> None:
    session = AsyncMock()
    factory = MagicMock(return_value=session)
    with patch.object(mod, "get_async_session_factory", return_value=factory):
        agen = mod.get_async_db_session()
        yielded = await agen.__anext__()
        assert yielded is session
        with pytest.raises(StopAsyncIteration):
            await agen.__anext__()
    session.close.assert_awaited()


@pytest.mark.asyncio
async def test_ping_database_async_success() -> None:
    conn = AsyncMock()
    conn.__aenter__ = AsyncMock(return_value=conn)
    conn.__aexit__ = AsyncMock(return_value=None)
    conn.execute = AsyncMock()
    engine = MagicMock()
    engine.connect.return_value = conn
    with patch.object(mod, "get_async_engine", return_value=engine):
        assert await mod.ping_database_async(timeout_seconds=1.0) is True


@pytest.mark.asyncio
async def test_ping_database_async_failure() -> None:
    with patch.object(mod, "get_async_engine", side_effect=RuntimeError("down")):
        assert await mod.ping_database_async(timeout_seconds=0.1) is False


@pytest.mark.asyncio
async def test_reset_async_engine_disposes() -> None:
    eng = AsyncMock()
    mod._async_engine = eng
    mod._AsyncSessionLocal = MagicMock()
    await mod.reset_async_engine()
    eng.dispose.assert_awaited()
    assert mod._async_engine is None
    assert mod._AsyncSessionLocal is None
