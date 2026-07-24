"""Transport Adapter Foundation tests (TASK-058)."""

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
from app.modules.transport import (
    TransportAdapter,
    TransportCapability,
    TransportRegistry,
    TransportResult,
    TransportSelector,
)


class _StubAdapter(TransportAdapter):
    """Test double — implements contract; send/health must not be called by foundation."""

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
        raise AssertionError("send() must not be invoked by TASK-058 foundation")

    def health(self) -> bool:
        self.health_calls += 1
        raise AssertionError("health() must not be invoked by TASK-058 foundation")


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
        metadata=freeze_mapping({}),
    )


@pytest.fixture()
def registry() -> TransportRegistry:
    return TransportRegistry()


@pytest.fixture()
def email_adapter() -> _StubAdapter:
    return _StubAdapter("email-stub", frozenset({TransportCapability.EMAIL}))


@pytest.fixture()
def multi_adapter() -> _StubAdapter:
    return _StubAdapter(
        "multi-stub",
        frozenset(
            {
                TransportCapability.EMAIL,
                TransportCapability.SMS,
                TransportCapability.PUSH,
            }
        ),
    )


def test_registry_pass(registry: TransportRegistry, email_adapter: _StubAdapter) -> None:
    assert len(registry) == 0
    registry.register(email_adapter)
    assert len(registry) == 1
    assert registry.adapters()[0] is email_adapter


def test_registration_pass(
    registry: TransportRegistry, email_adapter: _StubAdapter, multi_adapter: _StubAdapter
) -> None:
    registry.register(email_adapter)
    registry.register(multi_adapter)
    assert len(registry) == 2
    # replace by name
    replacement = _StubAdapter("email-stub", frozenset({TransportCapability.EMAIL}))
    registry.register(replacement)
    assert len(registry) == 2
    names = [a.name for a in registry.adapters()]
    assert names.count("email-stub") == 1
    assert names.count("multi-stub") == 1
    by_name = next(a for a in registry.adapters() if a.name == "email-stub")
    assert by_name is replacement
    # First supporter of EMAIL is multi-stub (registered before replacement)
    assert registry.lookup(TransportCapability.EMAIL) is multi_adapter


def test_lookup_pass(registry: TransportRegistry, email_adapter: _StubAdapter) -> None:
    registry.register(email_adapter)
    found = registry.lookup(TransportCapability.EMAIL)
    assert found is email_adapter
    assert registry.has("EMAIL") is True
    assert registry.lookup(TransportCapability.SMS) is None
    assert registry.has(TransportCapability.WHATSAPP) is False


def test_selector_pass(
    registry: TransportRegistry, email_adapter: _StubAdapter
) -> None:
    registry.register(email_adapter)
    selector = TransportSelector(registry=registry)
    adapter, result = selector.select(_delivery_request(DeliveryChannel.EMAIL))
    assert adapter is email_adapter
    assert result.supported is True
    assert result.adapter_found is True
    assert result.adapter_name == "email-stub"
    assert "ADAPTER_SELECTED" in result.reason
    data = result.as_dict()
    assert data["adapterFound"] is True
    assert data["adapterName"] == "email-stub"


def test_unknown_channel_pass(registry: TransportRegistry) -> None:
    # WEBSOCKET has no TransportCapability mapping
    selector = TransportSelector(registry=registry)
    adapter, result = selector.select(_delivery_request(DeliveryChannel.WEBSOCKET))
    assert adapter is None
    assert result.supported is False
    assert result.adapter_found is False
    assert result.adapter_name is None
    assert "UNKNOWN_CHANNEL" in result.reason

    # Registry rejects unknown capability tokens
    assert registry.lookup("CARRIER_PIGEON") is None
    assert registry.lookup("WEBSOCKET") is None


def test_capability_pass() -> None:
    values = {c.value for c in TransportCapability}
    assert values == {"EMAIL", "WHATSAPP", "SMS", "PUSH", "WEBHOOK"}


def test_adapter_not_found_pass(registry: TransportRegistry) -> None:
    selector = TransportSelector(registry=registry)
    adapter, result = selector.select(_delivery_request(DeliveryChannel.SMS))
    assert adapter is None
    assert result.supported is True
    assert result.adapter_found is False
    assert "ADAPTER_NOT_FOUND" in result.reason


def test_no_send_pass(
    registry: TransportRegistry, email_adapter: _StubAdapter
) -> None:
    registry.register(email_adapter)
    selector = TransportSelector(registry=registry)
    request = _delivery_request()

    adapter, result = selector.select(request)
    _ = registry.lookup(TransportCapability.EMAIL)
    _ = registry.has(TransportCapability.EMAIL)

    assert result.adapter_found is True
    assert adapter is email_adapter
    assert email_adapter.send_calls == 0
    assert email_adapter.health_calls == 0


def test_transport_modules_no_provider_imports() -> None:
    root = Path(__file__).resolve().parents[1] / "app" / "modules" / "transport"
    forbidden = (
        "smtplib",
        "httpx",
        "requests",
        "aiohttp",
        "twilio",
        "firebase_admin",
        "app.modules.complaints",
        "app.modules.complaint",
        "app.modules.workflow",
        "app.modules.notification",
        "app.modules.dashboard",
        "app.modules.kpi",
        "app.modules.execution",
        "app.modules.delivery.engine",
        "app.modules.delivery.validator",
    )
    for name in ("adapter.py", "registry.py", "selector.py", "models.py", "__init__.py"):
        tree = ast.parse((root / name).read_text(encoding="utf-8"))
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


def test_immutable_selector_input(
    registry: TransportRegistry, email_adapter: _StubAdapter
) -> None:
    registry.register(email_adapter)
    request = _delivery_request()
    selector = TransportSelector(registry=registry)
    selector.select(request)
    with pytest.raises(Exception):
        request.recipient = "other"  # type: ignore[misc]
    with pytest.raises(TypeError):
        request.payload["x"] = 2  # type: ignore[index]


def test_regression_delivery_engine_untouched() -> None:
    """DeliveryEngine still prepares independently of transport selection."""
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
    request, result = engine.prepare(dispatch)
    assert result.success is True
    assert request is not None

    selector = TransportSelector()
    adapter, t_result = selector.select(request)
    assert adapter is None
    assert t_result.adapter_found is False
    assert isinstance(t_result, TransportResult)


def test_abstract_adapter_cannot_instantiate() -> None:
    with pytest.raises(TypeError):
        TransportAdapter()  # type: ignore[abstract]


def test_get_transport_di() -> None:
    from app.dependencies.events import (
        get_transport_registry,
        get_transport_selector,
        reset_event_runtime_for_tests,
    )

    reset_event_runtime_for_tests()
    reg_a = get_transport_registry()
    reg_b = get_transport_registry()
    sel_a = get_transport_selector()
    sel_b = get_transport_selector()
    assert reg_a is reg_b
    assert sel_a is sel_b
    assert sel_a.registry is reg_a
    reset_event_runtime_for_tests()


def test_register_rejects_non_adapter(registry: TransportRegistry) -> None:
    with pytest.raises(TypeError):
        registry.register(MagicMock())  # type: ignore[arg-type]
