"""Dashboard Projection Foundation tests (TASK-050)."""

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
from app.modules.dashboard import (
    DashboardProjection,
    DashboardProjectionHandler,
    DashboardProjectionStore,
    register_dashboard_projection_handler,
)
from app.modules.event_dispatcher import EventDispatcher, EventHandler
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


def _base(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "complaint_id": uuid.uuid4(),
        "complaint_number": "CMP-DASH0001",
        "current_status": ComplaintStatus.NEW.value,
        "priority": "MEDIUM",
        "source": _source(),
        "target": _target(),
        "routing": _route(),
        "occurred_at": datetime.now(UTC),
    }
    data.update(overrides)
    return data


@pytest.fixture()
def store() -> DashboardProjectionStore:
    return DashboardProjectionStore()


@pytest.fixture()
def handler(store: DashboardProjectionStore) -> DashboardProjectionHandler:
    return DashboardProjectionHandler(store=store)


def test_projection_initialization_pass(store: DashboardProjectionStore) -> None:
    snap = store.snapshot()
    assert isinstance(snap, DashboardProjection)
    assert snap.total_complaints == 0
    assert snap.open_complaints == 0
    assert snap.assigned_complaints == 0
    assert snap.in_progress_complaints == 0
    assert snap.resolved_complaints == 0
    assert snap.closed_complaints == 0
    assert snap.escalated_complaints == 0
    assert snap.breached_sla == 0
    assert snap.updated_at.tzinfo is not None


def test_created_pass(handler: DashboardProjectionHandler, store: DashboardProjectionStore) -> None:
    event = ComplaintEventFactory.create_created(**_base())
    handler.handle(event)
    snap = store.snapshot()
    assert snap.total_complaints == 1
    assert snap.open_complaints == 1
    assert snap.assigned_complaints == 0


def test_assigned_pass(handler: DashboardProjectionHandler, store: DashboardProjectionStore) -> None:
    handler.handle(ComplaintEventFactory.create_created(**_base()))
    handler.handle(
        ComplaintEventFactory.create_assigned(
            **_base(
                current_status=ComplaintStatus.ASSIGNED.value,
                payload={
                    "fromStatus": ComplaintStatus.NEW.value,
                    "toStatus": ComplaintStatus.ASSIGNED.value,
                },
            )
        )
    )
    snap = store.snapshot()
    assert snap.total_complaints == 1
    assert snap.open_complaints == 1
    assert snap.assigned_complaints == 1


def test_accepted_pass(handler: DashboardProjectionHandler, store: DashboardProjectionStore) -> None:
    """Accepted is a marker; counters move on InProgress (no double-count)."""
    handler.handle(ComplaintEventFactory.create_created(**_base()))
    handler.handle(
        ComplaintEventFactory.create_assigned(
            **_base(
                current_status=ComplaintStatus.ASSIGNED.value,
                payload={"fromStatus": ComplaintStatus.NEW.value},
            )
        )
    )
    before = store.snapshot()
    handler.handle(
        ComplaintEventFactory.create_accepted(
            **_base(
                current_status=ComplaintStatus.IN_PROGRESS.value,
                payload={
                    "fromStatus": ComplaintStatus.ASSIGNED.value,
                    "toStatus": ComplaintStatus.IN_PROGRESS.value,
                },
            )
        )
    )
    after_accepted = store.snapshot()
    assert after_accepted.assigned_complaints == before.assigned_complaints
    assert after_accepted.in_progress_complaints == before.in_progress_complaints
    assert after_accepted.updated_at >= before.updated_at


