"""Complaint Event Foundation unit tests (TASK-045)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import MappingProxyType

import pytest

from app.core.enums import (
    ComplaintReceiverType,
    ComplaintSourceType,
    ComplaintStatus,
    ComplaintTargetType,
)
from app.modules.complaint_events import (
    ComplaintEvent,
    ComplaintEventFactory,
    ComplaintEventType,
    EventSourceRef,
    EventTargetRef,
    context_ref_for,
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


def _base_kwargs(**overrides: object) -> dict[str, object]:
    complaint_id = uuid.uuid4()
    data: dict[str, object] = {
        "complaint_id": complaint_id,
        "complaint_number": "CMP-EVT00001",
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


def test_complaint_created() -> None:
    event = ComplaintEventFactory.create_created(**_base_kwargs())
    assert event.event_type == ComplaintEventType.CREATED
    assert event.event_type.value == "ComplaintCreated"
    assert event.current_status == ComplaintStatus.NEW.value
    assert event.context_reference == context_ref_for(event.complaint_id)


def test_complaint_assigned() -> None:
    event = ComplaintEventFactory.create_assigned(
        **_base_kwargs(current_status=ComplaintStatus.ASSIGNED.value)
    )
    assert event.event_type == ComplaintEventType.ASSIGNED
    assert event.event_type.value == "ComplaintAssigned"


def test_complaint_accepted() -> None:
    event = ComplaintEventFactory.create_accepted(
        **_base_kwargs(current_status=ComplaintStatus.IN_PROGRESS.value)
    )
    assert event.event_type == ComplaintEventType.ACCEPTED
    assert event.event_type.value == "ComplaintAccepted"


def test_complaint_in_progress() -> None:
    event = ComplaintEventFactory.create_in_progress(
        **_base_kwargs(current_status=ComplaintStatus.IN_PROGRESS.value)
    )
    assert event.event_type == ComplaintEventType.IN_PROGRESS
    assert event.event_type.value == "ComplaintInProgress"


def test_complaint_resolved() -> None:
    event = ComplaintEventFactory.create_resolved(
        **_base_kwargs(current_status=ComplaintStatus.RESOLVED.value)
    )
    assert event.event_type == ComplaintEventType.RESOLVED
    assert event.event_type.value == "ComplaintResolved"


def test_complaint_closed() -> None:
    event = ComplaintEventFactory.create_closed(
        **_base_kwargs(current_status=ComplaintStatus.CLOSED.value)
    )
    assert event.event_type == ComplaintEventType.CLOSED
    assert event.event_type.value == "ComplaintClosed"


def test_complaint_escalated() -> None:
    event = ComplaintEventFactory.create_escalated(
        **_base_kwargs(current_status=ComplaintStatus.ESCALATED.value)
    )
    assert event.event_type == ComplaintEventType.ESCALATED
    assert event.event_type.value == "ComplaintEscalated"


def test_complaint_event_immutable() -> None:
    event = ComplaintEventFactory.create_created(**_base_kwargs())
    assert isinstance(event, ComplaintEvent)
    assert isinstance(event.payload, MappingProxyType)

    with pytest.raises(Exception):
        event.event_type = ComplaintEventType.CLOSED  # type: ignore[misc]

    with pytest.raises(TypeError):
        event.payload["mutated"] = True  # type: ignore[index]

    with pytest.raises(Exception):
        event.source.source_type = "SYSTEM"  # type: ignore[misc]


def test_event_fields_complete() -> None:
    event_id = uuid.uuid4()
    occurred = datetime(2026, 7, 24, 2, 0, tzinfo=UTC)
    kwargs = _base_kwargs(event_id=event_id, occurred_at=occurred)
    event = ComplaintEventFactory.create_created(**kwargs)

    assert event.event_id == event_id
    assert event.occurred_at == occurred
    assert event.complaint_id == kwargs["complaint_id"]
    assert event.complaint_number == "CMP-EVT00001"
    assert event.priority == "HIGH"
    assert isinstance(event.source, EventSourceRef)
    assert isinstance(event.target, EventTargetRef)
    assert event.routing is not None
    assert event.context_reference.startswith("complaint:")
    assert "actorUserId" in event.payload


def test_as_dict_is_read_only_view() -> None:
    event = ComplaintEventFactory.create_created(**_base_kwargs())
    view = event.as_dict()
    assert view["eventType"] == "ComplaintCreated"
    with pytest.raises(TypeError):
        view["eventType"] = "x"  # type: ignore[index]


def test_factory_allows_null_routing() -> None:
    event = ComplaintEventFactory.create_assigned(
        **_base_kwargs(routing=None, current_status=ComplaintStatus.ASSIGNED.value)
    )
    assert event.routing is None
    assert event.as_dict()["routing"] is None


def test_complaint_service_emits_created_event() -> None:
    """ComplaintService may create events on create (in-memory only)."""
    from unittest.mock import MagicMock

    from app.modules.complaints.schemas import ComplaintCreateRequest
    from app.modules.complaints.service import ComplaintService

    actor_id = uuid.uuid4()
    customer_id = uuid.uuid4()
    branch_id = uuid.uuid4()
    now = datetime.now(UTC)
    created: dict[str, object] = {}

    def _add(complaint: object) -> None:
        complaint.id = uuid.uuid4()  # type: ignore[attr-defined]
        complaint.created_at = now  # type: ignore[attr-defined]
        complaint.updated_at = now  # type: ignore[attr-defined]
        created["row"] = complaint

    repo = MagicMock()
    repo.customer_exists.return_value = True
    repo.branch_exists.return_value = True
    repo.add.side_effect = _add
    repo.refresh.side_effect = lambda c: None

    service = ComplaintService(repo, sla_service=MagicMock())
    service.create(
        ComplaintCreateRequest(
            sourceType="CUSTOMER",
            sourceId=customer_id,
            targetType="BRANCH",
            targetId=branch_id,
            subject="Event seed",
            description="Creates ComplaintCreated",
            priority="MEDIUM",
        ),
        actor_user_id=actor_id,
    )

    assert len(service._recent_events) == 1
    assert service._recent_events[0].event_type == ComplaintEventType.CREATED
    assert service._recent_events[0].complaint_id == created["row"].id  # type: ignore[attr-defined]


def test_complaint_service_emits_accepted_and_in_progress() -> None:
    """ASSIGNED → IN_PROGRESS emits Accepted + InProgress (service-owned path)."""
    from types import SimpleNamespace
    from unittest.mock import MagicMock

    from app.modules.complaints.schemas import ComplaintStatusChangeRequest
    from app.modules.complaints.service import ComplaintService

    complaint_id = uuid.uuid4()
    source_id = uuid.uuid4()
    target_id = uuid.uuid4()
    now = datetime.now(UTC)
    complaint = SimpleNamespace(
        id=complaint_id,
        complaint_number="CMP-EVTSTATUS",
        customer_id=source_id,
        branch_id=target_id,
        source_type=ComplaintSourceType.CUSTOMER.value,
        source_id=source_id,
        target_type=ComplaintTargetType.BRANCH.value,
        target_id=target_id,
        subject="s",
        description="d",
        status=ComplaintStatus.ASSIGNED.value,
        priority="HIGH",
        channel=None,
        category=None,
        reported_at=now,
        closed_at=None,
        closed_by=None,
        closure_notes=None,
        created_at=now,
        created_by=uuid.uuid4(),
        updated_at=now,
        updated_by=uuid.uuid4(),
    )

    repo = MagicMock()
    repo.get_by_id.return_value = complaint
    repo.refresh.side_effect = lambda c: None
    service = ComplaintService(repo, sla_service=MagicMock())

    service.change_status(
        complaint_id,
        ComplaintStatusChangeRequest(status=ComplaintStatus.IN_PROGRESS),
        actor_user_id=uuid.uuid4(),
    )

    types = [e.event_type for e in service._recent_events]
    assert ComplaintEventType.ACCEPTED in types
    assert ComplaintEventType.IN_PROGRESS in types
