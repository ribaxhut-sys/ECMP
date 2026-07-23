"""RC1 runtime configuration / secret guard tests."""

from __future__ import annotations

import pytest

from app.core.config import Settings, validate_runtime_config


def test_development_allows_default_secret() -> None:
    settings = Settings(
        environment="development",
        jwt_secret_key="change-me-in-production",
    )
    validate_runtime_config(settings)


def test_production_rejects_default_secret() -> None:
    settings = Settings(
        environment="production",
        jwt_secret_key="change-me-in-production",
        allowed_origins="https://app.example.com",
        debug=False,
    )
    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        validate_runtime_config(settings)


def test_production_rejects_short_secret() -> None:
    settings = Settings(
        environment="staging",
        jwt_secret_key="too-short-secret-value",
        allowed_origins="https://app.example.com",
        debug=False,
    )
    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        validate_runtime_config(settings)


def test_production_rejects_wildcard_cors() -> None:
    settings = Settings(
        environment="production",
        jwt_secret_key="a" * 32,
        allowed_origins="*",
        debug=False,
    )
    with pytest.raises(RuntimeError, match="Wildcard"):
        validate_runtime_config(settings)


def test_production_accepts_strong_secret() -> None:
    settings = Settings(
        environment="production",
        jwt_secret_key="a" * 32,
        allowed_origins="https://app.example.com",
        debug=False,
    )
    validate_runtime_config(settings)


def test_docs_disabled_outside_development() -> None:
    assert Settings(environment="development").docs_enabled is True
    assert Settings(environment="staging").docs_enabled is False
    assert Settings(environment="production").docs_enabled is False
