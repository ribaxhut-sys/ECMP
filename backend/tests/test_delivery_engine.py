"""Delivery Engine Foundation tests (TASK-057)."""

from __future__ import annotations

import ast
import uuid
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.modules.delivery import (
    DeliveryChannel,
    DeliveryContext,
    DeliveryEngine,
    DeliveryPolicy,
    DeliveryRequest,
    DeliveryResult,
    DeliveryValidator,
    freeze_mapping,
)
from app.modules.execution import (
    DispatchRequest,
    ExecutionContext,
    ExecutionDispatcher,
    ExecutionEngine,
    ExecutionRegistry,
    ExecutionRun,
    ExecutionRunStatus,
    ExecutionRunTask,
    ExecutionRunTaskStatus,
    ExecutionTask,
)
from app.modules.execution.models import freeze_mapping as exec_freeze


def _dispatch(
    *,
    channel: str = "EMAIL",
    recipient: str = "user@example.com",
    template: str = "complaint.created",
    payload: dict | None = None,
    target: str = "channel:email",
) -> DispatchRequest:
    cfg: dict = {
        "channel": channel,
        "recipient": recipient,
        "template_id": template,
        "payload": payload if payload is not None else {"caseId": "C-1"},
    }
    return DispatchRequest(
        run_id=uuid.uuid4(),
        task_id=uuid.uuid4(),
        task_type="NOTIFY",
        target=target,
        configuration=freeze_mapping(cfg),
        context=ExecutionContext(
            trace_id="trace-del",
            correlation_id="corr-del",
            tenant_id="tenant-1",
            user_id="user-9",
            metadata=freeze_mapping({"source": "test"}),
        ),
    )


def _dispatch_omit(*, omit: str) -> DispatchRequest:
    """Build a DispatchRequest missing one required delivery field."""
    cfg: dict = {
        "channel": "EMAIL",
        "recipient": "user@example.com",
        "template_id": "complaint.created",
        "payload": {"caseId": "C-1"},
    }
    if omit == "recipient":
        del cfg["recipient"]
    elif omit == "channel":
        del cfg["channel"]
    elif omit == "template":
        del cfg["template_id"]
    elif omit == "payload":
        del cfg["payload"]
    target = "x" if omit == "channel" else "channel:email"
    return DispatchRequest(
        run_id=uuid.uuid4(),
        task_id=uuid.uuid4(),
        task_type="NOTIFY",
        target=target,
        configuration=freeze_mapping(cfg),
        context=ExecutionContext(
            trace_id="t",
            correlation_id="c",
            metadata=freeze_mapping({}),
        ),
    )


@pytest.fixture()
def engine() -> DeliveryEngine:
    return DeliveryEngine()


def test_delivery_request_pass(engine: DeliveryEngine) -> None:
    dispatch = _dispatch()
    request, result = engine.prepare(dispatch)

    assert result.success is True
    assert isinstance(request, DeliveryRequest)
    assert request.dispatch_request_id == dispatch.task_id
    assert request.channel == DeliveryChannel.EMAIL
    assert request.recipient == "user@example.com"
    assert request.template_id == "complaint.created"
    assert request.payload["caseId"] == "C-1"
    assert request.context.trace_id == "trace-del"
    assert request.context.correlation_id == "corr-del"
    assert request.context.tenant_id == "tenant-1"
    assert request.context.user_id == "user-9"
    data = request.as_dict()
    assert data["channel"] == "EMAIL"
    assert data["templateId"] == "complaint.created"


def test_delivery_validator_pass() -> None:
    validator = DeliveryValidator()
    validation = validator.validate(_dispatch())
    assert validation.result.success is True
    assert validation.channel == DeliveryChannel.EMAIL
    assert validation.recipient == "user@example.com"
    assert validation.template_id == "complaint.created"
    assert validation.payload is not None


def test_delivery_context_pass(engine: DeliveryEngine) -> None:
    dispatch = _dispatch()
    request, _ = engine.prepare(dispatch)
    assert request is not None
    assert isinstance(request.context, DeliveryContext)
    ctx = request.context.as_dict()
    assert ctx["traceId"] == "trace-del"
    assert ctx["correlationId"] == "corr-del"
    assert ctx["metadata"]["source"] == "test"


