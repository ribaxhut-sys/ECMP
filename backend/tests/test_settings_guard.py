"""RC1 / R2 / R6-03 runtime configuration / secret guard tests."""

from __future__ import annotations

import pytest

from app.core.config import (
    ConfigValidationError,
    Settings,
    collect_runtime_config_issues,
    validate_runtime_config,
)

_STRONG_JWT = "a" * 32
_STRONG_DB_PASSWORD = "S3cure-Db-Pass!"

# Env keys that must not leak from the host/container into constructed Settings.
_ISOLATED_ENV = (
    "ENVIRONMENT",
    "DEBUG",
    "JWT_SECRET_KEY",
    "JWT_ALGORITHM",
    "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
    "JWT_REFRESH_TOKEN_EXPIRE_DAYS",
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_DB",
    "DATABASE_URL",
    "ALLOWED_ORIGINS",
    "ALLOWED_HOSTS",
    "PASSWORD_MIN_LENGTH",
    "PASSWORD_RESET_TOKEN_EXPIRE_MINUTES",
    "PASSWORD_RESET_FRONTEND_BASE_URL",
    "EMAIL_PROVIDER",
    "PGADMIN_DEFAULT_PASSWORD",
    "LOGIN_RATE_LIMIT_ENABLED",
    "LOGIN_MAX_FAILED_ATTEMPTS",
    "LOGIN_LOCKOUT_SECONDS",
)


