"""TASK-PLATFORM-SECMIG-P5-002 — Secrets Management tests."""

from __future__ import annotations

import logging
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.core.config import (
    ConfigValidationError,
    Settings,
    collect_runtime_config_issues,
    get_settings,
    validate_runtime_config,
)
from app.core.logging import configure_logging
from app.core.secrets import (
    MANDATORY_SECRET_ENV_VARS,
    REDACTED,
    SECRET_INVENTORY,
    SECRET_ENV_VARS,
    clear_runtime_secrets,
    collect_secret_values,
    redact_connection_string,
    redact_mapping,
    redact_text,
    register_runtime_secrets,
    safe_exception_text,
)
from app.main import create_app

pytestmark = pytest.mark.security

_STRONG_JWT = "a" * 32
_STRONG_DB_PASSWORD = "S3cure-Db-Pass!"
_LAB_JWT = "change-me-in-production"
_LAB_DB = "ecmp"

_ISOLATED_ENV = (
    "ENVIRONMENT",
    "DEBUG",
    "JWT_SECRET_KEY",
    "JWT_ALGORITHM",
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_DB",
    "DATABASE_URL",
    "ALLOWED_ORIGINS",
    "PASSWORD_RESET_FRONTEND_BASE_URL",
    "EMAIL_PROVIDER",
    "PGADMIN_DEFAULT_PASSWORD",
    "ECMP_AUTH_MODE",
    "ECMP_ENV",
    "OIDC_ISSUER",
    "OIDC_AUDIENCE",
    "OIDC_JWKS_URL",
)


@pytest.fixture(autouse=True)
def _isolate_settings_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in _ISOLATED_ENV:
        monkeypatch.delenv(key, raising=False)
    clear_runtime_secrets()
    yield
    clear_runtime_secrets()
    get_settings.cache_clear()


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
        "ecmp_auth_mode": "jwt",
        "ecmp_env": "shared",
        "oidc_issuer": "https://idp.example.com/realms/ecmp",
        "oidc_audience": "ecmp-api",
        "oidc_jwks_url": "https://idp.example.com/realms/ecmp/protocol/openid-connect/certs",
    }
    values.update(overrides)
    return _settings(**values)


# ---------------------------------------------------------------------------
# Inventory + configuration load
# ---------------------------------------------------------------------------


def test_secret_inventory_covers_mandatory_env_vars() -> None:
    assert "JWT_SECRET_KEY" in MANDATORY_SECRET_ENV_VARS
    assert "POSTGRES_PASSWORD" in MANDATORY_SECRET_ENV_VARS
    assert SECRET_ENV_VARS >= MANDATORY_SECRET_ENV_VARS
    assert {item.env_var for item in SECRET_INVENTORY} == SECRET_ENV_VARS
    assert all(item.settings_field for item in SECRET_INVENTORY)


def test_settings_defaults_contain_no_hardcoded_secrets() -> None:
    settings = _settings()
    assert settings.jwt_secret_key == ""
    assert settings.postgres_password == ""
    assert settings.pgadmin_default_password is None


def test_configuration_loads_secrets_from_constructor_env_source() -> None:
    """Approved source simulation: values supplied as env-backed Settings fields."""
    settings = _settings(
        environment="development",
        jwt_secret_key=_LAB_JWT,
        postgres_password=_LAB_DB,
    )
    assert settings.jwt_secret_key == _LAB_JWT
    assert settings.postgres_password == _LAB_DB
    validate_runtime_config(settings)


def test_configuration_loads_from_process_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", _LAB_JWT)
    monkeypatch.setenv("POSTGRES_PASSWORD", _LAB_DB)
    monkeypatch.setenv("ENVIRONMENT", "development")
    get_settings.cache_clear()
    settings = Settings(_env_file=None)
    assert settings.jwt_secret_key == _LAB_JWT
    assert settings.postgres_password == _LAB_DB
    validate_runtime_config(settings)
    get_settings.cache_clear()


# ---------------------------------------------------------------------------
# Startup validation — missing required secret
# ---------------------------------------------------------------------------


def test_missing_jwt_secret_fails_startup_validation() -> None:
    settings = _settings(
        environment="development",
        jwt_secret_key="",
        postgres_password=_LAB_DB,
    )
    with pytest.raises(ConfigValidationError, match="JWT_SECRET_KEY") as exc_info:
        validate_runtime_config(settings)
    message = str(exc_info.value)
    assert _LAB_DB not in message


def test_missing_postgres_password_fails_when_no_database_url() -> None:
    settings = _settings(
        environment="development",
        jwt_secret_key=_LAB_JWT,
        postgres_password="",
        database_url_override=None,
    )
    with pytest.raises(ConfigValidationError, match="POSTGRES_PASSWORD") as exc_info:
        validate_runtime_config(settings)
    assert _LAB_JWT not in str(exc_info.value)


