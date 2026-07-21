"""ADR-007 gate enforced in code: unsafe non-dev configuration must fail fast."""

from __future__ import annotations

import pytest

from app import settings


def test_dev_env_allows_defaults(monkeypatch):
    monkeypatch.delenv("ECMP_ENV", raising=False)
    settings.validate_runtime_config()  # no raise


def test_non_dev_rejects_default_token(monkeypatch):
    monkeypatch.setenv("ECMP_ENV", "uat")
    monkeypatch.delenv("ECMP_DEV_TOKEN", raising=False)
    monkeypatch.setenv("ECMP_ENABLE_DEV_ENDPOINTS", "false")
    with pytest.raises(RuntimeError, match="ECMP_DEV_TOKEN"):
        settings.validate_runtime_config()


def test_non_dev_rejects_dev_endpoints(monkeypatch):
    monkeypatch.setenv("ECMP_ENV", "prod")
    monkeypatch.setenv("ECMP_DEV_TOKEN", "real-secret-from-vault")
    monkeypatch.setenv("ECMP_ENABLE_DEV_ENDPOINTS", "true")
    with pytest.raises(RuntimeError, match="ECMP_ENABLE_DEV_ENDPOINTS"):
        settings.validate_runtime_config()


def test_non_dev_with_safe_config_passes(monkeypatch):
    monkeypatch.setenv("ECMP_ENV", "sit")
    monkeypatch.setenv("ECMP_DEV_TOKEN", "real-secret-from-vault")
    monkeypatch.setenv("ECMP_ENABLE_DEV_ENDPOINTS", "false")
    settings.validate_runtime_config()  # no raise
