"""Notification Intent Foundation tests (TASK-048)."""

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
    EventSourceRef,
    EventTargetRef,
)
from app.modules.event_dispatcher import EventDispatcher
from app.modules.notification import (
    InMemoryNotificationIntentStore,
    InMemoryNotificationStore,
    Notification,
    NotificationEventHandler,
    NotificationFactory,
    NotificationIntent,
    NotificationIntentChannel,
    NotificationIntentFactory,
    NotificationIntentPriority,
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


def _route() -> ComplaintRoute:
    rid = uuid.uuid4()
    return ComplaintRoute(
        receiver_type=ComplaintReceiverType.BRANCH,
        receiver_id=rid,
        assignment_context={"branchId": str(rid)},
        routing_reason="CUSTOMER->BRANCH",
    )


def _notification(
    *,
    notification_type: NotificationType = NotificationType.COMPLAINT_CREATED,
    priority: str = "MEDIUM",
) -> Notification:
    builders = {
        NotificationType.COMPLAINT_CREATED: ComplaintEventFactory.create_created,
        NotificationType.COMPLAINT_ASSIGNED: ComplaintEventFactory.create_assigned,
        NotificationType.COMPLAINT_ACCEPTED: ComplaintEventFactory.create_accepted,
        NotificationType.COMPLAINT_IN_PROGRESS: ComplaintEventFactory.create_in_progress,
        NotificationType.COMPLAINT_RESOLVED: ComplaintEventFactory.create_resolved,
        NotificationType.COMPLAINT_CLOSED: ComplaintEventFactory.create_closed,
        NotificationType.COMPLAINT_ESCALATED: ComplaintEventFactory.create_escalated,
    }
    status_map = {
        NotificationType.COMPLAINT_CREATED: ComplaintStatus.NEW.value,
        NotificationType.COMPLAINT_ASSIGNED: ComplaintStatus.ASSIGNED.value,
        NotificationType.COMPLAINT_ACCEPTED: ComplaintStatus.IN_PROGRESS.value,
        NotificationType.COMPLAINT_IN_PROGRESS: ComplaintStatus.IN_PROGRESS.value,
        NotificationType.COMPLAINT_RESOLVED: ComplaintStatus.RESOLVED.value,
        NotificationType.COMPLAINT_CLOSED: ComplaintStatus.CLOSED.value,
        NotificationType.COMPLAINT_ESCALATED: ComplaintStatus.ESCALATED.value,
    }
    event = builders[notification_type](
        complaint_id=uuid.uuid4(),
        complaint_number="CMP-INTENT0001",
        current_status=status_map[notification_type],
        priority=priority,
        source=_source(),
        target=_target(),
        routing=_route(),
        payload={"actorUserId": str(uuid.uuid4())},
        occurred_at=datetime.now(UTC),
    )
    return NotificationFactory.from_event(event)


def test_channel_enum_pass() -> None:
    values = {c.value for c in NotificationIntentChannel}
    assert values == {"EMAIL", "WHATSAPP", "PUSH", "SMS", "WEBSOCKET"}
    assert not hasattr(NotificationIntentChannel, "send")
    assert not hasattr(NotificationIntentChannel, "deliver")


def test_intent_creation_pass() -> None:
    notification = _notification()
    intent = NotificationIntentFactory.from_notification(notification)
    assert isinstance(intent, NotificationIntent)
    assert intent.notification_id == notification.notification_id
    assert intent.recipient_key == notification.recipient
    assert intent.template_key == "complaint.created"
    assert intent.priority == NotificationIntentPriority.MEDIUM
    assert NotificationIntentChannel.EMAIL in intent.preferred_channels


def test_factory_pass() -> None:
    notification = _notification(
        notification_type=NotificationType.COMPLAINT_RESOLVED,
        priority="HIGH",
    )
    intent = NotificationIntentFactory.from_notification(notification)
    assert intent.template_key == "complaint.resolved"
    assert intent.priority == NotificationIntentPriority.HIGH
    assert "title" in intent.variables
    assert "message" in intent.variables
    assert intent.metadata["notificationType"] == "ComplaintResolved"


@pytest.mark.parametrize(
    ("notif_type", "template_key"),
    [
        (NotificationType.COMPLAINT_CREATED, "complaint.created"),
        (NotificationType.COMPLAINT_ASSIGNED, "complaint.assigned"),
        (NotificationType.COMPLAINT_ACCEPTED, "complaint.accepted"),
        (NotificationType.COMPLAINT_IN_PROGRESS, "complaint.in_progress"),
        (NotificationType.COMPLAINT_RESOLVED, "complaint.resolved"),
        (NotificationType.COMPLAINT_CLOSED, "complaint.closed"),
        (NotificationType.COMPLAINT_ESCALATED, "complaint.escalated"),
    ],
)
def test_template_mapping_pass(
    notif_type: NotificationType,
    template_key: str,
) -> None:
    assert NotificationIntentFactory.template_key_for(notif_type) == template_key
    notification = _notification(notification_type=notif_type, priority="MEDIUM")
    intent = NotificationIntentFactory.from_notification(notification)
    assert intent.template_key == template_key


@pytest.mark.parametrize(
    ("priority", "expected_intent_priority", "must_include"),
    [
        ("LOW", NotificationIntentPriority.LOW, (NotificationIntentChannel.EMAIL,)),
        (
            "MEDIUM",
            NotificationIntentPriority.MEDIUM,
            (NotificationIntentChannel.EMAIL, NotificationIntentChannel.WEBSOCKET),
        ),
        (
            "HIGH",
            NotificationIntentPriority.HIGH,
            (
                NotificationIntentChannel.EMAIL,
                NotificationIntentChannel.PUSH,
            ),
        ),
        (
            "CRITICAL",
            NotificationIntentPriority.CRITICAL,
            (
                NotificationIntentChannel.EMAIL,
                NotificationIntentChannel.WHATSAPP,
                NotificationIntentChannel.SMS,
            ),
        ),
    ],
)
def test_priority_mapping_pass(
    priority: str,
    expected_intent_priority: NotificationIntentPriority,
    must_include: tuple[NotificationIntentChannel, ...],
) -> None:
    notification = _notification(priority=priority)
    intent = NotificationIntentFactory.from_notification(notification)
    assert intent.priority == expected_intent_priority
    for channel in must_include:
        assert channel in intent.preferred_channels


def test_escalated_maps_to_critical_priority() -> None:
    notification = _notification(
        notification_type=NotificationType.COMPLAINT_ESCALATED,
        priority="MEDIUM",
    )
    intent = NotificationIntentFactory.from_notification(notification)
    assert intent.priority == NotificationIntentPriority.CRITICAL
    assert NotificationIntentChannel.SMS in intent.preferred_channels


def test_intent_immutable() -> None:
    intent = NotificationIntentFactory.from_notification(_notification())
    with pytest.raises(Exception):
        intent.template_key = "mutated"  # type: ignore[misc]


def test_dispatcher_integration_pass() -> None:
    store = InMemoryNotificationStore()
    intent_store = InMemoryNotificationIntentStore()
    handler = NotificationEventHandler(store=store, intent_store=intent_store)
    dispatcher = EventDispatcher()
    register_notification_handler(dispatcher, handler=handler)

    event = ComplaintEventFactory.create_assigned(
        complaint_id=uuid.uuid4(),
        complaint_number="CMP-INTENTDISP",
        current_status=ComplaintStatus.ASSIGNED.value,
        priority="HIGH",
        source=_source(),
        target=_target(),
        routing=_route(),
        occurred_at=datetime.now(UTC),
    )
    result = dispatcher.dispatch(event)
    assert result.ok is True
    assert len(store) == 1
    assert len(intent_store) == 1
    intent = intent_store.all()[0]
    assert intent.notification_id == store.all()[0].notification_id
    assert intent.template_key == "complaint.assigned"
    assert intent.priority == NotificationIntentPriority.HIGH


def test_complaint_service_path_builds_intent() -> None:
    from app.modules.complaints.schemas import ComplaintCreateRequest
    from app.modules.complaints.service import ComplaintService

    customer_id = uuid.uuid4()
    branch_id = uuid.uuid4()
    created: dict[str, Any] = {}

    def _add(complaint: Any) -> Any:
        now = datetime.now(UTC)
        complaint.id = uuid.uuid4()  # type: ignore[attr-defined]
        complaint.complaint_number = "CMP-INTENTCREATE"  # type: ignore[attr-defined]
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
    intent_store = InMemoryNotificationIntentStore()
    dispatcher = EventDispatcher()
    register_notification_handler(
        dispatcher,
        handler=NotificationEventHandler(store=store, intent_store=intent_store),
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
            subject="Intent seed",
            description="Creates Notification + Intent",
            priority="LOW",
        ),
        actor_user_id=uuid.uuid4(),
    )

    assert len(store) == 1
    assert len(intent_store) == 1
    assert intent_store.all()[0].template_key == "complaint.created"
    assert intent_store.all()[0].priority == NotificationIntentPriority.LOW
