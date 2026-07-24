"""Provider Executor Foundation tests (TASK-059)."""

from __future__ import annotations

import ast
import uuid
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from app.modules.delivery import (
    DeliveryChannel,
    DeliveryContext,
    DeliveryEngine,
    DeliveryRequest,
    freeze_mapping,
)
from app.modules.execution import DispatchRequest, ExecutionContext
from app.modules.provider_executor import (
    ProviderExecutionPolicy,
    ProviderExecutionRequest,
    ProviderExecutionResult,
    ProviderExecutionValidator,
    ProviderExecutor,
)
from app.modules.transport import (
    TransportAdapter,
    TransportCapability,
    TransportSelector,
)


class _StubAdapter(TransportAdapter):
    """Test double — implements contract; send/health must not be called."""

    def __init__(
        self,
        name: str,
        channels: frozenset[TransportCapability],
    ) -> None:
        self._name = name
        self._channels = channels
        self.send_calls = 0
        self.health_calls = 0

    @property
    def name(self) -> str:
        return self._name

    def supports(self, channel: TransportCapability | str) -> bool:
        token = (
            channel.value
            if isinstance(channel, TransportCapability)
            else str(channel).strip().upper()
        )
        try:
            cap = TransportCapability(token)
        except ValueError:
            return False
        return cap in self._channels

    def send(self, request: DeliveryRequest) -> Any:
        self.send_calls += 1
        raise AssertionError("send() must not be invoked by TASK-059 foundation")

    def health(self) -> bool:
        self.health_calls += 1
        raise AssertionError("health() must not be invoked by TASK-059 foundation")


def _delivery_request(
    channel: DeliveryChannel = DeliveryChannel.EMAIL,
) -> DeliveryRequest:
    return DeliveryRequest(
        request_id=uuid.uuid4(),
        dispatch_request_id=uuid.uuid4(),
        channel=channel,
        recipient="user@example.com",
        template_id="t1",
        payload=freeze_mapping({"a": 1}),
        context=DeliveryContext(
            trace_id="tr",
            correlation_id="cr",
            metadata=freeze_mapping({}),
        ),
        metadata=freeze_mapping({"source": "test"}),
    )


@pytest.fixture()
def email_adapter() -> _StubAdapter:
    return _StubAdapter("email-stub", frozenset({TransportCapability.EMAIL}))


@pytest.fixture()
def sms_adapter() -> _StubAdapter:
    return _StubAdapter("sms-stub", frozenset({TransportCapability.SMS}))


@pytest.fixture()
def executor() -> ProviderExecutor:
    return ProviderExecutor()


def test_execution_request_pass(
    executor: ProviderExecutor, email_adapter: _StubAdapter
) -> None:
    delivery = _delivery_request()
    request, result = executor.prepare(delivery, email_adapter)
    assert result.success is True
    assert result.ready is True
    assert result.provider_name == "email-stub"
    assert "EXECUTION_READY" in result.reason
    assert request is not None
    assert isinstance(request, ProviderExecutionRequest)
    assert isinstance(request.execution_id, uuid.UUID)
    assert request.delivery_request is delivery
    assert request.transport_adapter is email_adapter
    assert request.context is delivery.context
    assert request.metadata["policy"] == "SYNC_PREPARE"
    assert request.metadata["channel"] == "EMAIL"
    data = request.as_dict()
    assert data["providerName"] == "email-stub"
    assert data["channel"] == "EMAIL"


def test_validator_pass(email_adapter: _StubAdapter) -> None:
    validator = ProviderExecutionValidator()
    validation = validator.validate(_delivery_request(), email_adapter)
    assert validation.result.success is True
    assert validation.result.ready is True
    assert validation.capability is TransportCapability.EMAIL


def test_policy_pass(executor: ProviderExecutor) -> None:
    assert executor.policy is ProviderExecutionPolicy.SYNC_PREPARE
    with pytest.raises(ValueError, match="SYNC_PREPARE"):
        ProviderExecutor(policy="ASYNC")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="SYNC_PREPARE"):
        ProviderExecutor(policy="RETRY")  # type: ignore[arg-type]


def test_adapter_compatibility_pass(
    executor: ProviderExecutor, email_adapter: _StubAdapter
) -> None:
    request, result = executor.prepare(_delivery_request(), email_adapter)
    assert result.success is True
    assert request is not None


def test_adapter_channel_mismatch(
    executor: ProviderExecutor, sms_adapter: _StubAdapter
) -> None:
    request, result = executor.prepare(
        _delivery_request(DeliveryChannel.EMAIL), sms_adapter
    )
    assert request is None
    assert result.success is False
    assert result.ready is False
    assert result.provider_name == "sms-stub"
    assert "ADAPTER_CHANNEL_MISMATCH" in result.reason


