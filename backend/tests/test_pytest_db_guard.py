"""Unit tests for pytest DB safety guard (no Postgres required)."""

from __future__ import annotations

import pytest
from tests.pytest_db_guard import (
    database_name_from_url,
    enforce_pytest_database,
    is_safe_pytest_database,
    replace_database_name_in_url,
)


def test_database_name_from_url_postgres() -> None:
    assert (
        database_name_from_url(
            "postgresql+psycopg://ecmp:secret@localhost:5433/ecmp",
        )
        == "ecmp"
    )


def test_replace_database_name_preserves_credentials() -> None:
    out = replace_database_name_in_url(
        "postgresql+psycopg://ecmp:secret@localhost:5433/ecmp",
        "ecmp_test",
    )
    assert out.endswith("/ecmp_test")
    assert "ecmp:secret@localhost:5433" in out


def test_ecmp_is_not_safe() -> None:
    assert is_safe_pytest_database("ecmp") is False
    assert is_safe_pytest_database("ecmp_test") is True
    assert is_safe_pytest_database("foo_test") is True


def test_enforce_redirects_ecmp_to_ecmp_test() -> None:
    env = {
        "POSTGRES_DB": "ecmp",
        "POSTGRES_HOST": "localhost",
    }
    assert enforce_pytest_database(env) == "ecmp_test"
    assert env["POSTGRES_DB"] == "ecmp_test"


def test_enforce_rewrites_database_url() -> None:
    env = {
        "DATABASE_URL": "postgresql+psycopg://ecmp:x@localhost:5433/ecmp",
    }
    assert enforce_pytest_database(env) == "ecmp_test"
    assert env["DATABASE_URL"].endswith("/ecmp_test")
    assert env["POSTGRES_DB"] == "ecmp_test"


def test_enforce_allows_sqlite() -> None:
    env = {"DATABASE_URL": "sqlite:////tmp/ecmp_test.db"}
    assert enforce_pytest_database(env) == "sqlite"


def test_enforce_rejects_unknown_non_test_name() -> None:
    env = {"POSTGRES_DB": "production_lab"}
    with pytest.raises(RuntimeError, match="non-test database"):
        enforce_pytest_database(env)