def test_in_progress_pass(
    handler: DashboardProjectionHandler, store: DashboardProjectionStore
) -> None:
    handler.handle(ComplaintEventFactory.create_created(**_base()))
    handler.handle(
        ComplaintEventFactory.create_assigned(
            **_base(
                current_status=ComplaintStatus.ASSIGNED.value,
                payload={"fromStatus": ComplaintStatus.NEW.value},
            )
        )
    )
    handler.handle(
        ComplaintEventFactory.create_accepted(
            **_base(
                current_status=ComplaintStatus.IN_PROGRESS.value,
                payload={"fromStatus": ComplaintStatus.ASSIGNED.value},
            )
        )
    )
    handler.handle(
        ComplaintEventFactory.create_in_progress(
            **_base(
                current_status=ComplaintStatus.IN_PROGRESS.value,
                payload={
                    "fromStatus": ComplaintStatus.ASSIGNED.value,
                    "toStatus": ComplaintStatus.IN_PROGRESS.value,
                },
            )
        )
    )
    snap = store.snapshot()
    assert snap.assigned_complaints == 0
    assert snap.in_progress_complaints == 1
    assert snap.open_complaints == 1


def test_resolved_pass(
    handler: DashboardProjectionHandler, store: DashboardProjectionStore
) -> None:
    handler.handle(ComplaintEventFactory.create_created(**_base()))
    handler.handle(
        ComplaintEventFactory.create_in_progress(
            **_base(
                current_status=ComplaintStatus.IN_PROGRESS.value,
                payload={"fromStatus": ComplaintStatus.ASSIGNED.value},
            )
        )
    )
    # Seed assigned/in_progress consistently for resolved transition.
    store.reset()
    handler.handle(ComplaintEventFactory.create_created(**_base()))
    handler.handle(
        ComplaintEventFactory.create_assigned(
            **_base(
                current_status=ComplaintStatus.ASSIGNED.value,
                payload={"fromStatus": ComplaintStatus.NEW.value},
            )
        )
    )
    handler.handle(
        ComplaintEventFactory.create_in_progress(
            **_base(
                current_status=ComplaintStatus.IN_PROGRESS.value,
                payload={"fromStatus": ComplaintStatus.ASSIGNED.value},
            )
        )
    )
    handler.handle(
        ComplaintEventFactory.create_resolved(
            **_base(
                current_status=ComplaintStatus.RESOLVED.value,
                payload={
                    "fromStatus": ComplaintStatus.IN_PROGRESS.value,
                    "toStatus": ComplaintStatus.RESOLVED.value,
                },
            )
        )
    )
    snap = store.snapshot()
    assert snap.in_progress_complaints == 0
    assert snap.resolved_complaints == 1
    assert snap.open_complaints == 0


def test_closed_pass(handler: DashboardProjectionHandler, store: DashboardProjectionStore) -> None:
    handler.handle(ComplaintEventFactory.create_created(**_base()))
    handler.handle(
        ComplaintEventFactory.create_closed(
            **_base(
                current_status=ComplaintStatus.CLOSED.value,
                payload={
                    "fromStatus": ComplaintStatus.IN_PROGRESS.value,
                    "toStatus": ComplaintStatus.CLOSED.value,
                },
            )
        )
    )
    # Without prior in_progress bump, closed increments and open decrements via fromStatus.
    # Seed a realistic path:
    store.reset()
    handler.handle(ComplaintEventFactory.create_created(**_base()))
    handler.handle(
        ComplaintEventFactory.create_assigned(
            **_base(
                current_status=ComplaintStatus.ASSIGNED.value,
                payload={"fromStatus": ComplaintStatus.NEW.value},
            )
        )
    )
    handler.handle(
        ComplaintEventFactory.create_in_progress(
            **_base(
                current_status=ComplaintStatus.IN_PROGRESS.value,
                payload={"fromStatus": ComplaintStatus.ASSIGNED.value},
            )
        )
    )
    handler.handle(
        ComplaintEventFactory.create_closed(
            **_base(
                current_status=ComplaintStatus.CLOSED.value,
                payload={
                    "fromStatus": ComplaintStatus.IN_PROGRESS.value,
                    "toStatus": ComplaintStatus.CLOSED.value,
                },
            )
        )
    )
    snap = store.snapshot()
    assert snap.closed_complaints == 1
    assert snap.in_progress_complaints == 0
    assert snap.open_complaints == 0
    assert snap.total_complaints == 1


