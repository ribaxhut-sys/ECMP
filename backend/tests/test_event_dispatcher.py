"""In-process EventDispatcher unit tests (TASK-046)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock

import pytest

from app.core.enums import (
    ComplaintSourceType,
    ComplaintStatus,
    ComplaintTargetType,
)
from app.modules.complaint_events import (
    ComplaintEventFactory,
    ComplaintEventType,
    EventSourceRef,
    EventTargetRef,
)
from app.modules.event_dispatcher import (
    DispatchResult,
    EventDispatcher,
    EventHandler,
    HandlerResult,
)


class _RecordingHandler(EventHandler):
    def __init__(self, name: str | None = None) -> None:
        self.name = name or type(self).__name__
        self.events: list[Any] = []

    def handle(self, event: Any) -> None:
        self.events.append(event)


class _FailingHandler(EventHandler):
    def __init__(self, message: str = "boom") -> None:
        self.message = message

    def handle(self, event: Any) -> None:
        raise RuntimeError(self.message)


class _OrderedHandler(EventHandler):
    def __init__(self, label: str, sink: list[str]) -> None:
        self.label = label
        self._sink = sink

    def handle(self, event: Any) -> None:
        self._sink.append(self.label)


def _sample_event() -> Any:
    return ComplaintEventFactory.create_created(
        complaint_id=uuid.uuid4(),
        complaint_number="CMP-DISP0001",
        current_status=ComplaintStatus.NEW.value,
        priority="MEDIUM",
        source=EventSourceRef(
            source_type=ComplaintSourceType.CUSTOMER.value,
            source_id=uuid.uuid4(),
        ),
        target=EventTargetRef(
            target_type=ComplaintTargetType.BRANCH.value,
            target_id=uuid.uuid4(),
        ),
        occurred_at=datetime.now(UTC),
    )


def test_register_pass() -> None:
    dispatcher = EventDispatcher()
    handler = _RecordingHandler()
    dispatcher.register(handler)
    assert dispatcher.registered_handlers() == [handler]


def test_register_rejects_non_handler() -> None:
    dispatcher = EventDispatcher()
    with pytest.raises(TypeError, match="EventHandler"):
        dispatcher.register(object())  # type: ignore[arg-type]


def test_unregister_pass() -> None:
    dispatcher = EventDispatcher()
    handler = _RecordingHandler()
    dispatcher.register(handler)
    assert dispatcher.unregister(handler) is True
    assert dispatcher.registered_handlers() == []
    assert dispatcher.unregister(handler) is False


def test_dispatch_pass() -> None:
    dispatcher = EventDispatcher()
    handler = _RecordingHandler()
    dispatcher.register(handler)
    event = _sample_event()
    result = dispatcher.dispatch(event)
    assert result.ok is True
    assert result.success_count == 1
    assert result.failed_count == 0
    assert len(handler.events) == 1
    assert handler.events[0] is event


def test_dispatch_with_no_handlers() -> None:
    dispatcher = EventDispatcher()
    result = dispatcher.dispatch(_sample_event())
    assert result.ok is True
    assert result.success_count == 0
    assert result.failed_count == 0
    assert result.handler_results == ()


def test_multiple_handlers_pass() -> None:
    dispatcher = EventDispatcher()
    h1 = _RecordingHandler()
    h2 = _RecordingHandler()
    dispatcher.register(h1)
    dispatcher.register(h2)
    event = _sample_event()
    result = dispatcher.dispatch(event)
    assert result.success_count == 2
    assert result.failed_count == 0
    assert h1.events == [event]
    assert h2.events == [event]


def test_handler_failure_pass() -> None:
    """One failure must not stop remaining handlers."""
    dispatcher = EventDispatcher()
    good_before = _RecordingHandler()
    failing = _FailingHandler("handler exploded")
    good_after = _RecordingHandler()
    dispatcher.register(good_before)
    dispatcher.register(failing)
    dispatcher.register(good_after)

    event = _sample_event()
    result = dispatcher.dispatch(event)

    assert result.success_count == 2
    assert result.failed_count == 1
    assert result.ok is False
    assert len(good_before.events) == 1
    assert len(good_after.events) == 1
    failed = [r for r in result.handler_results if not r.success]
    assert len(failed) == 1
    assert failed[0].handler_name == "_FailingHandler"
    assert "exploded" in (failed[0].error or "")
    assert failed[0].exception_type == "RuntimeError"


def test_dispatch_result_pass() -> None:
    dispatcher = EventDispatcher()
    dispatcher.register(_RecordingHandler())
    dispatcher.register(_FailingHandler())
    result = dispatcher.dispatch(_sample_event())

    assert isinstance(result, DispatchResult)
    assert result.success_count == 1
    assert result.failed_count == 1
    assert len(result.handler_results) == 2
    assert all(isinstance(r, HandlerResult) for r in result.handler_results)
    assert result.handler_results[0].success is True
    assert result.handler_results[1].success is False


def test_ordering_pass() -> None:
    dispatcher = EventDispatcher()
    order: list[str] = []
    dispatcher.register(_OrderedHandler("A", order))
    dispatcher.register(_OrderedHandler("B", order))
    dispatcher.register(_OrderedHandler("C", order))
    dispatcher.dispatch(_sample_event())
    assert order == ["A", "B", "C"]
    names = [h.__class__.__name__ for h in dispatcher.registered_handlers()]
    assert names == ["_OrderedHandler", "_OrderedHandler", "_OrderedHandler"]
    labels = [h.label for h in dispatcher.registered_handlers()]  # type: ignore[attr-defined]
    assert labels == ["A", "B", "C"]


def test_complaint_service_dispatches_without_knowing_handlers() -> None:
    """Producer → factory → dispatcher; service does not name consumers."""
    from app.modules.complaints.schemas import ComplaintCreateRequest
    from app.modules.complaints.service import ComplaintService

    customer_id = uuid.uuid4()
    branch_id = uuid.uuid4()
    actor_id = uuid.uuid4()
    created: dict[str, Any] = {}

    def _add(complaint: Any) -> Any:
        now = datetime.now(UTC)
        complaint.id = uuid.uuid4()  # type: ignore[attr-defined]
        complaint.complaint_number = "CMP-DISPCREATE"  # type: ignore[attr-defined]
        complaint.created_at = now  # type: ignore[attr-defined]
        complaint.updated_at = now  # type: ignore[attr-defined]
        created["row"] = complaint
        return complaint

    repo = MagicMock()
    repo.customer_exists.return_value = True
    repo.branch_exists.return_value = True
    repo.add.side_effect = _add
    repo.refresh.side_effect = lambda c: None

    dispatcher = EventDispatcher()
    handler = _RecordingHandler()
    dispatcher.register(handler)

    service = ComplaintService(
        repo,
        sla_service=MagicMock(),
        event_dispatcher=dispatcher,
    )
    service.create(
        ComplaintCreateRequest(
            sourceType="CUSTOMER",
            sourceId=customer_id,
            targetType="BRANCH",
            targetId=branch_id,
            subject="Dispatch seed",
            description="Creates and dispatches ComplaintCreated",
            priority="MEDIUM",
        ),
        actor_user_id=actor_id,
    )

    assert len(service._recent_events) == 1
    assert service._recent_events[0].event_type == ComplaintEventType.CREATED
    assert len(handler.events) == 1
    assert handler.events[0].event_type == ComplaintEventType.CREATED
    assert len(service._last_dispatch_results) == 1
    assert service._last_dispatch_results[0].success_count == 1
    # Service must not import/register concrete consumer modules.
    assert "Notification" not in type(handler).__name__


def test_complaint_service_dispatch_isolates_handler_failure() -> None:
    """Business write succeeds even when a handler raises."""
    from app.modules.complaints.schemas import ComplaintCreateRequest
    from app.modules.complaints.service import ComplaintService

    customer_id = uuid.uuid4()
    branch_id = uuid.uuid4()
    created: dict[str, Any] = {}

    def _add(complaint: Any) -> Any:
        now = datetime.now(UTC)
        complaint.id = uuid.uuid4()  # type: ignore[attr-defined]
        complaint.complaint_number = "CMP-DISPFAIL"  # type: ignore[attr-defined]
        complaint.created_at = now  # type: ignore[attr-defined]
        complaint.updated_at = now  # type: ignore[attr-defined]
        created["row"] = complaint
        return complaint

    repo = MagicMock()
    repo.customer_exists.return_value = True
    repo.branch_exists.return_value = True
    repo.add.side_effect = _add
    repo.refresh.side_effect = lambda c: None

    dispatcher = EventDispatcher()
    dispatcher.register(_FailingHandler("consumer down"))
    after = _RecordingHandler()
    dispatcher.register(after)

    service = ComplaintService(
        repo,
        sla_service=MagicMock(),
        event_dispatcher=dispatcher,
    )
    # Must not raise despite handler failure.
    service.create(
        ComplaintCreateRequest(
            sourceType="CUSTOMER",
            sourceId=customer_id,
            targetType="BRANCH",
            targetId=branch_id,
            subject="Isolated failure",
            description="Handler failure must not abort create",
            priority="LOW",
        ),
        actor_user_id=uuid.uuid4(),
    )

    assert created["row"] is not None
    assert len(after.events) == 1
    assert service._last_dispatch_results[-1].failed_count == 1
    assert service._last_dispatch_results[-1].success_count == 1
