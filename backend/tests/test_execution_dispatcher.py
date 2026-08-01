"""Execution Dispatcher Foundation tests (TASK-056)."""



from __future__ import annotations

import ast
import uuid
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from app.modules.execution import (
    DispatchPolicy,
    DispatchRequest,
    DispatchResult,
    DispatchValidator,
    ExecutionContext,
    ExecutionDispatcher,
    ExecutionRegistry,
    ExecutionRun,
    ExecutionRunStatus,
    ExecutionRunTask,
    ExecutionRunTaskStatus,
    ExecutionTask,
)
from app.modules.execution.models import freeze_mapping


def _task(

    *,

    task_type: str = "NOTIFY",

    order: int = 1,

    task_id: uuid.UUID | None = None,

) -> ExecutionTask:

    return ExecutionTask(

        task_id=task_id or uuid.uuid4(),

        order=order,

        task_type=task_type,

        target="channel:email",

        configuration=freeze_mapping({"template": "x"}),

        executed=False,

    )





def _run(

    *plan_tasks: ExecutionTask,

    status: ExecutionRunStatus = ExecutionRunStatus.READY,

) -> ExecutionRun:

    tasks = tuple(

        ExecutionRunTask(

            task_id=uuid.uuid4(),

            execution_task_id=pt.task_id,

            order=pt.order,

            status=ExecutionRunTaskStatus.CREATED,

        )

        for pt in plan_tasks

    )

    return ExecutionRun(

        run_id=uuid.uuid4(),

        plan_id=uuid.uuid4(),

        created_at=datetime.now(UTC),

        status=status,

        tasks=tasks,

        metadata=freeze_mapping({}),

        context=ExecutionContext(

            trace_id="trace-d",

            correlation_id="corr-d",

            tenant_id="tenant-1",

            metadata=freeze_mapping({}),

        ),

    )





@pytest.fixture()

def registry() -> ExecutionRegistry:

    reg = ExecutionRegistry()

    reg.register("NOTIFY", lambda *_a, **_k: None)

    reg.register("AUDIT", lambda *_a, **_k: None)

    return reg





@pytest.fixture()

def dispatcher(registry: ExecutionRegistry) -> ExecutionDispatcher:

    return ExecutionDispatcher(registry=registry)





def test_dispatch_request_pass(dispatcher: ExecutionDispatcher) -> None:

    plan_task = _task()

    run = _run(plan_task)

    request, result = dispatcher.dispatch(run, plan_task)

    assert result.success is True

    assert isinstance(request, DispatchRequest)

    assert request.run_id == run.run_id

    assert request.task_id == run.tasks[0].task_id

    assert request.task_type == "NOTIFY"

    assert request.target == "channel:email"

    assert request.configuration["template"] == "x"

    assert request.context is run.context

    data = request.as_dict()

    assert data["taskType"] == "NOTIFY"





def test_dispatch_validator_pass(registry: ExecutionRegistry) -> None:

    validator = DispatchValidator()

    plan_task = _task()

    run = _run(plan_task, status=ExecutionRunStatus.RUNNING)

    validation = validator.validate(run, plan_task, registry)

    assert validation.result.success is True

    assert validation.result.handler_registered is True

    assert validation.run_task is not None





def test_handler_availability_pass(dispatcher: ExecutionDispatcher) -> None:

    plan_task = _task(task_type="NOTIFY")

    run = _run(plan_task)

    _, result = dispatcher.dispatch(run, plan_task)

    assert result.handler_registered is True

    assert result.success is True





def test_sequential_policy_pass(dispatcher: ExecutionDispatcher) -> None:

    assert dispatcher.policy == DispatchPolicy.SEQUENTIAL

    a = _task(task_type="AUDIT", order=2)

    b = _task(task_type="NOTIFY", order=1)

    run = _run(a, b, status=ExecutionRunStatus.READY)

    planned = dispatcher.dispatch_sequential(run, [a, b])

    assert len(planned) == 2

    assert planned[0][0] is not None and planned[0][0].task_type == "NOTIFY"

    assert planned[1][0] is not None and planned[1][0].task_type == "AUDIT"

    with pytest.raises(ValueError, match="SEQUENTIAL"):

        ExecutionDispatcher(policy="PARALLEL")  # type: ignore[arg-type]





