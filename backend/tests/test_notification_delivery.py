"""Notification Delivery Foundation tests (TASK-049)."""

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
    InMemoryNotificationDeliveryStore,
    InMemoryNotificationIntentStore,
    InMemoryNotificationStore,
    NotificationDelivery,
    NotificationDeliveryFactory,
    NotificationDeliveryStatus,
    NotificationEventHandler,
    NotificationFactory,
    NotificationIntentChannel,
    NotificationIntentFactory,
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


def _intent(
    *,
    notification_type: NotificationType = NotificationType.COMPLAINT_CREATED,
    priority: str = "MEDIUM",
):
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
        complaint_number="CMP-DELIV0001",
        current_status=status_map[notification_type],
        priority=priority,
        source=_source(),
        target=_target(),
        routing=_route(),
        payload={"actorUserId": str(uuid.uuid4())},
        occurred_at=datetime.now(UTC),
    )
    notification = NotificationFactory.from_event(event)
    return NotificationIntentFactory.from_notification(notification)


def test_status_pass() -> None:
    assert list(NotificationDeliveryStatus) == [NotificationDeliveryStatus.PLANNED]
    assert NotificationDeliveryStatus.PLANNED.value == "PLANNED"
    assert not hasattr(NotificationDeliveryStatus, "SENT")
    assert not hasattr(NotificationDeliveryStatus, "FAILED")
    assert not hasattr(NotificationDeliveryStatus, "RETRY")


def test_delivery_creation_pass() -> None:
    intent = _intent()
    deliveries = NotificationDeliveryFactory.from_intent(intent)
    assert len(deliveries) >= 1
    delivery = deliveries[0]
    assert isinstance(delivery, NotificationDelivery)
    assert delivery.intent_id == intent.intent_id
    assert delivery.recipient_key == intent.recipient_key
    assert delivery.template_key == intent.template_key
    assert delivery.priority == intent.priority
    assert delivery.status == NotificationDeliveryStatus.PLANNED


def test_factory_pass() -> None:
    intent = _intent(
        notification_type=NotificationType.COMPLAINT_RESOLVED,
        priority="HIGH",
    )
    deliveries = NotificationDeliveryFactory.from_intent(intent)
    assert all(d.template_key == "complaint.resolved" for d in deliveries)
    assert all(d.status == NotificationDeliveryStatus.PLANNED for d in deliveries)
    assert {d.channel for d in deliveries} == set(intent.preferred_channels)


def test_channel_mapping_pass() -> None:
    intent = _intent(priority="CRITICAL")
    deliveries = NotificationDeliveryFactory.from_intent(intent)
    channels = [d.channel for d in deliveries]
    assert channels == list(intent.preferred_channels)
    assert NotificationIntentChannel.EMAIL in channels
    assert NotificationIntentChannel.SMS in channels
    assert NotificationIntentChannel.WHATSAPP in channels
    assert len(deliveries) == len(set(channels))


def test_delivery_immutable() -> None:
    delivery = NotificationDeliveryFactory.from_intent(_intent())[0]
    with pytest.raises(Exception):
        delivery.status = NotificationDeliveryStatus.PLANNED  # type: ignore[misc]


def test_handler_integration_pass() -> None:
    store = InMemoryNotificationStore()
    intent_store = InMemoryNotificationIntentStore()
    delivery_store = InMemoryNotificationDeliveryStore()
    handler = NotificationEventHandler(
        store=store,
        intent_store=intent_store,
        delivery_store=delivery_store,
    )
    event = ComplaintEventFactory.create_created(
        complaint_id=uuid.uuid4(),
        complaint_number="CMP-DELIVHAND",
        current_status=ComplaintStatus.NEW.value,
        priority="LOW",
        source=_source(),
        target=_target(),
        routing=_route(),
        occurred_at=datetime.now(UTC),
    )
    handler.handle(event)
    assert len(store) == 1
    assert len(intent_store) == 1
    assert len(delivery_store) == len(intent_store.all()[0].preferred_channels)
    assert all(
        d.status == NotificationDeliveryStatus.PLANNED for d in delivery_store.all()
    )
    assert all(
        d.intent_id == intent_store.all()[0].intent_id for d in delivery_store.all()
    )


def test_dispatcher_integration_pass() -> None:
    store = InMemoryNotificationStore()
    intent_store = InMemoryNotificationIntentStore()
    delivery_store = InMemoryNotificationDeliveryStore()
    handler = NotificationEventHandler(
        store=store,
        intent_store=intent_store,
        delivery_store=delivery_store,
    )
    dispatcher = EventDispatcher()
    register_notification_handler(dispatcher, handler=handler)

    event = ComplaintEventFactory.create_assigned(
        complaint_id=uuid.uuid4(),
        complaint_number="CMP-DELIVDISP",
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
    assert len(delivery_store) >= 1
    assert {d.channel for d in delivery_store.all()} == set(
        intent_store.all()[0].preferred_channels
    )


def test_complaint_service_path_builds_deliveries() -> None:
    from app.modules.complaints.schemas import ComplaintCreateRequest
    from app.modules.complaints.service import ComplaintService

    customer_id = uuid.uuid4()
    branch_id = uuid.uuid4()
    created: dict[str, Any] = {}

    def _add(complaint: Any) -> Any:
        now = datetime.now(UTC)
        complaint.id = uuid.uuid4()  # type: ignore[attr-defined]
        complaint.complaint_number = "CMP-DELIVCREATE"  # type: ignore[attr-defined]
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
    delivery_store = InMemoryNotificationDeliveryStore()
    dispatcher = EventDispatcher()
    register_notification_handler(
        dispatcher,
        handler=NotificationEventHandler(
            store=store,
            intent_store=intent_store,
            delivery_store=delivery_store,
        ),
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
            subject="Delivery seed",
            description="Creates Notification + Intent + Delivery",
            priority="MEDIUM",
        ),
        actor_user_id=uuid.uuid4(),
    )

    assert len(store) == 1
    assert len(intent_store) == 1
    assert len(delivery_store) == len(intent_store.all()[0].preferred_channels)
    assert all(
        d.status == NotificationDeliveryStatus.PLANNED for d in delivery_store.all()
    )
