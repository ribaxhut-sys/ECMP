"""Shared pytest fixtures / platform compatibility for backend tests.

On Windows, asyncio defaults to ProactorEventLoop. Async psycopg requires a
SelectorEventLoop; without this policy, Postgres integration tests fail with
psycopg.InterfaceError. Linux/macOS are unaffected (Selector is already default).
"""

from __future__ import annotations

import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
