"""Provider Contract Foundation tests (TASK-060)."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from app.modules.provider_contract import (
    ProviderError,
    ProviderErrorCategory,
    ProviderException,
    ProviderMetadata,
    ProviderResponse,
    ProviderStatus,
)
from app.modules.provider_executor import (
    ProviderExecutionPolicy,
    ProviderExecutor,
)


def test_provider_status_pass() -> None:
    values = {s.value for s in ProviderStatus}
    assert values == {"READY", "SUCCESS", "FAILED", "RETRYABLE", "UNSUPPORTED"}


def test_provider_error_pass() -> None:
    err = ProviderError(
        code="RATE_LIMITED",
        message="Too many requests",
        retryable=True,
        category=ProviderErrorCategory.RATE_LIMIT,
    )
    assert err.code == "RATE_LIMITED"
    assert err.retryable is True
    assert err.category is ProviderErrorCategory.RATE_LIMIT
    data = err.as_dict()
    assert data["code"] == "RATE_LIMITED"
    assert data["retryable"] is True
    assert data["category"] == "RATE_LIMIT"


def test_provider_error_rejects_empty() -> None:
    with pytest.raises(ValueError, match="code"):
        ProviderError(code=" ", message="x", retryable=False, category="PROVIDER")
    with pytest.raises(ValueError, match="message"):
        ProviderError(code="E", message="", retryable=False, category="PROVIDER")


def test_provider_metadata_pass() -> None:
    meta = ProviderMetadata(
        latency_ms=12,
        provider_version="1.0.0",
        region="ap-southeast-1",
        tags={"env": "test"},
    )
    assert meta.latency_ms == 12
    assert meta.provider_version == "1.0.0"
    assert meta.region == "ap-southeast-1"
    assert dict(meta.tags) == {"env": "test"}
    data = meta.as_dict()
    assert data["latencyMs"] == 12
    assert data["tags"] == {"env": "test"}


def test_provider_metadata_rejects_negative_latency() -> None:
    with pytest.raises(ValueError, match="latency_ms"):
        ProviderMetadata(latency_ms=-1)


def test_provider_response_pass() -> None:
    response = ProviderResponse(
        provider_name="email-stub",
        status=ProviderStatus.SUCCESS,
        correlation_id="corr-1",
        provider_reference="ext-99",
        error=None,
        metadata=ProviderMetadata(latency_ms=5, tags={"ch": "EMAIL"}),
    )
    assert response.provider_name == "email-stub"
    assert response.status is ProviderStatus.SUCCESS
    assert response.correlation_id == "corr-1"
    assert response.provider_reference == "ext-99"
    assert response.error is None
    data = response.as_dict()
    assert data["status"] == "SUCCESS"
    assert data["providerReference"] == "ext-99"
    assert data["error"] is None


def test_provider_response_with_error() -> None:
    err = ProviderError(
        code="UNSUPPORTED",
        message="Channel not supported",
        retryable=False,
        category=ProviderErrorCategory.UNSUPPORTED,
    )
    response = ProviderResponse(
        provider_name="sms-stub",
        status=ProviderStatus.UNSUPPORTED,
        correlation_id="c-2",
        error=err,
    )
    assert response.status is ProviderStatus.UNSUPPORTED
    assert response.error is err
    assert response.as_dict()["error"]["code"] == "UNSUPPORTED"


def test_provider_response_rejects_blank_name() -> None:
    with pytest.raises(ValueError, match="provider_name"):
        ProviderResponse(
            provider_name="  ",
            status=ProviderStatus.READY,
            correlation_id="c",
        )


def test_provider_exception_abstract() -> None:
    with pytest.raises(TypeError, match="abstract"):
        ProviderException("boom")  # type: ignore[misc]

    class _Concrete(ProviderException):
        pass

    exc = _Concrete(
        "failed",
        provider_name="x",
        status=ProviderStatus.FAILED,
        error=ProviderError(
            code="E1",
            message="fail",
            retryable=False,
            category=ProviderErrorCategory.PROVIDER,
        ),
        correlation_id="cid",
    )
    assert isinstance(exc, ProviderException)
    assert isinstance(exc, Exception)
    assert str(exc) == "failed"
    assert exc.provider_name == "x"
    assert exc.status is ProviderStatus.FAILED
    assert exc.correlation_id == "cid"


def test_immutability_pass() -> None:
    response = ProviderResponse(
        provider_name="p",
        status=ProviderStatus.READY,
        correlation_id="c",
        metadata=ProviderMetadata(tags={"a": "1"}),
    )
    with pytest.raises(Exception):
        response.status = ProviderStatus.SUCCESS  # type: ignore[misc]
    with pytest.raises(TypeError):
        response.metadata.tags["a"] = "2"  # type: ignore[index]
    err = ProviderError(
        code="E",
        message="m",
        retryable=False,
        category="UNKNOWN",
    )
    with pytest.raises(Exception):
        err.retryable = True  # type: ignore[misc]


def test_provider_contract_modules_no_forbidden_imports() -> None:
    root = Path(__file__).resolve().parents[1] / "app" / "modules" / "provider_contract"
    forbidden = (
        "smtplib",
        "httpx",
        "requests",
        "aiohttp",
        "twilio",
        "firebase_admin",
        "socket",
        "urllib",
        "app.modules.complaints",
        "app.modules.complaint",
        "app.modules.workflow",
        "app.modules.notification",
        "app.modules.dashboard",
        "app.modules.kpi",
        "app.modules.execution",
        "app.modules.delivery",
        "app.modules.transport",
        "app.modules.provider_executor",
    )
    for name in ("models.py", "exceptions.py", "__init__.py"):
        source = (root / name).read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)
        for mod in imports:
            assert not any(mod == f or mod.startswith(f + ".") for f in forbidden), (
                f"{name} imports forbidden module {mod}"
            )
        assert ".send(" not in source
        assert ".health(" not in source


def test_regression_provider_executor_untouched() -> None:
    """ProviderExecutor foundation remains prepare-only and independent."""
    executor = ProviderExecutor()
    assert executor.policy is ProviderExecutionPolicy.SYNC_PREPARE
    request, result = executor.prepare(None, None)
    assert request is None
    assert result.success is False
    assert "MISSING_DELIVERY_REQUEST" in result.reason
