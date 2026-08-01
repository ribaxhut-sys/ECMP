"""Shared pytest fixtures / platform compatibility for backend tests.

On Windows, asyncio defaults to ProactorEventLoop. Async psycopg requires a
SelectorEventLoop; without this policy, Postgres integration tests fail with
psycopg.InterfaceError. Linux/macOS are unaffected (Selector is already default).

SECMIG-P5-002: secrets must come from env (approved source), never code defaults.
Provide lab placeholders for the test process when unset so create_app() startup
validation continues to succeed.
"""

from __future__ import annotations

import asyncio
import os
import sys

# Approved test-configuration source (env) — not hardcoded Settings defaults.
os.environ.setdefault("JWT_SECRET_KEY", "change-me-in-production")
if not os.environ.get("DATABASE_URL") and not os.environ.get("POSTGRES_PASSWORD"):
    os.environ.setdefault("POSTGRES_PASSWORD", "ecmp")

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
