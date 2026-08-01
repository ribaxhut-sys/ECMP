"""Database engine and session factory."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def build_connect_args(settings, *, connect_timeout: int = 5) -> dict:
    """psycopg connect args, including optional server-side statement timeout.

    ``DB_STATEMENT_TIMEOUT_MS=0`` (default) leaves the server default in place,
    so behaviour is unchanged unless an operator opts in.
    """
    args: dict = {"connect_timeout": connect_timeout}
    timeout_ms = getattr(settings, "db_statement_timeout_ms", 0) or 0
    if timeout_ms > 0:
        args["options"] = f"-c statement_timeout={timeout_ms}"
    return args


def build_pool_kwargs(settings) -> dict:
    """Pool sizing from settings; defaults reproduce prior SQLAlchemy behaviour."""
    kwargs: dict = {
        "pool_size": getattr(settings, "db_pool_size", 5),
        "max_overflow": getattr(settings, "db_max_overflow", 10),
    }
    recycle = getattr(settings, "db_pool_recycle_seconds", 0) or 0
    # SQLAlchemy uses -1 to mean "never recycle"; 0 in config means the same.
    kwargs["pool_recycle"] = recycle if recycle > 0 else -1
    return kwargs


def get_engine() -> Engine:
    global _engine, _SessionLocal
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            future=True,
            connect_args=build_connect_args(settings),
            **build_pool_kwargs(settings),
        )
        _SessionLocal = sessionmaker(
            bind=_engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            future=True,
        )
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    get_engine()
    assert _SessionLocal is not None
    return _SessionLocal


def get_db_session() -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


def ping_database() -> bool:
    """Return True when the database accepts a simple connection."""
    with get_engine().connect() as connection:
        connection.execute(text("SELECT 1"))
    return True