def test_database_url_satisfies_db_secret_without_postgres_password() -> None:
    settings = _settings(
        environment="development",
        jwt_secret_key=_LAB_JWT,
        postgres_password="",
        database_url_override="postgresql+psycopg://ecmp:ci_secret@localhost:5432/ecmp",
    )
    validate_runtime_config(settings)


def test_production_database_url_credentials_skip_postgres_password() -> None:
    """R3: DATABASE_URL with credentials is the effective secret source."""
    settings = _prod_ok(
        postgres_password="",
        database_url_override=(
            f"postgresql+psycopg://ecmp:{_STRONG_DB_PASSWORD}@db.example.com:5432/ecmp"
        ),
    )
    validate_runtime_config(settings)
    issues = collect_runtime_config_issues(settings)
    assert not any(i.variable == "POSTGRES_PASSWORD" for i in issues)


def test_production_weak_password_in_database_url_fails() -> None:
    """R3: strength check evaluates the URL password, not empty POSTGRES_PASSWORD."""
    settings = _prod_ok(
        postgres_password="",
        database_url_override="postgresql+psycopg://ecmp:ecmp@db.example.com:5432/ecmp",
    )
    issues = collect_runtime_config_issues(settings)
    assert any(i.variable == "DATABASE_URL" for i in issues)
    assert not any(i.variable == "POSTGRES_PASSWORD" for i in issues)


def test_production_missing_strong_jwt_still_fails() -> None:
    settings = _prod_ok(jwt_secret_key="")
    issues = collect_runtime_config_issues(settings)
    assert any(i.variable == "JWT_SECRET_KEY" for i in issues)


# ---------------------------------------------------------------------------
# Secrets never appear in logs / errors / dumps
# ---------------------------------------------------------------------------


def test_config_validation_error_omits_secret_values() -> None:
    secret = "UniqueLeakProbeJwtSecretValue9999"
    settings = _prod_ok(jwt_secret_key=secret[:16], postgres_password="ecmp")
    with pytest.raises(ConfigValidationError) as exc_info:
        validate_runtime_config(settings)
    text = str(exc_info.value)
    assert secret[:16] not in text
    for issue in exc_info.value.issues:
        assert secret[:16] not in issue.problem
        assert secret[:16] not in issue.suggested_fix


def test_settings_repr_and_model_dump_redact_secrets() -> None:
    secret = "ReprLeakJwtSecretValue-32chars!!"
    db_secret = "ReprLeakDbPassword99"
    settings = _settings(
        jwt_secret_key=secret,
        postgres_password=db_secret,
    )
    rendered = repr(settings)
    assert secret not in rendered
    assert db_secret not in rendered
    assert REDACTED in rendered

    dumped = settings.model_dump()
    assert dumped["jwt_secret_key"] == REDACTED
    assert dumped["postgres_password"] == REDACTED
    assert db_secret not in dumped["database_url"]
    assert REDACTED in dumped["database_url"]
    # Property access still yields real value for runtime use (JWT / DB)
    assert settings.jwt_secret_key == secret
    assert settings.postgres_password == db_secret


def test_settings_str_redacts_secrets() -> None:
    secret = "StrLeakJwtSecretValue-32chars!!!"
    db_secret = "StrLeakDbPassword99"
    settings = _settings(jwt_secret_key=secret, postgres_password=db_secret)
    rendered = str(settings)
    assert secret not in rendered
    assert db_secret not in rendered
    assert REDACTED in rendered
    assert settings.jwt_secret_key == secret


def test_settings_dict_redacts_secrets() -> None:
    secret = "DictLeakJwtSecretValue-32chars!!"
    db_secret = "DictLeakDbPassword99"
    settings = _settings(jwt_secret_key=secret, postgres_password=db_secret)
    as_dict = dict(settings)
    assert as_dict["jwt_secret_key"] == REDACTED
    assert as_dict["postgres_password"] == REDACTED
    blob = str(as_dict)
    assert secret not in blob
    assert db_secret not in blob
    assert settings.jwt_secret_key == secret


def test_settings_model_dump_json_redacts_secrets() -> None:
    secret = "JsonLeakJwtSecretValue-32chars!!"
    db_secret = "JsonLeakDbPassword99"
    url = f"postgresql+psycopg://ecmp:{db_secret}@db:5432/ecmp"
    settings = _settings(
        jwt_secret_key=secret,
        postgres_password=db_secret,
        database_url_override=url,
    )
    payload = settings.model_dump_json()
    assert secret not in payload
    assert db_secret not in payload
    assert REDACTED in payload


def test_logger_exception_traceback_redacts_secrets() -> None:
    """R1: secrets in exception args must not appear in logger.exception output."""
    import io

    secret = "TbLeakJwtSecretValue-TRACEBACK01"
    db_secret = "TbLeakDbPassTRACE99"
    settings = _settings(
        environment="development",
        jwt_secret_key=secret,
        postgres_password=db_secret,
    )
    register_runtime_secrets(settings)
    configure_logging("INFO")

    buf = io.StringIO()
    handler = logging.StreamHandler(buf)
    handler.setFormatter(logging.Formatter("%(message)s"))
    from app.core.secrets import SecretRedactingFilter

    handler.addFilter(SecretRedactingFilter())
    log = logging.getLogger("secmig.p5.traceback")
    log.handlers.clear()
    log.addHandler(handler)
    log.setLevel(logging.ERROR)
    log.propagate = False
    try:
        try:
            raise RuntimeError(f"connect failed secret={secret} pwd={db_secret}")
        except RuntimeError:
            log.exception("unhandled boom")
    finally:
        log.removeHandler(handler)

    out = buf.getvalue()
    assert "Traceback" in out
    assert secret not in out
    assert db_secret not in out
    assert REDACTED in out


