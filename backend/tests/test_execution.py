"""Execution Plan Foundation tests (TASK-053)."""

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
from app.modules.event_dispatcher import EventDispatcher
from app.modules.execution import (
    ExecutionPlan,
    ExecutionPlanner,
    ExecutionPlanSource,
    ExecutionPlanStatus,
    ExecutionPlanStore,
    ExecutionRegistry,
    ExecutionTask,
    WorkflowExecutionProducer,
)
from app.modules.routing import ComplaintRoute
from app.modules.workflow import (
    WorkflowEventHandler,
    WorkflowInstance,
    WorkflowInstanceStatus,
    WorkflowInstanceStore,
    WorkflowRegistry,
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
        "complaint_number": "CMP-EX0001",
        "current_status": ComplaintStatus.NEW.value,
        "priority": "MEDIUM",
        "source": _source(),
        "target": _target(),
        "routing": _route(),
        "occurred_at": datetime.now(UTC),
    }
    data.update(overrides)
    return data


def _sample_instance() -> WorkflowInstance:
    from app.modules.workflow.engine import WorkflowEngine

    engine = WorkflowEngine()
    engine.registry.register(
        build_definition(
            name="On Created",
            trigger=WorkflowTrigger.COMPLAINT_CREATED,
            steps=[
                build_step(
                    name="notify",
                    order=2,
                    action_type="NOTIFY",
                    configuration={"template": "complaint.created", "target": "channel:email"},
                ),
                build_step(
                    name="audit",
                    order=1,
                    action_type="AUDIT",
                    configuration={"action": "record"},
                ),
                build_step(
                    name="assign-hint",
                    order=3,
                    action_type="ASSIGN",
                    configuration={"target": "queue:default"},
                ),
            ],
        )
    )
    instances = engine.process(ComplaintEventFactory.create_created(**_base()))
    assert len(instances) == 1
    return instances[0]


@pytest.fixture()
def planner() -> ExecutionPlanner:
    return ExecutionPlanner()


@pytest.fixture()
def store() -> ExecutionPlanStore:
    return ExecutionPlanStore()


@pytest.fixture()
def registry() -> ExecutionRegistry:
    return ExecutionRegistry()


def test_plan_creation_pass(planner: ExecutionPlanner, store: ExecutionPlanStore) -> None:
    instance = _sample_instance()
    plan = planner.from_workflow(instance)
    store.add(plan)

    assert isinstance(plan, ExecutionPlan)
    assert plan.source == ExecutionPlanSource.WORKFLOW.value
    assert plan.source_id == instance.instance_id
    assert plan.created_at.tzinfo is not None
    assert len(plan.tasks) == 3
    assert store.get(plan.plan_id) is plan
    assert len(store) == 1


def test_task_ordering_pass(planner: ExecutionPlanner) -> None:
    instance = _sample_instance()
    plan = planner.from_workflow(instance)
    orders = [t.order for t in plan.tasks]
    assert orders == sorted(orders)
    assert plan.tasks[0].task_type == "AUDIT"
    assert plan.tasks[0].order == 1
    assert plan.tasks[1].task_type == "NOTIFY"
    assert plan.tasks[1].order == 2
    assert plan.tasks[2].task_type == "ASSIGN"
    assert plan.tasks[2].order == 3


def test_planned_status_pass(planner: ExecutionPlanner) -> None:
    plan = planner.from_workflow(_sample_instance())
    assert plan.status == ExecutionPlanStatus.PLANNED
    assert plan.status.value == "PLANNED"
    assert set(ExecutionPlanStatus) == {ExecutionPlanStatus.PLANNED}
    assert all(t.executed is False for t in plan.tasks)


def test_planner_pass(planner: ExecutionPlanner) -> None:
    instance = _sample_instance()
    plan = planner.from_workflow(instance)
    assert plan.metadata["workflowInstanceId"] == str(instance.instance_id)
    assert plan.metadata["workflowId"] == str(instance.workflow_id)
    assert plan.metadata["triggerEvent"] == instance.trigger_event
    assert plan.metadata["taskCount"] == 3
    assert plan.tasks[1].target == "channel:email"
    assert plan.tasks[0].target == "workflow.step:audit"


def test_workflow_mapping_pass() -> None:
    workflow_store = WorkflowInstanceStore()
    plan_store = ExecutionPlanStore()
    producer = WorkflowExecutionProducer(store=plan_store)
    registry = WorkflowRegistry()
    registry.register(
        build_definition(
            name="Map Test",
            trigger=WorkflowTrigger.COMPLAINT_CREATED,
            steps=[
                build_step(name="a", order=1, action_type="A", configuration={}),
                build_step(name="b", order=2, action_type="B", configuration={}),
            ],
        )
    )
    handler = WorkflowEventHandler(
        registry=registry,
        store=workflow_store,
        on_instances=producer,
    )
    dispatcher = EventDispatcher()
    dispatcher.register(handler)
    result = dispatcher.dispatch(ComplaintEventFactory.create_created(**_base()))

    assert result.ok is True
    assert len(workflow_store) == 1
    assert len(plan_store) == 1
    plan = plan_store.all()[0]
    assert plan.source == "WORKFLOW"
    assert plan.source_id == workflow_store.all()[0].instance_id
    assert [t.task_type for t in plan.tasks] == ["A", "B"]
    assert all(t.executed is False for t in plan.tasks)


