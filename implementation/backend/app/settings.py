"""Environment-based configuration (ADR-007: no secrets in source)."""

from __future__ import annotations

import os


def env() -> str:
    """Deployment environment: dev (default) | sit | uat | prod (ADR-010)."""
    return os.getenv("ECMP_ENV", "dev").lower()


def database_url() -> str:
    # SQLite default keeps local bootstrap zero-dependency; CI/DEV use PostgreSQL (ADR-004).
    return os.getenv("ECMP_DATABASE_URL", "sqlite:///./ecmp_dev.db")


def dev_token() -> str:
    return os.getenv("ECMP_DEV_TOKEN", "dev-token")


def readonly_token() -> str:
    return os.getenv("ECMP_DEV_READONLY_TOKEN", "dev-readonly-token")


def noperm_token() -> str:
    """Principal with no permissions — exercises the documented 403 paths."""
    return os.getenv("ECMP_DEV_NOPERM_TOKEN", "dev-noperm-token")


def dev_endpoints_enabled() -> bool:
    return os.getenv("ECMP_ENABLE_DEV_ENDPOINTS", "false").lower() in {"1", "true", "yes"}


def validate_runtime_config() -> None:
    """Fail fast on unsafe non-dev configuration (ADR-007 gate, enforced in code).

    Outside dev, the static default tokens and dev endpoints are prohibited
    (10 Security and Access Standards / TS-001 §2).
    """
    if env() == "dev":
        return
    problems = []
    if os.getenv("ECMP_DEV_TOKEN") is None:
        problems.append("ECMP_DEV_TOKEN unset (default 'dev-token' prohibited outside dev)")
    if dev_endpoints_enabled():
        problems.append("ECMP_ENABLE_DEV_ENDPOINTS must be off outside dev (TS-001 §2)")
    if problems:
        raise RuntimeError(f"Unsafe configuration for ECMP_ENV={env()}: " + "; ".join(problems))