def test_invalid_task_type_pass(dispatcher: ExecutionDispatcher) -> None:

    plan_task = _task(task_type="UNKNOWN_XYZ")

    run = _run(plan_task)

    request, result = dispatcher.dispatch(run, plan_task)

    assert request is None

    assert result.success is False

    assert result.handler_registered is False

    assert "HANDLER_NOT_REGISTERED" in result.reason



    empty = ExecutionTask(

        task_id=uuid.uuid4(),

        order=1,

        task_type="   ",

        target="t",

        configuration=freeze_mapping({}),

    )

    run2 = _run(empty)

    request2, result2 = dispatcher.dispatch(run2, empty)

    assert request2 is None

    assert "UNKNOWN_TASK_TYPE" in result2.reason





def test_invalid_state_pass(dispatcher: ExecutionDispatcher) -> None:

    plan_task = _task()

    for status in (

        ExecutionRunStatus.CREATED,

        ExecutionRunStatus.COMPLETED,

        ExecutionRunStatus.FAILED,

        ExecutionRunStatus.CANCELLED,

    ):

        run = _run(plan_task, status=status)

        request, result = dispatcher.dispatch(run, plan_task)

        assert request is None

        assert result.success is False

        assert "INVALID_STATE" in result.reason





def test_task_not_on_run_pass(dispatcher: ExecutionDispatcher) -> None:

    on_run = _task()

    other = _task(task_type="NOTIFY")

    run = _run(on_run)

    request, result = dispatcher.dispatch(run, other)

    assert request is None

    assert "TASK_NOT_FOUND" in result.reason





def test_dispatch_result_pass(dispatcher: ExecutionDispatcher) -> None:

    plan_task = _task()

    run = _run(plan_task)

    _, result = dispatcher.dispatch(run, plan_task)

    assert isinstance(result, DispatchResult)

    data = result.as_dict()

    assert data["success"] is True

    assert data["handlerRegistered"] is True





def test_immutable_dispatch_request(dispatcher: ExecutionDispatcher) -> None:

    plan_task = _task()

    run = _run(plan_task)

    request, _ = dispatcher.dispatch(run, plan_task)

    assert request is not None

    with pytest.raises(Exception):

        request.task_type = "X"  # type: ignore[misc]

    with pytest.raises(TypeError):

        request.configuration["k"] = 1  # type: ignore[index]





def test_no_execution_pass(dispatcher: ExecutionDispatcher, registry: ExecutionRegistry) -> None:

    invoked = {"count": 0}



    def boom(*_a: object, **_k: object) -> None:

        invoked["count"] += 1

        raise AssertionError("handler must not be invoked")



    registry.register("NOTIFY", boom)

    plan_task = _task()

    run = _run(plan_task, status=ExecutionRunStatus.RUNNING)



    with (

        patch("app.modules.notification.factory.NotificationFactory") as mock_notif,

        patch("app.modules.assignments.service.AssignmentService", create=True) as mock_assign,

        patch("app.modules.workflow.engine.WorkflowEngine", create=True) as mock_wf,

    ):

        request, result = dispatcher.dispatch(run, plan_task)

        dispatcher.dispatch_sequential(run, [plan_task])



    assert result.success is True

    assert request is not None

    assert invoked["count"] == 0

    assert registry.get("NOTIFY") is boom

    mock_notif.assert_not_called()

    mock_assign.assert_not_called()

    mock_wf.assert_not_called()





def test_dispatcher_modules_domain_agnostic() -> None:

    root = Path(__file__).resolve().parents[1] / "app" / "modules" / "execution"

    forbidden = (

        "app.modules.complaints",

        "app.modules.complaint",

        "app.modules.workflow",

        "app.modules.notification",

        "app.modules.execution.engine",

        "app.modules.execution.lifecycle",

        "app.modules.execution.runtime",

    )

    for name in ("dispatcher.py", "dispatch_validator.py", "dispatch_models.py"):

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





def test_regression_engine_untouched() -> None:

    """Engine transition still works independently of dispatcher."""

    from app.modules.execution import ExecutionEngine



    plan_task = _task()

    run = _run(plan_task, status=ExecutionRunStatus.CREATED)

    engine = ExecutionEngine()

    result, ready = engine.transition(run, ExecutionRunStatus.READY)

    assert result.success is True

    assert ready.status == ExecutionRunStatus.READY