def test_unknown_adapter(executor: ProviderExecutor) -> None:
    request, result = executor.prepare(_delivery_request(), MagicMock())  # type: ignore[arg-type]
    assert request is None
    assert result.success is False
    assert result.ready is False
    assert "UNKNOWN_ADAPTER" in result.reason


def test_missing_delivery_request(
    executor: ProviderExecutor, email_adapter: _StubAdapter
) -> None:
    request, result = executor.prepare(None, email_adapter)
    assert request is None
    assert "MISSING_DELIVERY_REQUEST" in result.reason


def test_missing_transport_adapter(executor: ProviderExecutor) -> None:
    request, result = executor.prepare(_delivery_request(), None)
    assert request is None
    assert "MISSING_TRANSPORT_ADAPTER" in result.reason


def test_unsupported_channel(
    executor: ProviderExecutor, email_adapter: _StubAdapter
) -> None:
    request, result = executor.prepare(
        _delivery_request(DeliveryChannel.WEBSOCKET), email_adapter
    )
    assert request is None
    assert result.success is False
    assert "UNSUPPORTED_CHANNEL" in result.reason


def test_no_execution_pass(
    executor: ProviderExecutor, email_adapter: _StubAdapter
) -> None:
    request, result = executor.prepare(_delivery_request(), email_adapter)
    assert result.ready is True
    assert request is not None
    assert email_adapter.send_calls == 0
    assert email_adapter.health_calls == 0
    # Result proves prepare-only contract
    assert isinstance(result, ProviderExecutionResult)
    result_data = result.as_dict()
    assert result_data["ready"] is True
    assert "send" not in result.reason.lower()


def test_immutable_execution_request(
    executor: ProviderExecutor, email_adapter: _StubAdapter
) -> None:
    request, result = executor.prepare(_delivery_request(), email_adapter)
    assert result.success is True
    assert request is not None
    with pytest.raises(Exception):
        request.provider_name = "x"  # type: ignore[attr-defined]
    with pytest.raises(Exception):
        request.execution_id = uuid.uuid4()  # type: ignore[misc]
    with pytest.raises(TypeError):
        request.metadata["x"] = 1  # type: ignore[index]


def test_provider_executor_modules_no_forbidden_imports() -> None:
    root = Path(__file__).resolve().parents[1] / "app" / "modules" / "provider_executor"
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
        "app.modules.delivery.engine",
        "app.modules.delivery.validator",
        "app.modules.transport.selector",
        "app.modules.transport.registry",
    )
    forbidden_attrs = ("send", "health")
    for name in ("executor.py", "validator.py", "models.py", "__init__.py"):
        source = (root / name).read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)
            elif isinstance(node, ast.Attribute) and isinstance(node.attr, str):
                if node.attr in forbidden_attrs and name != "validator.py":
                    # validator / executor must not call .send / .health
                    # Attribute access of method name in comments is fine;
                    # AST Attribute nodes mean real code references.
                    pass
        for mod in imports:
            assert not any(mod == f or mod.startswith(f + ".") for f in forbidden), (
                f"{name} imports forbidden module {mod}"
            )
        # Explicit: never call send() or health() in module source
        assert ".send(" not in source
        assert ".health(" not in source


def test_regression_transport_and_delivery_untouched(
    email_adapter: _StubAdapter,
) -> None:
    """DeliveryEngine + TransportSelector still work; executor does not send."""
    engine = DeliveryEngine()
    dispatch = DispatchRequest(
        run_id=uuid.uuid4(),
        task_id=uuid.uuid4(),
        task_type="NOTIFY",
        target="channel:email",
        configuration=freeze_mapping(
            {
                "channel": "EMAIL",
                "recipient": "a@b.c",
                "template_id": "t",
                "payload": {"k": 1},
            }
        ),
        context=ExecutionContext(
            trace_id="t",
            correlation_id="c",
            metadata=freeze_mapping({}),
        ),
    )
    delivery, d_result = engine.prepare(dispatch)
    assert d_result.success is True
    assert delivery is not None

    selector = TransportSelector()
    # No adapter registered → selector finds none; executor still rejects missing
    adapter, t_result = selector.select(delivery)
    assert adapter is None
    assert t_result.adapter_found is False

    executor = ProviderExecutor()
    # With stub adapter (as if selected), prepare succeeds without send
    request, p_result = executor.prepare(delivery, email_adapter)
    assert p_result.success is True
    assert request is not None
    assert email_adapter.send_calls == 0
    assert email_adapter.health_calls == 0


def test_get_provider_executor_di() -> None:
    from app.dependencies.events import (
        get_provider_executor,
        reset_event_runtime_for_tests,
    )

    reset_event_runtime_for_tests()
    a = get_provider_executor()
    b = get_provider_executor()
    assert a is b
    assert a.policy is ProviderExecutionPolicy.SYNC_PREPARE
    reset_event_runtime_for_tests()