def test_delivery_policy_pass(engine: DeliveryEngine) -> None:
    assert engine.policy == DeliveryPolicy.DIRECT
    with pytest.raises(ValueError, match="DIRECT"):
        DeliveryEngine(policy="BATCH")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="DIRECT"):
        DeliveryEngine(policy="RETRY")  # type: ignore[arg-type]


def test_invalid_channel_pass(engine: DeliveryEngine) -> None:
    dispatch = DispatchRequest(
        run_id=uuid.uuid4(),
        task_id=uuid.uuid4(),
        task_type="NOTIFY",
        target="channel:carrier-pigeon",
        configuration=freeze_mapping(
            {
                "channel": "CARRIER_PIGEON",
                "recipient": "a@b.c",
                "template_id": "t1",
                "payload": {},
            }
        ),
        context=ExecutionContext(
            trace_id="t",
            correlation_id="c",
            metadata=freeze_mapping({}),
        ),
    )
    request, result = engine.prepare(dispatch)
    assert request is None
    assert result.success is False
    assert "INVALID_CHANNEL" in result.reason
    assert result.provider_selected is None


def test_invalid_recipient_pass(engine: DeliveryEngine) -> None:
    request, result = engine.prepare(_dispatch_omit(omit="recipient"))
    assert request is None
    assert "INVALID_RECIPIENT" in result.reason

    empty = DispatchRequest(
        run_id=uuid.uuid4(),
        task_id=uuid.uuid4(),
        task_type="NOTIFY",
        target="channel:email",
        configuration=freeze_mapping(
            {
                "channel": "EMAIL",
                "recipient": "   ",
                "template_id": "t1",
                "payload": {},
            }
        ),
        context=ExecutionContext(
            trace_id="t",
            correlation_id="c",
            metadata=freeze_mapping({}),
        ),
    )
    request2, result2 = engine.prepare(empty)
    assert request2 is None
    assert "INVALID_RECIPIENT" in result2.reason


def test_invalid_template_pass(engine: DeliveryEngine) -> None:
    request, result = engine.prepare(_dispatch_omit(omit="template"))
    assert request is None
    assert "INVALID_TEMPLATE" in result.reason


def test_invalid_payload_pass(engine: DeliveryEngine) -> None:
    request, result = engine.prepare(_dispatch_omit(omit="payload"))
    assert request is None
    assert "INVALID_PAYLOAD" in result.reason

    bad = DispatchRequest(
        run_id=uuid.uuid4(),
        task_id=uuid.uuid4(),
        task_type="NOTIFY",
        target="channel:sms",
        configuration=freeze_mapping(
            {
                "channel": "SMS",
                "recipient": "62812",
                "template_id": "t1",
                "payload": "not-a-mapping",
            }
        ),
        context=ExecutionContext(
            trace_id="t",
            correlation_id="c",
            metadata=freeze_mapping({}),
        ),
    )
    request2, result2 = engine.prepare(bad)
    assert request2 is None
    assert "INVALID_PAYLOAD" in result2.reason