@pytest.fixture(autouse=True)
def _isolate_settings_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure Settings(**kwargs) is not overridden by process/Compose env."""
    for key in _ISOLATED_ENV:
        monkeypatch.delenv(key, raising=False)


def _settings(**kwargs: object) -> Settings:
    """Construct Settings ignoring dotenv files (Compose-mounted .env)."""
    return Settings(_env_file=None, **kwargs)  # type: ignore[arg-type]


def _prod_ok(**overrides: object) -> Settings:
    values: dict[str, object] = {
        "environment": "production",
        "jwt_secret_key": _STRONG_JWT,
        "postgres_password": _STRONG_DB_PASSWORD,
        "allowed_origins": "https://app.example.com",
        "password_reset_frontend_base_url": "https://app.example.com",
        "email_provider": "noop",
        "debug": False,
    }
    values.update(overrides)
    return _settings(**values)


def test_development_allows_default_secret() -> None:
    settings = _settings(
        environment="development",
        jwt_secret_key="change-me-in-production",
        postgres_password="ecmp",
    )
    validate_runtime_config(settings)


def test_test_environment_treated_as_development_for_guards() -> None:
    settings = _settings(
        environment="test",
        jwt_secret_key="change-me-in-production",
        postgres_password="ecmp",
        email_provider="logging",
    )
    validate_runtime_config(settings)


def test_production_rejects_default_secret() -> None:
    settings = _prod_ok(jwt_secret_key="change-me-in-production")
    with pytest.raises(ConfigValidationError, match="JWT_SECRET_KEY"):
        validate_runtime_config(settings)


def test_production_rejects_short_secret() -> None:
    settings = _prod_ok(
        environment="staging",
        jwt_secret_key="too-short-secret-value",
        allowed_origins="https://app.example.com",
    )
    with pytest.raises(ConfigValidationError, match="JWT_SECRET_KEY"):
        validate_runtime_config(settings)


def test_production_rejects_weak_postgres_password() -> None:
    settings = _prod_ok(postgres_password="ecmp")
    with pytest.raises(ConfigValidationError, match="POSTGRES_PASSWORD"):
        validate_runtime_config(settings)


def test_production_rejects_weak_pgadmin_password_when_set() -> None:
    settings = _prod_ok(pgadmin_default_password="admin")
    with pytest.raises(ConfigValidationError, match="PGADMIN_DEFAULT_PASSWORD"):
        validate_runtime_config(settings)


def test_production_allows_unset_pgadmin_password() -> None:
    settings = _prod_ok(pgadmin_default_password=None)
    validate_runtime_config(settings)


def test_production_rejects_wildcard_cors() -> None:
    settings = _prod_ok(allowed_origins="*")
    with pytest.raises(ConfigValidationError, match="ALLOWED_ORIGINS"):
        validate_runtime_config(settings)


def test_production_accepts_strong_secret() -> None:
    validate_runtime_config(_prod_ok())


def test_production_rejects_localhost_password_reset_url() -> None:
    settings = _prod_ok(password_reset_frontend_base_url="http://localhost:3000")
    with pytest.raises(ConfigValidationError, match="PASSWORD_RESET_FRONTEND_BASE_URL"):
        validate_runtime_config(settings)


def test_production_rejects_localhost_allowed_origins() -> None:
    settings = _prod_ok(
        allowed_origins="http://localhost:3000",
        password_reset_frontend_base_url="http://localhost:3000",
    )
    with pytest.raises(ConfigValidationError, match="ALLOWED_ORIGINS"):
        validate_runtime_config(settings)


def test_production_rejects_http_allowed_origins() -> None:
    settings = _prod_ok(
        allowed_origins="http://app.example.com",
        password_reset_frontend_base_url="http://app.example.com",
    )
    with pytest.raises(ConfigValidationError, match="ALLOWED_ORIGINS"):
        validate_runtime_config(settings)


def test_staging_allows_http_origins_without_localhost() -> None:
    settings = _prod_ok(
        environment="staging",
        allowed_origins="http://staging.example.internal",
        password_reset_frontend_base_url="http://staging.example.internal",
    )
    validate_runtime_config(settings)


def test_production_rejects_logging_email_provider() -> None:
    settings = _prod_ok(email_provider="logging")
    with pytest.raises(ConfigValidationError, match="EMAIL_PROVIDER"):
        validate_runtime_config(settings)


def test_rejects_unknown_email_provider_everywhere() -> None:
    settings = _settings(
        environment="development",
        email_provider="smtp",
    )
    with pytest.raises(ConfigValidationError, match="EMAIL_PROVIDER"):
        validate_runtime_config(settings)


def test_rejects_unsupported_jwt_algorithm() -> None:
    settings = _settings(
        environment="development",
        jwt_algorithm="RS256",
    )
    with pytest.raises(ConfigValidationError, match="JWT_ALGORITHM"):
        validate_runtime_config(settings)


def test_production_rejects_misaligned_reset_and_cors_origins() -> None:
    settings = _prod_ok(
        allowed_origins="https://app.example.com",
        password_reset_frontend_base_url="https://other.example.com",
    )
    with pytest.raises(ConfigValidationError, match="PASSWORD_RESET_FRONTEND_BASE_URL"):
        validate_runtime_config(settings)


def test_collect_issues_reports_variable_problem_and_fix() -> None:
    settings = _prod_ok(jwt_secret_key="change-me-in-production", debug=True)
    issues = collect_runtime_config_issues(settings)
    assert issues
    assert all(issue.variable and issue.problem and issue.suggested_fix for issue in issues)
    assert any(issue.variable == "JWT_SECRET_KEY" for issue in issues)
    assert any(issue.variable == "DEBUG" for issue in issues)


def test_development_allows_logging_email_and_localhost_reset_url() -> None:
    settings = _settings(
        environment="development",
        jwt_secret_key="change-me-in-production",
        postgres_password="ecmp",
        password_reset_frontend_base_url="http://localhost:3000",
        email_provider="logging",
    )
    validate_runtime_config(settings)


def test_docs_disabled_outside_development() -> None:
    assert _settings(environment="development").docs_enabled is True
    assert _settings(environment="test").docs_enabled is True
    assert _settings(environment="staging").docs_enabled is False
    assert _settings(environment="production").docs_enabled is False


def test_refresh_cookie_secure_outside_development() -> None:
    assert _settings(environment="development").refresh_cookie_secure is False
    assert _settings(environment="production").refresh_cookie_secure is True
    assert _settings(environment="production").refresh_cookie_samesite == "lax"
