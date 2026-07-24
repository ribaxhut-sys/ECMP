"""KPI Projection Foundation tests (TASK-051)."""

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
from app.modules.event_dispatcher import EventDispatcher, EventHandler
from app.modules.kpi import (
    KpiProjection,
    KpiProjectionHandler,
    KpiProjectionStore,
    register_kpi_projection_handler,
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


def _base(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "complaint_id": uuid.uuid4(),
        "complaint_number": "CMP-KPI0001",
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
def store() -> KpiProjectionStore:
    return KpiProjectionStore()


@pytest.fixture()
def handler(store: KpiProjectionStore) -> KpiProjectionHandler:
    return KpiProjectionHandler(store=store)


def test_initialization_pass(store: KpiProjectionStore) -> None:
    snap = store.snapshot()
    assert isinstance(snap, KpiProjection)
    assert snap.total_received == 0
    assert snap.total_closed == 0
    assert snap.total_resolved == 0
    assert snap.total_escalated == 0
    assert snap.current_open == 0
    assert snap.current_in_progress == 0
    assert snap.sla_breached == 0
    assert snap.closure_rate == 0.0
    assert snap.resolution_rate == 0.0
    assert snap.updated_at.tzinfo is not None


def test_created_pass(handler: KpiProjectionHandler, store: KpiProjectionStore) -> None:
    event = ComplaintEventFactory.create_created(**_base())
    handler.handle(event)
    snap = store.snapshot()
    assert snap.total_received == 1
    assert snap.current_open == 1
    assert snap.current_in_progress == 0
    assert snap.closure_rate == 0.0
    assert snap.resolution_rate == 0.0


def test_resolved_pass(
    handler: KpiProjectionHandler, store: KpiProjectionStore
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
    assert snap.total_received == 1
    assert snap.total_resolved == 1
    assert snap.current_in_progress == 0
    assert snap.current_open == 0
    assert snap.resolution_rate == 1.0


def test_closed_pass(handler: KpiProjectionHandler, store: KpiProjectionStore) -> None:
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
    assert snap.total_closed == 1
    assert snap.current_in_progress == 0
    assert snap.current_open == 0
    assert snap.total_received == 1
    assert snap.closure_rate == 1.0


def test_escalated_pass(
    handler: KpiProjectionHandler, store: KpiProjectionStore
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
    assert snap.total_escalated == 1
    assert snap.current_open == 1
    assert snap.current_in_progress == 0


def test_rate_calculation_pass(
    handler: KpiProjectionHandler, store: KpiProjectionStore
) -> None:
    for i in range(4):
        handler.handle(
            ComplaintEventFactory.create_created(
                **_base(complaint_number=f"CMP-KPI-R{i}")
            )
        )

    # Resolve 2 of 4
    for _ in range(2):
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

    # Close 1 of 4
    handler.handle(
        ComplaintEventFactory.create_closed(
            **_base(
                current_status=ComplaintStatus.CLOSED.value,
                payload={
                    "fromStatus": ComplaintStatus.RESOLVED.value,
                    "toStatus": ComplaintStatus.CLOSED.value,
                },
            )
        )
    )

    snap = store.snapshot()
    assert snap.total_received == 4
    assert snap.total_resolved == 2
    assert snap.total_closed == 1
    assert snap.resolution_rate == 0.5
    assert snap.closure_rate == 0.25


def test_divide_by_zero_pass(store: KpiProjectionStore) -> None:
    snap = store.snapshot()
    assert snap.total_received == 0
    assert snap.closure_rate == 0.0
    assert snap.resolution_rate == 0.0


def test_dispatcher_integration_pass(store: KpiProjectionStore) -> None:
    handler = KpiProjectionHandler(store=store)
    assert isinstance(handler, EventHandler)
    dispatcher = EventDispatcher()
    register_kpi_projection_handler(dispatcher, handler=handler)

    dispatcher.dispatch(ComplaintEventFactory.create_created(**_base()))
    dispatcher.dispatch(
        ComplaintEventFactory.create_assigned(
            **_base(
                current_status=ComplaintStatus.ASSIGNED.value,
                payload={"fromStatus": ComplaintStatus.NEW.value},
            )
        )
    )
    dispatcher.dispatch(
        ComplaintEventFactory.create_in_progress(
            **_base(
                current_status=ComplaintStatus.IN_PROGRESS.value,
                payload={"fromStatus": ComplaintStatus.ASSIGNED.value},
            )
        )
    )
    snap = store.snapshot()
    assert snap.total_received == 1
    assert snap.current_open == 1
    assert snap.current_in_progress == 1


def test_projection_immutable(store: KpiProjectionStore) -> None:
    snap = store.snapshot()
    with pytest.raises(Exception):
        snap.total_received = 99  # type: ignore[misc]


def test_handler_ignores_non_complaint_event(
    handler: KpiProjectionHandler, store: KpiProjectionStore
) -> None:
    handler.handle({"not": "complaint"})
    assert store.snapshot().total_received == 0


def test_accepted_is_marker_only(
    handler: KpiProjectionHandler, store: KpiProjectionStore
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
    after = store.snapshot()
    assert after.current_in_progress == before.current_in_progress
    assert after.current_open == before.current_open
    assert after.updated_at >= before.updated_at


def test_sla_breached_flag(
    handler: KpiProjectionHandler, store: KpiProjectionStore
) -> None:
    handler.handle(
        ComplaintEventFactory.create_created(
            **_base(payload={"slaBreached": True})
        )
    )
    assert store.snapshot().sla_breached == 1


def test_complaint_service_path_updates_projection() -> None:
    from app.modules.complaints.schemas import ComplaintCreateRequest
    from app.modules.complaints.service import ComplaintService

    customer_id = uuid.uuid4()
    branch_id = uuid.uuid4()

    def _add(complaint: Any) -> Any:
        now = datetime.now(UTC)
        complaint.id = uuid.uuid4()  # type: ignore[attr-defined]
        complaint.complaint_number = "CMP-KPICREATE"  # type: ignore[attr-defined]
        complaint.created_at = now  # type: ignore[attr-defined]
        complaint.updated_at = now  # type: ignore[attr-defined]
        return complaint

    repo = MagicMock()
    repo.customer_exists.return_value = True
    repo.branch_exists.return_value = True
    repo.add.side_effect = _add
    repo.refresh.side_effect = lambda c: None

    store = KpiProjectionStore()
    dispatcher = EventDispatcher()
    register_kpi_projection_handler(
        dispatcher,
        handler=KpiProjectionHandler(store=store),
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
            subject="KPI projection seed",
            description="Creates ComplaintCreated → KPI projection update",
            priority="LOW",
        ),
        actor_user_id=uuid.uuid4(),
    )

    assert store.snapshot().total_received == 1
    assert store.snapshot().current_open == 1


def test_store_does_not_import_complaint_service() -> None:
    import app.modules.kpi.projection_handler as handler_mod
    import app.modules.kpi.projection_store as store_mod

    store_src = open(store_mod.__file__, encoding="utf-8").read()
    handler_src = open(handler_mod.__file__, encoding="utf-8").read()
    assert "from app.modules.complaints" not in store_src
    assert "from app.modules.complaints" not in handler_src
    assert "import ComplaintService" not in store_src
    assert "import ComplaintService" not in handler_src
    assert "complaint_service" not in store_src
    assert "complaint_service" not in handler_src


def test_regression_existing_kpi_api_unchanged() -> None:
    """KPI HTTP summary module remains separate from projection foundation."""
    from app.modules.kpi import service as kpi_service_mod

    src = open(kpi_service_mod.__file__, encoding="utf-8").read()
    assert "KpiProjection" not in src
    assert "projection_store" not in src
