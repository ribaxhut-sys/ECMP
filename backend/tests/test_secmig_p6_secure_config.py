"""TASK-PLATFORM-SECMIG-P6-001 — Secure Configuration Baseline tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.core.config import (
    ConfigValidationError,
    Settings,
    collect_runtime_config_issues,
    validate_runtime_config,
)

pytestmark = pytest.mark.security

_REPO_ROOT = Path(__file__).resolve().parents[2]
_STRONG_JWT = "a" * 32
_STRONG_DB_PASSWORD = "S3cure-Db-Pass!"
_PROD_OIDC = {
    "ecmp_auth_mode": "jwt",
    "ecmp_env": "shared",
    "oidc_issuer": "https://idp.example.com/realms/ecmp",
    "oidc_audience": "ecmp-api",
    "oidc_jwks_url": (
        "https://idp.example.com/realms/ecmp/protocol/openid-connect/certs"
    ),
}

_ISOLATED_ENV = (
    "ENVIRONMENT",
    "DEBUG",
    "JWT_SECRET_KEY",
    "POSTGRES_PASSWORD",
    "DATABASE_URL",
    "ALLOWED_ORIGINS",
    "PASSWORD_RESET_FRONTEND_BASE_URL",
    "EMAIL_PROVIDER",
    "ECMP_AUTH_MODE",
    "ECMP_ENV",
    "ECMP_ENTERPRISE_MODE",
    "ECMP_LOCAL_CREDENTIAL_AUTH",
    "OIDC_ISSUER",
    "OIDC_AUDIENCE",
    "OIDC_JWKS_URL",
    "PGADMIN_DEFAULT_PASSWORD",
)

_REQUIRED_COMPOSE_AUTH_KEYS = (
    "ECMP_AUTH_MODE",
    "ECMP_ENV",
    "ECMP_LOCAL_CREDENTIAL_AUTH",
    "ECMP_ENTERPRISE_MODE",
    "OIDC_ISSUER",
    "OIDC_AUDIENCE",
    "OIDC_JWKS_URL",
)


@pytest.fixture(autouse=True)
def _isolate_settings_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in _ISOLATED_ENV:
        monkeypatch.delenv(key, raising=False)


def _settings(**kwargs: object) -> Settings:
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
        "ecmp_local_credential_auth": False,
        "ecmp_enterprise_mode": False,
        **_PROD_OIDC,
    }
    values.update(overrides)
    return _settings(**values)


# ---------------------------------------------------------------------------
# Startup validation — staging / production refuse lab AuthN
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("environment", ["staging", "production"])
def test_staging_production_reject_dev_auth_mode(environment: str) -> None:
    settings = _prod_ok(
        environment=environment,
        ecmp_auth_mode="dev",
        ecmp_env="local",
        allowed_origins=(
            "http://staging.example.internal"
            if environment == "staging"
            else "https://app.example.com"
        ),
        password_reset_frontend_base_url=(
            "http://staging.example.internal"
            if environment == "staging"
            else "https://app.example.com"
        ),
    )
    issues = collect_runtime_config_issues(settings)
    assert any(
        i.variable == "ECMP_AUTH_MODE" and "forbidden" in i.problem.lower()
        for i in issues
    )
    with pytest.raises(ConfigValidationError, match="ECMP_AUTH_MODE"):
        validate_runtime_config(settings)


@pytest.mark.parametrize("environment", ["staging", "production"])
def test_staging_production_require_oidc_when_jwt(environment: str) -> None:
    settings = _prod_ok(
        environment=environment,
        oidc_issuer=None,
        oidc_audience=None,
        oidc_jwks_url=None,
        allowed_origins=(
            "http://staging.example.internal"
            if environment == "staging"
            else "https://app.example.com"
        ),
        password_reset_frontend_base_url=(
            "http://staging.example.internal"
            if environment == "staging"
            else "https://app.example.com"
        ),
    )
    variables = {i.variable for i in collect_runtime_config_issues(settings)}
    assert "OIDC_ISSUER" in variables
    assert "OIDC_AUDIENCE" in variables
    assert "OIDC_JWKS_URL" in variables


@pytest.mark.parametrize("environment", ["staging", "production"])
def test_staging_production_accept_jwt_with_oidc(environment: str) -> None:
    settings = _prod_ok(
        environment=environment,
        allowed_origins=(
            "http://staging.example.internal"
            if environment == "staging"
            else "https://app.example.com"
        ),
        password_reset_frontend_base_url=(
            "http://staging.example.internal"
            if environment == "staging"
            else "https://app.example.com"
        ),
    )
    validate_runtime_config(settings)


def test_staging_production_forbid_local_credential_auth() -> None:
    """ADR-014 / K-3 — Mode A password surface must not be a production AuthN path."""
    settings = _prod_ok(ecmp_local_credential_auth=True)
    issues = collect_runtime_config_issues(settings)
    assert any(
        i.variable == "ECMP_LOCAL_CREDENTIAL_AUTH" and "forbidden" in i.problem.lower()
        for i in issues
    )
    with pytest.raises(ConfigValidationError, match="ECMP_LOCAL_CREDENTIAL_AUTH"):
        validate_runtime_config(settings)


def test_enterprise_mode_forbids_local_credential_auth() -> None:
    settings = _settings(
        environment="development",
        jwt_secret_key=_STRONG_JWT,
        postgres_password=_STRONG_DB_PASSWORD,
        ecmp_auth_mode="jwt",
        ecmp_env="local",
        oidc_issuer="https://idp.example.com/realms/ecmp",
        oidc_audience="ecmp-api",
        oidc_jwks_url="https://idp.example.com/realms/ecmp/protocol/openid-connect/certs",
        ecmp_enterprise_mode=True,
        ecmp_local_credential_auth=True,
    )
    issues = collect_runtime_config_issues(settings)
    assert any(i.variable == "ECMP_LOCAL_CREDENTIAL_AUTH" for i in issues)
    with pytest.raises(ConfigValidationError, match="ECMP_LOCAL_CREDENTIAL_AUTH"):
        validate_runtime_config(settings)


def test_enterprise_mode_requires_jwt() -> None:
    settings = _settings(
        environment="development",
        jwt_secret_key=_STRONG_JWT,
        postgres_password=_STRONG_DB_PASSWORD,
        ecmp_auth_mode="dev",
        ecmp_env="local",
        ecmp_enterprise_mode=True,
        ecmp_local_credential_auth=False,
    )
    issues = collect_runtime_config_issues(settings)
    assert any(
        i.variable == "ECMP_AUTH_MODE" and "enterprise" in i.problem.lower()
        for i in issues
    )


def test_development_still_allows_dev_auth_mode() -> None:
    settings = _settings(
        environment="development",
        jwt_secret_key="change-me-in-production",
        postgres_password="ecmp",
        ecmp_auth_mode="dev",
        ecmp_env="local",
    )
    validate_runtime_config(settings)


def test_production_default_auth_mode_fails_without_explicit_jwt() -> None:
    """Simulate missing compose injection → Settings default ECMP_AUTH_MODE=dev."""
    settings = _settings(
        environment="production",
        jwt_secret_key=_STRONG_JWT,
        postgres_password=_STRONG_DB_PASSWORD,
        allowed_origins="https://app.example.com",
        password_reset_frontend_base_url="https://app.example.com",
        email_provider="noop",
        debug=False,
        # defaults: ecmp_auth_mode=dev, no OIDC
    )
    issues = collect_runtime_config_issues(settings)
    variables = {i.variable for i in issues}
    assert "ECMP_AUTH_MODE" in variables
    assert "OIDC_ISSUER" in variables
    assert "OIDC_AUDIENCE" in variables
    assert "OIDC_JWKS_URL" in variables


# ---------------------------------------------------------------------------
# Production smoke — compose + template consistency
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "compose_name",
    ["docker-compose.prod.yml", "docker-compose.prod.nginx.yml"],
)
def test_prod_compose_injects_authn_and_oidc_vars(compose_name: str) -> None:
    path = _REPO_ROOT / compose_name
    text = path.read_text(encoding="utf-8")
    for key in _REQUIRED_COMPOSE_AUTH_KEYS:
        assert f"{key}:" in text, f"{compose_name} missing {key}"
        assert "${" + key + ":?" in text, f"{compose_name} must require {key} via :?"


def test_env_production_example_passes_runtime_validation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Smoke: template values (with strong secrets) validate as production jwt."""
    example = _REPO_ROOT / ".env.production.example"
    assert example.is_file()
    loaded: dict[str, str] = {}
    for raw in example.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        loaded[key.strip()] = value.strip().strip('"').strip("'")

    assert loaded.get("ENVIRONMENT") == "production"
    assert loaded.get("ECMP_AUTH_MODE") == "jwt"
    assert loaded.get("ECMP_ENV") == "shared"
    assert loaded.get("OIDC_ISSUER")
    assert loaded.get("OIDC_AUDIENCE")
    assert loaded.get("OIDC_JWKS_URL")

    # Template placeholders are weak by design — swap for validation smoke only.
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("ECMP_AUTH_MODE", loaded["ECMP_AUTH_MODE"])
    monkeypatch.setenv("ECMP_ENV", loaded["ECMP_ENV"])
    monkeypatch.setenv("OIDC_ISSUER", loaded["OIDC_ISSUER"])
    monkeypatch.setenv("OIDC_AUDIENCE", loaded["OIDC_AUDIENCE"])
    monkeypatch.setenv("OIDC_JWKS_URL", loaded["OIDC_JWKS_URL"])
    monkeypatch.setenv("JWT_SECRET_KEY", _STRONG_JWT)
    monkeypatch.setenv("POSTGRES_PASSWORD", _STRONG_DB_PASSWORD)
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://ecmp.example.com")
    monkeypatch.setenv(
        "PASSWORD_RESET_FRONTEND_BASE_URL", "https://ecmp.example.com"
    )
    monkeypatch.setenv("EMAIL_PROVIDER", "noop")
    monkeypatch.setenv("ECMP_LOCAL_CREDENTIAL_AUTH", "false")
    monkeypatch.setenv("ECMP_ENTERPRISE_MODE", "false")

    settings = Settings(_env_file=None)
    assert settings.ecmp_auth_mode == "jwt"
    assert settings.environment == "production"
    assert settings.ecmp_local_credential_auth is False
    assert settings.ecmp_enterprise_mode is False
    assert settings.oidc_issuer
    assert settings.oidc_audience
    assert settings.oidc_jwks_url
    validate_runtime_config(settings)


def test_docs_mention_secmig_p6_auth_requirements() -> None:
    env_ref = (_REPO_ROOT / "docs" / "deployment" / "ENVIRONMENT_VARIABLE_REFERENCE.md").read_text(
        encoding="utf-8"
    )
    checklist = (_REPO_ROOT / "docs" / "deployment" / "STARTUP_CHECKLIST.md").read_text(
        encoding="utf-8"
    )
    assert "SECMIG-P6-001" in env_ref
    assert "ECMP_AUTH_MODE" in env_ref
    assert "OIDC_ISSUER" in env_ref
    assert "ECMP_AUTH_MODE=jwt" in checklist or "ECMP_AUTH_MODE`=jwt" in checklist