def test_escalated_pass(
    handler: DashboardProjectionHandler, store: DashboardProjectionStore
) -> None:
    handler.handle(ComplaintEventFactory.create_created(**_base()))
    handler.handle(
        ComplaintEventFactory.create_assigned(
            **_base(
                current_status=ComplaintStatus.ASSIGNED.value,
                payload={"fromStatus": ComplaintStatus.NEW.value},
            )
        )
    )
    handler.handle(
        ComplaintEventFactory.create_escalated(
            **_base(
                current_status=ComplaintStatus.ESCALATED.value,
                payload={
                    "fromStatus": ComplaintStatus.ASSIGNED.value,
                    "toStatus": ComplaintStatus.ESCALATED.value,
                },
            )
        )
    )
    snap = store.snapshot()
    assert snap.escalated_complaints == 1
    assert snap.assigned_complaints == 0
    assert snap.open_complaints == 1


def test_dispatcher_integration_pass(store: DashboardProjectionStore) -> None:
    handler = DashboardProjectionHandler(store=store)
    assert isinstance(handler, EventHandler)
    dispatcher = EventDispatcher()
    register_dashboard_projection_handler(dispatcher, handler=handler)

    dispatcher.dispatch(ComplaintEventFactory.create_created(**_base()))
    dispatcher.dispatch(
        ComplaintEventFactory.create_assigned(
            **_base(
                current_status=ComplaintStatus.ASSIGNED.value,
                payload={"fromStatus": ComplaintStatus.NEW.value},
            )
        )
    )
    snap = store.snapshot()
    assert snap.total_complaints == 1
    assert snap.assigned_complaints == 1


def test_projection_immutable(store: DashboardProjectionStore) -> None:
    snap = store.snapshot()
    with pytest.raises(Exception):
        snap.total_complaints = 99  # type: ignore[misc]


def test_handler_ignores_non_complaint_event(
    handler: DashboardProjectionHandler, store: DashboardProjectionStore
) -> None:
    handler.handle({"not": "complaint"})
    assert store.snapshot().total_complaints == 0


def test_complaint_service_path_updates_projection() -> None:
    from app.modules.complaints.schemas import ComplaintCreateRequest
    from app.modules.complaints.service import ComplaintService

    customer_id = uuid.uuid4()
    branch_id = uuid.uuid4()

    def _add(complaint: Any) -> Any:
        now = datetime.now(UTC)
        complaint.id = uuid.uuid4()  # type: ignore[attr-defined]
        complaint.complaint_number = "CMP-DASHCREATE"  # type: ignore[attr-defined]
        complaint.created_at = now  # type: ignore[attr-defined]
        complaint.updated_at = now  # type: ignore[attr-defined]
        return complaint

    repo = MagicMock()
    repo.customer_exists.return_value = True
    repo.branch_exists.return_value = True
    repo.add.side_effect = _add
    repo.refresh.side_effect = lambda c: None

    store = DashboardProjectionStore()
    dispatcher = EventDispatcher()
    register_dashboard_projection_handler(
        dispatcher,
        handler=DashboardProjectionHandler(store=store),
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
            subject="Projection seed",
            description="Creates ComplaintCreated → projection update",
            priority="LOW",
        ),
        actor_user_id=uuid.uuid4(),
    )

    assert store.snapshot().total_complaints == 1
    assert store.snapshot().open_complaints == 1


def test_store_does_not_import_complaint_service() -> None:
    import app.modules.dashboard.projection_handler as handler_mod
    import app.modules.dashboard.projection_store as store_mod

    store_src = open(store_mod.__file__, encoding="utf-8").read()
    handler_src = open(handler_mod.__file__, encoding="utf-8").read()
    assert "from app.modules.complaints" not in store_src
    assert "from app.modules.complaints" not in handler_src
    assert "import ComplaintService" not in store_src
    assert "import ComplaintService" not in handler_src
    assert "complaint_service" not in store_src
    assert "complaint_service" not in handler_src
