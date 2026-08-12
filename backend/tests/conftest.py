"""Shared pytest fixtures / platform compatibility for backend tests.

On Windows, asyncio defaults to ProactorEventLoop. Async psycopg requires a
SelectorEventLoop; without this policy, Postgres integration tests fail with
psycopg.InterfaceError. Linux/macOS are unaffected (Selector is already default).

SECMIG-P5-002: secrets must come from env (approved source), never code defaults.
Provide lab placeholders for the test process when unset so create_app() startup
validation continues to succeed.

DB safety: integration tests must not write to the shared lab/public ``ecmp``
database (same instance as pengaduan.layanankami.tech). See ``pytest_db_guard``.
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from tests.pytest_db_guard import enforce_pytest_database

# backend/tests/conftest.py → repo root (compose /.env lives here, not backend/).
_REPO_ROOT = Path(__file__).resolve().parents[2]
_ROOT_ENV = _REPO_ROOT / ".env"
if _ROOT_ENV.is_file():
    # setdefault semantics: do not override explicit CI / shell exports.
    load_dotenv(_ROOT_ENV, override=False)

# Approved test-configuration source (env) — not hardcoded Settings defaults.
os.environ.setdefault("JWT_SECRET_KEY", "change-me-in-production")
if not os.environ.get("DATABASE_URL") and not os.environ.get("POSTGRES_PASSWORD"):
    os.environ.setdefault("POSTGRES_PASSWORD", "ecmp")

# Redirect / refuse shared lab DB before any Settings / engine import.
_EFFECTIVE_TEST_DB = enforce_pytest_database(os.environ)
print(
    f"[pytest] database target locked to {_EFFECTIVE_TEST_DB!r}",
    file=sys.stderr,
)

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