def test_registry_pass(registry: ExecutionRegistry) -> None:
    called = {"count": 0}

    def fake_handler(*_args: object, **_kwargs: object) -> None:
        called["count"] += 1

    registry.register("NOTIFY", fake_handler)
    assert len(registry) == 1
    assert registry.has("NOTIFY") is True
    assert registry.get("NOTIFY") is fake_handler
    assert registry.task_types() == ["NOTIFY"]
    assert called["count"] == 0  # register must not invoke


def test_no_execution_pass(planner: ExecutionPlanner, registry: ExecutionRegistry) -> None:
    invoked = {"count": 0}

    def boom(*_a: object, **_k: object) -> None:
        invoked["count"] += 1
        raise AssertionError("handler must not be invoked")

    registry.register("NOTIFY", boom)
    registry.register("AUDIT", boom)
    registry.register("ASSIGN", boom)

    with (
        patch("app.modules.notification.factory.NotificationFactory") as mock_notif,
        patch("app.modules.assignments.service.AssignmentService", create=True) as mock_assign,
    ):
        plan = planner.from_workflow(_sample_instance())

    assert plan.status == ExecutionPlanStatus.PLANNED
    assert all(t.executed is False for t in plan.tasks)
    assert invoked["count"] == 0
    mock_notif.assert_not_called()
    mock_assign.assert_not_called()
    # Registry lookup must not imply execution
    assert registry.get("NOTIFY") is boom


def test_multiple_workflow_instances_produce_multiple_plans() -> None:
    plan_store = ExecutionPlanStore()
    producer = WorkflowExecutionProducer(store=plan_store)
    registry = WorkflowRegistry()
    registry.register(
        build_definition(
            name="A",
            trigger=WorkflowTrigger.COMPLAINT_CREATED,
            steps=[build_step(name="s", order=1, action_type="X", configuration={})],
        )
    )
    registry.register(
        build_definition(
            name="B",
            trigger=WorkflowTrigger.COMPLAINT_CREATED,
            steps=[build_step(name="s", order=1, action_type="Y", configuration={})],
        )
    )
    handler = WorkflowEventHandler(registry=registry, on_instances=producer)
    handler.handle(ComplaintEventFactory.create_created(**_base()))
    assert len(plan_store) == 2
    assert {p.tasks[0].task_type for p in plan_store.all()} == {"X", "Y"}


def test_register_workflow_handler_with_producer() -> None:
    dispatcher = EventDispatcher()
    plan_store = ExecutionPlanStore()
    producer = WorkflowExecutionProducer(store=plan_store)
    wf_registry = WorkflowRegistry()
    wf_registry.register(
        build_definition(
            name="R",
            trigger=WorkflowTrigger.COMPLAINT_CREATED,
            steps=[build_step(name="s", order=1, action_type="Z", configuration={})],
        )
    )
    register_workflow_handler(
        dispatcher,
        registry=wf_registry,
        on_instances=producer,
    )
    dispatcher.dispatch(ComplaintEventFactory.create_created(**_base()))
    assert len(plan_store) == 1


def test_immutable_models(planner: ExecutionPlanner) -> None:
    plan = planner.from_workflow(_sample_instance())
    with pytest.raises(Exception):
        plan.status = ExecutionPlanStatus.PLANNED  # type: ignore[misc]
    with pytest.raises(Exception):
        plan.tasks[0].executed = True  # type: ignore[misc]


def test_execution_task_default_executed() -> None:
    task = ExecutionTask(
        task_id=uuid.uuid4(),
        order=1,
        task_type="NOOP",
        target="t",
        configuration={},
    )
    assert task.executed is False


def test_as_dict(planner: ExecutionPlanner) -> None:
    plan = planner.from_workflow(_sample_instance())
    data = plan.as_dict()
    assert data["status"] == "PLANNED"
    assert data["source"] == "WORKFLOW"
    assert isinstance(data["tasks"], list)
    assert data["tasks"][0]["executed"] is False


def test_regression_workflow_unchanged_without_producer() -> None:
    """Without on_instances, workflow still creates CREATED instances only."""
    store = WorkflowInstanceStore()
    registry = WorkflowRegistry()
    registry.register(
        build_definition(
            name="Plain",
            trigger=WorkflowTrigger.COMPLAINT_CREATED,
            steps=[build_step(name="s", order=1, action_type="X", configuration={})],
        )
    )
    handler = WorkflowEventHandler(registry=registry, store=store)
    handler.handle(ComplaintEventFactory.create_created(**_base()))
    assert len(store) == 1
    assert store.all()[0].status == WorkflowInstanceStatus.CREATED


def test_planner_rejects_non_instance(planner: ExecutionPlanner) -> None:
    with pytest.raises(TypeError):
        planner.from_workflow(MagicMock())  # type: ignore[arg-type]
