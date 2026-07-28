"""RC1 / R2 runtime configuration / secret guard tests."""

from __future__ import annotations

import pytest

from app.core.config import Settings, validate_runtime_config

_STRONG_JWT = "a" * 32
_STRONG_DB_PASSWORD = "S3cure-Db-Pass!"


def test_development_allows_default_secret() -> None:
    settings = Settings(
        environment="development",
        jwt_secret_key="change-me-in-production",
        postgres_password="ecmp",
    )
    validate_runtime_config(settings)


def test_production_rejects_default_secret() -> None:
    settings = Settings(
        environment="production",
        jwt_secret_key="change-me-in-production",
        postgres_password=_STRONG_DB_PASSWORD,
        allowed_origins="https://app.example.com",
        password_reset_frontend_base_url="https://app.example.com",
        email_provider="noop",
        debug=False,
    )
    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        validate_runtime_config(settings)


def test_production_rejects_short_secret() -> None:
    settings = Settings(
        environment="staging",
        jwt_secret_key="too-short-secret-value",
        postgres_password=_STRONG_DB_PASSWORD,
        allowed_origins="https://app.example.com",
        password_reset_frontend_base_url="https://app.example.com",
        email_provider="noop",
        debug=False,
    )
    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        validate_runtime_config(settings)


def test_production_rejects_weak_postgres_password() -> None:
    settings = Settings(
        environment="production",
        jwt_secret_key=_STRONG_JWT,
        postgres_password="ecmp",
        allowed_origins="https://app.example.com",
        password_reset_frontend_base_url="https://app.example.com",
        email_provider="noop",
        debug=False,
    )
    with pytest.raises(RuntimeError, match="POSTGRES_PASSWORD"):
        validate_runtime_config(settings)


def test_production_rejects_weak_pgadmin_password_when_set() -> None:
    settings = Settings(
        environment="production",
        jwt_secret_key=_STRONG_JWT,
        postgres_password=_STRONG_DB_PASSWORD,
        pgadmin_default_password="admin",
        allowed_origins="https://app.example.com",
        password_reset_frontend_base_url="https://app.example.com",
        email_provider="noop",
        debug=False,
    )
    with pytest.raises(RuntimeError, match="PGADMIN_DEFAULT_PASSWORD"):
        validate_runtime_config(settings)


def test_production_allows_unset_pgadmin_password() -> None:
    settings = Settings(
        environment="production",
        jwt_secret_key=_STRONG_JWT,
        postgres_password=_STRONG_DB_PASSWORD,
        pgadmin_default_password=None,
        allowed_origins="https://app.example.com",
        password_reset_frontend_base_url="https://app.example.com",
        email_provider="noop",
        debug=False,
    )
    validate_runtime_config(settings)


def test_production_rejects_wildcard_cors() -> None:
    settings = Settings(
        environment="production",
        jwt_secret_key=_STRONG_JWT,
        postgres_password=_STRONG_DB_PASSWORD,
        allowed_origins="*",
        password_reset_frontend_base_url="https://app.example.com",
        email_provider="noop",
        debug=False,
    )
    with pytest.raises(RuntimeError, match="Wildcard"):
        validate_runtime_config(settings)


def test_production_accepts_strong_secret() -> None:
    settings = Settings(
        environment="production",
        jwt_secret_key=_STRONG_JWT,
        postgres_password=_STRONG_DB_PASSWORD,
        allowed_origins="https://app.example.com",
        password_reset_frontend_base_url="https://app.example.com",
        email_provider="noop",
        debug=False,
    )
    validate_runtime_config(settings)


def test_production_rejects_localhost_password_reset_url() -> None:
    settings = Settings(
        environment="production",
        jwt_secret_key=_STRONG_JWT,
        postgres_password=_STRONG_DB_PASSWORD,
        allowed_origins="https://app.example.com",
        password_reset_frontend_base_url="http://localhost:3000",
        email_provider="noop",
        debug=False,
    )
    with pytest.raises(RuntimeError, match="PASSWORD_RESET_FRONTEND_BASE_URL"):
        validate_runtime_config(settings)


def test_production_rejects_logging_email_provider() -> None:
    settings = Settings(
        environment="production",
        jwt_secret_key=_STRONG_JWT,
        postgres_password=_STRONG_DB_PASSWORD,
        allowed_origins="https://app.example.com",
        password_reset_frontend_base_url="https://app.example.com",
        email_provider="logging",
        debug=False,
    )
    with pytest.raises(RuntimeError, match="EMAIL_PROVIDER"):
        validate_runtime_config(settings)


def test_development_allows_logging_email_and_localhost_reset_url() -> None:
    settings = Settings(
        environment="development",
        jwt_secret_key="change-me-in-production",
        postgres_password="ecmp",
        password_reset_frontend_base_url="http://localhost:3000",
        email_provider="logging",
    )
    validate_runtime_config(settings)


def test_docs_disabled_outside_development() -> None:
    assert Settings(environment="development").docs_enabled is True
    assert Settings(environment="staging").docs_enabled is False
    assert Settings(environment="production").docs_enabled is False
