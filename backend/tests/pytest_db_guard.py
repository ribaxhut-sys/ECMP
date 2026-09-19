"""Fail-fast helpers: pytest must never target the shared lab/public database.

The lab host ``pengaduan.layanankami.tech`` and local compose share ``POSTGRES_DB=ecmp``.
Integration tests that create branches/complaints must use ``ecmp_test`` (or another
``*_test`` database / sqlite), not ``ecmp``.
"""

from __future__ import annotations

from urllib.parse import urlparse, urlunparse

# Exact names that are never safe for destructive pytest writes.
_FORBIDDEN_DB_NAMES = frozenset(
    {
        "ecmp",
        "postgres",
        "template0",
        "template1",
    }
)


def database_name_from_url(url: str) -> str | None:
    """Return the path database name from a SQLAlchemy / libpq URL, or None."""
    raw = (url or "").strip()
    if not raw:
        return None
    # SQLAlchemy may use postgresql+psycopg:// — urlparse keeps that as scheme.
    parsed = urlparse(raw)
    if parsed.scheme.startswith("sqlite"):
        return None
    path = (parsed.path or "").lstrip("/")
    if not path:
        return None
    # Ignore query driver args: /dbname?sslmode=...
    return path.split("?", 1)[0].strip() or None


def is_sqlite_url(url: str | None) -> bool:
    return bool(url) and urlparse(url.strip()).scheme.startswith("sqlite")


def is_safe_pytest_database(name: str | None, *, database_url: str | None = None) -> bool:
    """True when the target is clearly a disposable test database."""
    if database_url and is_sqlite_url(database_url):
        return True
    if not name:
        return False
    normalized = name.strip().lower()
    if normalized in _FORBIDDEN_DB_NAMES:
        return False
    if normalized.endswith("_test"):
        return True
    if normalized == "test":
        return True
    return False


def replace_database_name_in_url(url: str, database_name: str) -> str:
    """Swap only the DB name in a Postgres URL; leave credentials/host intact."""
    parsed = urlparse(url.strip())
    if parsed.scheme.startswith("sqlite"):
        return url
    return urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            f"/{database_name}",
            parsed.params,
            parsed.query,
            parsed.fragment,
        )
    )


def resolve_effective_database_name(
    *,
    postgres_db: str | None,
    database_url: str | None,
) -> str | None:
    if database_url and not is_sqlite_url(database_url):
        return database_name_from_url(database_url)
    if postgres_db and postgres_db.strip():
        return postgres_db.strip()
    return None


def enforce_pytest_database(
    environ: dict[str, str],
    *,
    preferred_test_db: str = "ecmp_test",
) -> str:
    """Force env onto a safe test DB; raise if the result is still unsafe.

    Returns the effective database name (or ``sqlite``).
    """
    database_url = (environ.get("DATABASE_URL") or "").strip() or None
    postgres_db = (environ.get("POSTGRES_DB") or "").strip() or None
    current = resolve_effective_database_name(
        postgres_db=postgres_db,
        database_url=database_url,
    )

    if database_url and is_sqlite_url(database_url):
        return "sqlite"

    if is_safe_pytest_database(current, database_url=database_url):
        if current:
            environ["POSTGRES_DB"] = current
        return current or preferred_test_db

    # Auto-redirect only the known shared lab/public name (or unset).
    normalized = (current or "").strip().lower()
    if normalized in _FORBIDDEN_DB_NAMES or not normalized:
        if database_url:
            environ["DATABASE_URL"] = replace_database_name_in_url(
                database_url,
                preferred_test_db,
            )
        environ["POSTGRES_DB"] = preferred_test_db
        return preferred_test_db

    raise RuntimeError(
        "Refusing to run pytest against a non-test database "
        f"{current!r}. Set POSTGRES_DB={preferred_test_db} (or DATABASE_URL "
        f"…/{preferred_test_db}), upgrade that DB with alembic, and retry."
    )