def test_redact_text_and_logs_never_emit_registered_secrets() -> None:
    secret = "LogLeakJwtSecretValue-ABCDEFGH"
    settings = _settings(
        environment="development",
        jwt_secret_key=secret,
        postgres_password="LogLeakDbPass99",
    )
    register_runtime_secrets(settings)
    configure_logging("INFO")

    assert secret not in redact_text(f"using key={secret}")
    assert "LogLeakDbPass99" not in redact_text("pwd=LogLeakDbPass99")

    records: list[str] = []

    class _Capture(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            records.append(record.getMessage())

    root = logging.getLogger()
    capture = _Capture()
    # SecretRedactingFilter already on root handlers from configure_logging
    root.addHandler(capture)
    try:
        logging.getLogger("secmig.p5.test").error("boom secret=%s", secret)
    finally:
        root.removeHandler(capture)

    joined = "\n".join(records)
    assert secret not in joined
    assert REDACTED in joined


def test_safe_exception_text_scrubs_secrets() -> None:
    secret = "ExcLeakJwtSecretValue-XYZ12345"
    settings = _settings(jwt_secret_key=secret, postgres_password="x")
    register_runtime_secrets(settings)
    exc = RuntimeError(f"connect failed with {secret}")
    text = safe_exception_text(exc)
    assert secret not in text
    assert REDACTED in text


def test_redact_mapping_masks_sensitive_keys() -> None:
    payload = {
        "user": "agent",
        "password": "plain",
        "nested": {"jwt_secret_key": "abc", "ok": 1},
    }
    cleaned = redact_mapping(payload)
    assert cleaned["user"] == "agent"
    assert cleaned["password"] == REDACTED
    assert cleaned["nested"]["jwt_secret_key"] == REDACTED
    assert cleaned["nested"]["ok"] == 1


def test_redact_connection_string_masks_password() -> None:
    url = "postgresql+psycopg://ecmp:SuperSecretDb@db:5432/ecmp"
    scrubbed = redact_connection_string(url)
    assert "SuperSecretDb" not in scrubbed
    assert REDACTED in scrubbed
    assert scrubbed.startswith("postgresql+psycopg://ecmp:")


def test_api_error_response_scrubs_secret_in_details() -> None:
    secret = "ApiLeakJwtSecretValue-DETAIL01"
    settings = _settings(
        environment="development",
        jwt_secret_key=secret,
        postgres_password=_LAB_DB,
    )
    register_runtime_secrets(settings)
    get_settings.cache_clear()

    with (
        patch("app.main.get_settings", return_value=settings),
        patch("app.main.validate_runtime_config"),
        patch("app.main.configure_authentication"),
        TestClient(create_app()) as client,
    ):
        # Force unhandled path via a route that raises with secret in message
        from fastapi import FastAPI

        app = client.app
        assert isinstance(app, FastAPI)

        @app.get("/__secmig_p5_probe")
        def _probe() -> None:
            from app.core.errors import ValidationAppError

            raise ValidationAppError(
                "bad input",
                details={"hint": f"key={secret}", "password": secret},
            )

        response = client.get("/__secmig_p5_probe")

    assert response.status_code == 400
    body = response.json()
    blob = str(body)
    assert secret not in blob
    assert body["details"]["password"] == REDACTED
    get_settings.cache_clear()


# ---------------------------------------------------------------------------
# Regression — existing startup behavior with valid lab secrets
# ---------------------------------------------------------------------------


def test_startup_succeeds_with_lab_secrets_like_dotenv() -> None:
    """Regression: development still starts when secrets come from config source."""
    settings = _settings(
        environment="development",
        jwt_secret_key=_LAB_JWT,
        postgres_password=_LAB_DB,
        email_provider="logging",
        password_reset_frontend_base_url="http://localhost:3000",
    )
    validate_runtime_config(settings)
    register_runtime_secrets(settings)
    values = collect_secret_values(settings)
    assert _LAB_JWT in values
    assert _LAB_DB in values


def test_create_app_lifespan_with_valid_secrets() -> None:
    settings = _settings(
        environment="development",
        jwt_secret_key=_LAB_JWT,
        postgres_password=_LAB_DB,
    )
    get_settings.cache_clear()
    with (
        patch("app.main.get_settings", return_value=settings),
        TestClient(create_app()) as client,
    ):
        response = client.get("/live")
    assert response.status_code == 200
    get_settings.cache_clear()
