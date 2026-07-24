"""Notification Domain Foundation — EventDispatcher consumer tests (TASK-047)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock

import pytest

from app.core.enums import (
    ComplaintReceiverType,
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
from app.modules.event_dispatcher import EventDispatcher, EventHandler
from app.modules.notification import (
    InMemoryNotificationStore,
    Notification,
    NotificationEventHandler,
    NotificationFactory,
    NotificationSeverity,
    NotificationType,
    register_notification_handler,
)
from app.modules.routing import ComplaintRoute


def _source() -> EventSourceRef:
    return EventSourceRef(
        source_type=ComplaintSourceType.CUSTOMER.value,
        source_id=uuid.uuid4(),
    )


def _target() -> EventTargetRef:
    return EventTargetRef(
        target_type=ComplaintTargetType.BRANCH.value,
        target_id=uuid.uuid4(),
    )


def _route(receiver_id: uuid.UUID | None = None) -> ComplaintRoute:
    rid = receiver_id or uuid.uuid4()
    return ComplaintRoute(
        receiver_type=ComplaintReceiverType.BRANCH,
        receiver_id=rid,
        assignment_context={"branchId": str(rid)},
        routing_reason="CUSTOMER->BRANCH",
    )


def _event_kwargs(**overrides: object) -> dict[str, object]:
    complaint_id = uuid.uuid4()
    data: dict[str, object] = {
        "complaint_id": complaint_id,
        "complaint_number": "CMP-NOTIF0001",
        "current_status": ComplaintStatus.NEW.value,
        "priority": "HIGH",
        "source": _source(),
        "target": _target(),
        "routing": _route(),
        "payload": {"actorUserId": str(uuid.uuid4())},
        "occurred_at": datetime.now(UTC),
    }
    data.update(overrides)
    return data


@pytest.fixture()
def store() -> InMemoryNotificationStore:
    return InMemoryNotificationStore()


@pytest.fixture()
def handler(store: InMemoryNotificationStore) -> NotificationEventHandler:
    return NotificationEventHandler(store=store)


def test_handler_registration_pass(handler: NotificationEventHandler) -> None:
    dispatcher = EventDispatcher()
    registered = register_notification_handler(dispatcher, handler=handler)
    assert registered is handler
    assert isinstance(handler, EventHandler)
    assert dispatcher.registered_handlers() == [handler]
    # Idempotent — does not double-register.
    again = register_notification_handler(dispatcher, handler=handler)
    assert again is handler
    assert len(dispatcher.registered_handlers()) == 1


def test_notification_factory_pass() -> None:
    event = ComplaintEventFactory.create_created(**_event_kwargs())
    notification = NotificationFactory.from_event(event)
    assert isinstance(notification, Notification)
    assert notification.notification_type == NotificationType.COMPLAINT_CREATED
    assert notification.source_event == event.event_id
    assert notification.severity == NotificationSeverity.HIGH
    assert "CMP-NOTIF0001" in notification.message
    assert notification.recipient.startswith("receiver:BRANCH:")
    assert notification.payload["complaintNumber"] == "CMP-NOTIF0001"


@pytest.mark.parametrize(
    ("builder", "event_type", "notif_type", "status"),
    [
        (
            ComplaintEventFactory.create_created,
            ComplaintEventType.CREATED,
            NotificationType.COMPLAINT_CREATED,
            ComplaintStatus.NEW.value,
        ),
        (
            ComplaintEventFactory.create_assigned,
            ComplaintEventType.ASSIGNED,
            NotificationType.COMPLAINT_ASSIGNED,
            ComplaintStatus.ASSIGNED.value,
        ),
        (
            ComplaintEventFactory.create_accepted,
            ComplaintEventType.ACCEPTED,
            NotificationType.COMPLAINT_ACCEPTED,
            ComplaintStatus.IN_PROGRESS.value,
        ),
        (
            ComplaintEventFactory.create_in_progress,
            ComplaintEventType.IN_PROGRESS,
            NotificationType.COMPLAINT_IN_PROGRESS,
            ComplaintStatus.IN_PROGRESS.value,
        ),
        (
            ComplaintEventFactory.create_resolved,
            ComplaintEventType.RESOLVED,
            NotificationType.COMPLAINT_RESOLVED,
            ComplaintStatus.RESOLVED.value,
        ),
        (
            ComplaintEventFactory.create_closed,
            ComplaintEventType.CLOSED,
            NotificationType.COMPLAINT_CLOSED,
            ComplaintStatus.CLOSED.value,
        ),
        (
            ComplaintEventFactory.create_escalated,
            ComplaintEventType.ESCALATED,
            NotificationType.COMPLAINT_ESCALATED,
            ComplaintStatus.ESCALATED.value,
        ),
    ],
)
def test_factory_all_supported_events(
    builder: Any,
    event_type: ComplaintEventType,
    notif_type: NotificationType,
    status: str,
) -> None:
    event = builder(**_event_kwargs(current_status=status))
    assert event.event_type == event_type
    notification = NotificationFactory.from_event(event)
    assert notification.notification_type == notif_type
    assert notification.source_event == event.event_id
    if event_type == ComplaintEventType.ESCALATED:
        assert notification.severity == NotificationSeverity.CRITICAL


@pytest.mark.parametrize(
    ("builder", "notif_type", "status"),
    [
        (
            ComplaintEventFactory.create_created,
            NotificationType.COMPLAINT_CREATED,
            ComplaintStatus.NEW.value,
        ),
        (
            ComplaintEventFactory.create_assigned,
            NotificationType.COMPLAINT_ASSIGNED,
            ComplaintStatus.ASSIGNED.value,
        ),
        (
            ComplaintEventFactory.create_accepted,
            NotificationType.COMPLAINT_ACCEPTED,
            ComplaintStatus.IN_PROGRESS.value,
        ),
        (
            ComplaintEventFactory.create_in_progress,
            NotificationType.COMPLAINT_IN_PROGRESS,
            ComplaintStatus.IN_PROGRESS.value,
        ),
        (
            ComplaintEventFactory.create_resolved,
            NotificationType.COMPLAINT_RESOLVED,
            ComplaintStatus.RESOLVED.value,
        ),
        (
            ComplaintEventFactory.create_closed,
            NotificationType.COMPLAINT_CLOSED,
            ComplaintStatus.CLOSED.value,
        ),
        (
            ComplaintEventFactory.create_escalated,
            NotificationType.COMPLAINT_ESCALATED,
            ComplaintStatus.ESCALATED.value,
        ),
    ],
)
def test_handler_builds_notification_for_each_event(
    handler: NotificationEventHandler,
    store: InMemoryNotificationStore,
    builder: Any,
    notif_type: NotificationType,
    status: str,
) -> None:
    event = builder(**_event_kwargs(current_status=status))
    handler.handle(event)
    assert len(store) == 1
    built = store.all()[0]
    assert built.notification_type == notif_type
    assert built.source_event == event.event_id


def test_handler_ignores_non_complaint_event(
    handler: NotificationEventHandler,
    store: InMemoryNotificationStore,
) -> None:
    handler.handle({"not": "a complaint event"})
    assert len(store) == 0


def test_dispatcher_integration_pass(
    handler: NotificationEventHandler,
    store: InMemoryNotificationStore,
) -> None:
    dispatcher = EventDispatcher()
    register_notification_handler(dispatcher, handler=handler)
    event = ComplaintEventFactory.create_created(**_event_kwargs())
    result = dispatcher.dispatch(event)
    assert result.ok is True
    assert result.success_count == 1
    assert len(store) == 1
    assert store.all()[0].notification_type == NotificationType.COMPLAINT_CREATED


def test_complaint_service_does_not_import_notification() -> None:
    import app.modules.complaints.service as complaint_service_mod

    source = open(complaint_service_mod.__file__, encoding="utf-8").read()
    assert "notification" not in source.lower()
    assert "Notification" not in source


def test_complaint_service_dispatch_builds_notification_via_wiring() -> None:
    """Producer path + injected dispatcher → Notification built; service unaware."""
    from app.modules.complaints.schemas import ComplaintCreateRequest
    from app.modules.complaints.service import ComplaintService

    customer_id = uuid.uuid4()
    branch_id = uuid.uuid4()
    created: dict[str, Any] = {}

    def _add(complaint: Any) -> Any:
        now = datetime.now(UTC)
        complaint.id = uuid.uuid4()  # type: ignore[attr-defined]
        complaint.complaint_number = "CMP-NOTIFCREATE"  # type: ignore[attr-defined]
        complaint.created_at = now  # type: ignore[attr-defined]
        complaint.updated_at = now  # type: ignore[attr-defined]
        created["row"] = complaint
        return complaint

    repo = MagicMock()
    repo.customer_exists.return_value = True
    repo.branch_exists.return_value = True
    repo.add.side_effect = _add
    repo.refresh.side_effect = lambda c: None

    store = InMemoryNotificationStore()
    dispatcher = EventDispatcher()
    register_notification_handler(
        dispatcher,
        handler=NotificationEventHandler(store=store),
    )

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
            subject="Notify seed",
            description="Creates ComplaintCreated → Notification",
            priority="MEDIUM",
        ),
        actor_user_id=uuid.uuid4(),
    )

    assert len(service._recent_events) == 1
    assert len(store) == 1
    assert store.all()[0].notification_type == NotificationType.COMPLAINT_CREATED
    assert store.all()[0].source_event == service._recent_events[0].event_id


def test_notification_immutable() -> None:
    event = ComplaintEventFactory.create_closed(
        **_event_kwargs(current_status=ComplaintStatus.CLOSED.value)
    )
    notification = NotificationFactory.from_event(event)
    with pytest.raises(Exception):
        notification.title = "mutated"  # type: ignore[misc]
