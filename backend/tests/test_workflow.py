"""Workflow Foundation tests (TASK-052)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

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
from app.modules.routing import ComplaintRoute
from app.modules.workflow import (
    WorkflowDefinition,
    WorkflowEngine,
    WorkflowEventHandler,
    WorkflowInstance,
    WorkflowInstanceStatus,
    WorkflowInstanceStore,
    WorkflowRegistry,
    WorkflowStep,
    WorkflowTrigger,
    build_definition,
    build_step,
    register_workflow_handler,
)


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
        "complaint_number": "CMP-WF0001",
        "current_status": ComplaintStatus.NEW.value,
        "priority": "MEDIUM",
        "source": _source(),
        "target": _target(),
        "routing": _route(),
        "occurred_at": datetime.now(UTC),
    }
    data.update(overrides)
    return data


def _on_created_definition(
    *,
    name: str = "On Complaint Created",
    workflow_id: uuid.UUID | None = None,
) -> WorkflowDefinition:
    return build_definition(
        name=name,
        trigger=WorkflowTrigger.COMPLAINT_CREATED,
        workflow_id=workflow_id,
        steps=[
            build_step(
                name="plan-notify",
                order=1,
                action_type="NOTIFY",
                configuration={"template": "complaint.created"},
            ),
            build_step(
                name="plan-audit",
                order=2,
                action_type="AUDIT",
                configuration={"action": "record"},
            ),
        ],
        metadata={"version": 1},
    )


@pytest.fixture()
def registry() -> WorkflowRegistry:
    return WorkflowRegistry()


@pytest.fixture()
def store() -> WorkflowInstanceStore:
    return WorkflowInstanceStore()


@pytest.fixture()
def engine(
    registry: WorkflowRegistry, store: WorkflowInstanceStore
) -> WorkflowEngine:
    return WorkflowEngine(registry=registry, store=store)


@pytest.fixture()
def handler(engine: WorkflowEngine) -> WorkflowEventHandler:
    return WorkflowEventHandler(engine=engine)


def test_workflow_registration_pass(registry: WorkflowRegistry) -> None:
    definition = _on_created_definition()
    registry.register(definition)
    assert len(registry) == 1
    assert registry.get(definition.workflow_id) is definition
    assert registry.match(WorkflowTrigger.COMPLAINT_CREATED) == [definition]
    assert registry.match("ComplaintCreated") == [definition]
    assert registry.match(WorkflowTrigger.COMPLAINT_CLOSED) == []


def test_workflow_matching_pass(engine: WorkflowEngine) -> None:
    created_def = _on_created_definition()
    assigned_def = build_definition(
        name="On Assigned",
        trigger=WorkflowTrigger.COMPLAINT_ASSIGNED,
        steps=[
            build_step(
                name="plan-assign-followup",
                order=1,
                action_type="ASSIGN_FOLLOWUP",
                configuration={},
            )
        ],
    )
    engine.registry.register(created_def)
    engine.registry.register(assigned_def)

    created_event = ComplaintEventFactory.create_created(**_base())
    assigned_event = ComplaintEventFactory.create_assigned(
        **_base(current_status=ComplaintStatus.ASSIGNED.value)
    )

    created_instances = engine.process(created_event)
    assigned_instances = engine.process(assigned_event)

    assert len(created_instances) == 1
    assert created_instances[0].workflow_id == created_def.workflow_id
    assert created_instances[0].trigger_event == "ComplaintCreated"

    assert len(assigned_instances) == 1
    assert assigned_instances[0].workflow_id == assigned_def.workflow_id
    assert assigned_instances[0].trigger_event == "ComplaintAssigned"


def test_instance_creation_pass(engine: WorkflowEngine) -> None:
    definition = _on_created_definition()
    engine.registry.register(definition)
    event = ComplaintEventFactory.create_created(**_base())

    instances = engine.process(event)
    assert len(instances) == 1
    instance = instances[0]

    assert isinstance(instance, WorkflowInstance)
    assert instance.workflow_id == definition.workflow_id
    assert instance.trigger_event == WorkflowTrigger.COMPLAINT_CREATED.value
    assert instance.created_at.tzinfo is not None
    assert len(instance.steps) == 2
    assert instance.steps[0].order == 1
    assert instance.steps[0].action_type == "NOTIFY"
    assert instance.metadata["eventId"] == str(event.event_id)
    assert instance.metadata["complaintId"] == str(event.complaint_id)
    assert engine.store.get(instance.instance_id) is instance
    assert len(engine.store) == 1


def test_created_status_pass(engine: WorkflowEngine) -> None:
    engine.registry.register(_on_created_definition())
    instances = engine.process(ComplaintEventFactory.create_created(**_base()))
    assert len(instances) == 1
    assert instances[0].status == WorkflowInstanceStatus.CREATED
    assert instances[0].status.value == "CREATED"
    assert set(WorkflowInstanceStatus) == {WorkflowInstanceStatus.CREATED}


def test_dispatcher_integration_pass(
    handler: WorkflowEventHandler, store: WorkflowInstanceStore
) -> None:
    assert isinstance(handler, EventHandler)
    handler.registry.register(_on_created_definition())

    dispatcher = EventDispatcher()
    dispatcher.register(handler)

    event = ComplaintEventFactory.create_created(**_base())
    result = dispatcher.dispatch(event)

    assert result.ok is True
    assert result.success_count == 1
    assert result.failed_count == 0
    assert len(store) == 1
    assert store.all()[0].trigger_event == "ComplaintCreated"


def test_multiple_workflow_pass(engine: WorkflowEngine) -> None:
    first = _on_created_definition(name="Created A")
    second = _on_created_definition(name="Created B")
    engine.registry.register(first)
    engine.registry.register(second)

    instances = engine.process(ComplaintEventFactory.create_created(**_base()))
    assert len(instances) == 2
    workflow_ids = {i.workflow_id for i in instances}
    assert workflow_ids == {first.workflow_id, second.workflow_id}
    assert all(i.status == WorkflowInstanceStatus.CREATED for i in instances)
    assert len(engine.store) == 2


def test_no_action_execution_pass(engine: WorkflowEngine) -> None:
    """Planned actions are recorded with executed=False; no side-effect modules called."""
    definition = _on_created_definition()
    engine.registry.register(definition)

    with (
        patch("app.modules.notification.factory.NotificationFactory") as mock_notif,
        patch(
            "app.modules.assignments.service.AssignmentService",
            create=True,
        ) as mock_assign,
    ):
        instances = engine.process(ComplaintEventFactory.create_created(**_base()))

    assert len(instances) == 1
    planned = instances[0].metadata["plannedActions"]
    assert len(planned) == 2
    assert all(item["executed"] is False for item in planned)
    mock_notif.assert_not_called()
    mock_assign.assert_not_called()


def test_all_supported_triggers_pass(engine: WorkflowEngine) -> None:
    factories = [
        (WorkflowTrigger.COMPLAINT_CREATED, ComplaintEventFactory.create_created),
        (WorkflowTrigger.COMPLAINT_ASSIGNED, ComplaintEventFactory.create_assigned),
        (WorkflowTrigger.COMPLAINT_ACCEPTED, ComplaintEventFactory.create_accepted),
        (
            WorkflowTrigger.COMPLAINT_IN_PROGRESS,
            ComplaintEventFactory.create_in_progress,
        ),
        (WorkflowTrigger.COMPLAINT_RESOLVED, ComplaintEventFactory.create_resolved),
        (WorkflowTrigger.COMPLAINT_CLOSED, ComplaintEventFactory.create_closed),
        (WorkflowTrigger.COMPLAINT_ESCALATED, ComplaintEventFactory.create_escalated),
    ]
    for trigger, factory in factories:
        engine.registry.register(
            build_definition(
                name=f"WF-{trigger.value}",
                trigger=trigger,
                steps=[
                    build_step(
                        name="plan",
                        order=1,
                        action_type="NOOP",
                        configuration={},
                    )
                ],
            )
        )
        status_map = {
            WorkflowTrigger.COMPLAINT_CREATED: ComplaintStatus.NEW.value,
            WorkflowTrigger.COMPLAINT_ASSIGNED: ComplaintStatus.ASSIGNED.value,
            WorkflowTrigger.COMPLAINT_ACCEPTED: ComplaintStatus.ASSIGNED.value,
            WorkflowTrigger.COMPLAINT_IN_PROGRESS: ComplaintStatus.IN_PROGRESS.value,
            WorkflowTrigger.COMPLAINT_RESOLVED: ComplaintStatus.RESOLVED.value,
            WorkflowTrigger.COMPLAINT_CLOSED: ComplaintStatus.CLOSED.value,
            WorkflowTrigger.COMPLAINT_ESCALATED: ComplaintStatus.ESCALATED.value,
        }
        event = factory(**_base(current_status=status_map[trigger]))
        instances = engine.process(event)
        assert len(instances) == 1
        assert instances[0].trigger_event == trigger.value
        assert instances[0].status == WorkflowInstanceStatus.CREATED

    assert len(engine.store) == len(factories)


def test_no_match_creates_nothing(engine: WorkflowEngine) -> None:
    engine.registry.register(_on_created_definition())
    instances = engine.process(
        ComplaintEventFactory.create_closed(
            **_base(current_status=ComplaintStatus.CLOSED.value)
        )
    )
    assert instances == []
    assert len(engine.store) == 0


def test_register_workflow_handler_idempotent() -> None:
    dispatcher = EventDispatcher()
    registry = WorkflowRegistry()
    store = WorkflowInstanceStore()
    first = register_workflow_handler(dispatcher, registry=registry, store=store)
    second = register_workflow_handler(dispatcher, registry=registry, store=store)
    assert first is second
    assert len(dispatcher.registered_handlers()) == 1


def test_handler_ignores_non_complaint_events(handler: WorkflowEventHandler) -> None:
    handler.registry.register(_on_created_definition())
    handler.handle({"not": "an-event"})
    handler.handle(MagicMock())
    assert len(handler.store) == 0


def test_immutable_models() -> None:
    step = build_step(name="s", order=1, action_type="X", configuration={"a": 1})
    definition = build_definition(
        name="d",
        trigger=WorkflowTrigger.COMPLAINT_CREATED,
        steps=[step],
    )
    with pytest.raises(Exception):
        step.name = "changed"  # type: ignore[misc]
    with pytest.raises(Exception):
        definition.name = "changed"  # type: ignore[misc]


def test_regression_dispatcher_failure_isolation(
    handler: WorkflowEventHandler,
) -> None:
    """Workflow failure must not block other handlers (dispatcher contract)."""

    class BoomHandler(EventHandler):
        def handle(self, event: object) -> None:
            raise RuntimeError("boom")

    handler.registry.register(_on_created_definition())
    dispatcher = EventDispatcher()
    boom = BoomHandler()
    dispatcher.register(boom)
    dispatcher.register(handler)

    result = dispatcher.dispatch(ComplaintEventFactory.create_created(**_base()))
    assert result.success_count == 1
    assert result.failed_count == 1
    assert len(handler.store) == 1


def test_step_and_definition_as_dict() -> None:
    step = WorkflowStep(
        step_id=uuid.uuid4(),
        name="n",
        order=1,
        action_type="NOTIFY",
        configuration={"k": "v"},
    )
    definition = WorkflowDefinition(
        workflow_id=uuid.uuid4(),
        name="wf",
        trigger=WorkflowTrigger.COMPLAINT_CREATED,
        steps=(step,),
        metadata={"m": 1},
    )
    assert step.as_dict()["actionType"] == "NOTIFY"
    assert definition.as_dict()["trigger"] == "ComplaintCreated"