def test_channel_from_target_pass(engine: DeliveryEngine) -> None:
    dispatch = DispatchRequest(
        run_id=uuid.uuid4(),
        task_id=uuid.uuid4(),
        task_type="NOTIFY",
        target="channel:whatsapp",
        configuration=freeze_mapping(
            {
                "recipient": "62812",
                "template": "alert",
                "payload": {"x": 1},
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
    assert request.channel == DeliveryChannel.WHATSAPP
    assert request.template_id == "alert"


def test_immutable_delivery_request(engine: DeliveryEngine) -> None:
    request, _ = engine.prepare(_dispatch())
    assert request is not None
    with pytest.raises(Exception):
        request.recipient = "other"  # type: ignore[misc]
    with pytest.raises(TypeError):
        request.payload["k"] = 1  # type: ignore[index]
    with pytest.raises(TypeError):
        request.metadata["k"] = 1  # type: ignore[index]


def test_delivery_result_foundation(engine: DeliveryEngine) -> None:
    _, result = engine.prepare(_dispatch())
    assert isinstance(result, DeliveryResult)
    data = result.as_dict()
    assert data["success"] is True
    assert data["providerSelected"] is None
    assert "DELIVERY_READY" in data["reason"]


def test_no_delivery_pass(engine: DeliveryEngine) -> None:
    """Engine must not call any transport / provider / AI."""
    smtp = MagicMock(name="smtp")
    whatsapp = MagicMock(name="whatsapp")
    fcm = MagicMock(name="fcm")
    apns = MagicMock(name="apns")
    sms = MagicMock(name="sms")
    webhook = MagicMock(name="webhook")
    ai = MagicMock(name="ai")

    with (
        patch.dict(
            "sys.modules",
            {
                "smtplib": smtp,
                "app.modules.delivery.providers": MagicMock(),
            },
        ),
        patch("app.modules.notification.factory.NotificationFactory") as mock_notif,
        patch("app.modules.complaints.service.ComplaintService", create=True) as mock_c,
        patch("app.modules.workflow.engine.WorkflowEngine", create=True) as mock_wf,
    ):
        request, result = engine.prepare(_dispatch())
        engine.prepare(_dispatch(channel="SMS", target="channel:sms"))

    assert result.success is True
    assert request is not None
    assert result.provider_selected is None
    mock_notif.assert_not_called()
    mock_c.assert_not_called()
    mock_wf.assert_not_called()
    smtp.assert_not_called()
    whatsapp.assert_not_called()
    fcm.assert_not_called()
    apns.assert_not_called()
    sms.assert_not_called()
    webhook.assert_not_called()
    ai.assert_not_called()


def test_delivery_modules_no_transport_imports() -> None:
    root = Path(__file__).resolve().parents[1] / "app" / "modules" / "delivery"
    forbidden = (
        "smtplib",
        "httpx",
        "requests",
        "aiohttp",
        "app.modules.complaints",
        "app.modules.complaint",
        "app.modules.workflow",
        "app.modules.notification",
        "app.modules.dashboard",
        "app.modules.kpi",
        "app.modules.execution.engine",
        "app.modules.execution.dispatcher",
        "app.modules.execution.runtime",
        "app.modules.execution.registry",
    )
    for name in ("engine.py", "validator.py", "models.py", "__init__.py"):
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


def test_regression_dispatcher_untouched() -> None:
    """ExecutionDispatcher still plans independently of DeliveryEngine."""
    reg = ExecutionRegistry()
    reg.register("NOTIFY", lambda *_a, **_k: None)
    plan_task = ExecutionTask(
        task_id=uuid.uuid4(),
        order=1,
        task_type="NOTIFY",
        target="channel:email",
        configuration=exec_freeze({"template": "x"}),
        executed=False,
    )
    run = ExecutionRun(
        run_id=uuid.uuid4(),
        plan_id=uuid.uuid4(),
        created_at=datetime.now(UTC),
        status=ExecutionRunStatus.READY,
        tasks=(
            ExecutionRunTask(
                task_id=uuid.uuid4(),
                execution_task_id=plan_task.task_id,
                order=1,
                status=ExecutionRunTaskStatus.CREATED,
            ),
        ),
        metadata=exec_freeze({}),
        context=ExecutionContext(
            trace_id="t",
            correlation_id="c",
            metadata=exec_freeze({}),
        ),
    )
    dispatcher = ExecutionDispatcher(registry=reg)
    request, result = dispatcher.dispatch(run, plan_task)
    assert result.success is True
    assert request is not None

    engine = ExecutionEngine()
    created = ExecutionRun(
        run_id=run.run_id,
        plan_id=run.plan_id,
        created_at=run.created_at,
        status=ExecutionRunStatus.CREATED,
        tasks=run.tasks,
        metadata=run.metadata,
        context=run.context,
    )
    eng_result, ready = engine.transition(created, ExecutionRunStatus.READY)
    assert eng_result.success is True
    assert ready.status == ExecutionRunStatus.READY


def test_get_delivery_engine_di() -> None:
    from app.dependencies.events import get_delivery_engine, reset_event_runtime_for_tests

    reset_event_runtime_for_tests()
    a = get_delivery_engine()
    b = get_delivery_engine()
    assert a is b
    assert a.policy == DeliveryPolicy.DIRECT
    reset_event_runtime_for_tests()
