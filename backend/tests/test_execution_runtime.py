"""Execution Runtime Foundation tests (TASK-054)."""



from __future__ import annotations



import ast

import uuid

from datetime import UTC, datetime

from pathlib import Path

from unittest.mock import patch



import pytest



from app.modules.execution import (

    ExecutionContext,

    ExecutionPlan,

    ExecutionPlanSource,

    ExecutionPlanStatus,

    ExecutionPlanStore,

    ExecutionPlanner,

    ExecutionRegistry,

    ExecutionResult,

    ExecutionRun,

    ExecutionRunStatus,

    ExecutionRunStore,

    ExecutionRunTask,

    ExecutionRunTaskStatus,

    ExecutionRuntime,

    ExecutionTask,

    build_execution_context,

)

from app.modules.execution.models import freeze_mapping





def _plan(*, task_count: int = 3) -> ExecutionPlan:

    tasks = tuple(

        ExecutionTask(

            task_id=uuid.uuid4(),

            order=i,

            task_type=f"TYPE_{i}",

            target=f"target:{i}",

            configuration=freeze_mapping({"n": i}),

            executed=False,

        )

        for i in range(1, task_count + 1)

    )

    return ExecutionPlan(

        plan_id=uuid.uuid4(),

        source=ExecutionPlanSource.SCHEDULED_JOB.value,

        source_id=uuid.uuid4(),

        created_at=datetime.now(UTC),

        status=ExecutionPlanStatus.PLANNED,

        tasks=tasks,

        metadata=freeze_mapping({"origin": "unit-test", "taskCount": task_count}),

    )





@pytest.fixture()

def run_store() -> ExecutionRunStore:

    return ExecutionRunStore()





@pytest.fixture()

def runtime(run_store: ExecutionRunStore) -> ExecutionRuntime:

    return ExecutionRuntime(store=run_store)





def test_execution_run_creation_pass(runtime: ExecutionRuntime, run_store: ExecutionRunStore) -> None:

    plan = _plan()

    run = runtime.prepare(plan)



    assert isinstance(run, ExecutionRun)

    assert run.plan_id == plan.plan_id

    assert run.created_at.tzinfo is not None

    assert run_store.get(run.run_id) is run

    assert len(run_store) == 1

    assert run_store.by_plan_id(plan.plan_id) == [run]





def test_execution_task_expansion_pass(runtime: ExecutionRuntime) -> None:

    plan = _plan(task_count=3)

    run = runtime.prepare(plan)



    assert len(run.tasks) == 3

    assert [t.order for t in run.tasks] == [1, 2, 3]

    plan_ids = {t.task_id for t in plan.tasks}

    assert {t.execution_task_id for t in run.tasks} == plan_ids

    assert all(isinstance(t.task_id, uuid.UUID) for t in run.tasks)

    assert {t.task_id for t in run.tasks}.isdisjoint(plan_ids)





def test_execution_context_pass(runtime: ExecutionRuntime) -> None:

    plan = _plan()

    ctx = build_execution_context(

        trace_id="trace-1",

        correlation_id="corr-1",

        tenant_id="tenant-a",

        user_id="user-b",

        metadata={"channel": "test"},

    )

    run = runtime.prepare(plan, context=ctx)



    assert isinstance(run.context, ExecutionContext)

    assert run.context is ctx

    assert run.context.trace_id == "trace-1"

    assert run.context.correlation_id == "corr-1"

    assert run.context.tenant_id == "tenant-a"

    assert run.context.user_id == "user-b"

    assert run.context.metadata["channel"] == "test"





def test_execution_context_default_pass(runtime: ExecutionRuntime) -> None:

    plan = _plan()

    run = runtime.prepare(plan)

    assert run.context.trace_id

    assert run.context.correlation_id == str(plan.plan_id)

    assert run.context.metadata["planId"] == str(plan.plan_id)





def test_execution_result_foundation_pass() -> None:

    result = ExecutionResult(

        success=True,

        error_code=None,

        message="foundation only",

        metadata=freeze_mapping({"phase": "TASK-054"}),

    )

    assert result.success is True

    assert result.error_code is None

    assert result.message == "foundation only"

    data = result.as_dict()

    assert data["success"] is True

    assert data["metadata"]["phase"] == "TASK-054"





def test_created_status_pass(runtime: ExecutionRuntime) -> None:

    run = runtime.prepare(_plan())

    assert run.status == ExecutionRunStatus.CREATED

    assert run.status.value == "CREATED"

    assert {
        ExecutionRunStatus.CREATED,
        ExecutionRunStatus.READY,
        ExecutionRunStatus.RUNNING,
        ExecutionRunStatus.COMPLETED,
        ExecutionRunStatus.FAILED,
        ExecutionRunStatus.CANCELLED,
    } == set(ExecutionRunStatus)

    assert set(ExecutionRunTaskStatus) == {ExecutionRunTaskStatus.CREATED}

    assert all(t.status == ExecutionRunTaskStatus.CREATED for t in run.tasks)

    assert all(t.started_at is None for t in run.tasks)

    assert all(t.finished_at is None for t in run.tasks)

    assert all(t.result is None for t in run.tasks)





def test_runtime_pass(runtime: ExecutionRuntime) -> None:

    plan = _plan(task_count=2)

    run = runtime.prepare(plan)

    assert run.metadata["planSource"] == plan.source

    assert run.metadata["planStatus"] == "PLANNED"

    assert run.metadata["taskCount"] == 2

    assert run.metadata["runtime"] == "TASK-054"

    assert run.metadata["origin"] == "unit-test"





def test_store_pass(run_store: ExecutionRunStore) -> None:

    runtime = ExecutionRuntime(store=run_store)

    a = runtime.prepare(_plan(task_count=1))

    b = runtime.prepare(_plan(task_count=1))

    assert len(run_store) == 2

    assert run_store.get(a.run_id) is a

    assert run_store.get(b.run_id) is b

    assert run_store.all() == [a, b]

    run_store.clear()

    assert len(run_store) == 0





def test_immutable_objects_pass(runtime: ExecutionRuntime) -> None:

    run = runtime.prepare(_plan())

    with pytest.raises(Exception):

        run.status = ExecutionRunStatus.CREATED  # type: ignore[misc]

    with pytest.raises(Exception):

        run.tasks[0].status = ExecutionRunTaskStatus.CREATED  # type: ignore[misc]

    with pytest.raises(Exception):

        run.context.trace_id = "mutated"  # type: ignore[misc]

    with pytest.raises(TypeError):

        run.metadata["x"] = 1  # type: ignore[index]

    with pytest.raises(TypeError):

        run.context.metadata["y"] = 2  # type: ignore[index]





def test_context_creation_validation_pass() -> None:

    ctx = build_execution_context(tenant_id="t1")

    assert isinstance(ctx, ExecutionContext)

    assert uuid.UUID(ctx.trace_id)

    assert uuid.UUID(ctx.correlation_id)

    with pytest.raises(Exception):

        ctx.user_id = "x"  # type: ignore[misc]





def test_no_execution_pass(runtime: ExecutionRuntime) -> None:

    registry = ExecutionRegistry()

    invoked = {"count": 0}



    def boom(*_a: object, **_k: object) -> None:

        invoked["count"] += 1

        raise AssertionError("handler must not be invoked")



    registry.register("TYPE_1", boom)

    registry.register("TYPE_2", boom)



    with (

        patch("app.modules.notification.factory.NotificationFactory") as mock_notif,

        patch("app.modules.assignments.service.AssignmentService", create=True) as mock_assign,

    ):

        run = runtime.prepare(_plan(task_count=2))



    assert run.status == ExecutionRunStatus.CREATED

    assert all(t.status == ExecutionRunTaskStatus.CREATED for t in run.tasks)

    assert invoked["count"] == 0

    mock_notif.assert_not_called()

    mock_assign.assert_not_called()

    assert registry.get("TYPE_1") is boom





def test_runtime_rejects_non_plan(runtime: ExecutionRuntime) -> None:

    with pytest.raises(TypeError):

        runtime.prepare(object())  # type: ignore[arg-type]





def test_runtime_rejects_bad_context(runtime: ExecutionRuntime) -> None:

    with pytest.raises(TypeError):

        runtime.prepare(_plan(), context=object())  # type: ignore[arg-type]





def test_runtime_domain_agnostic_imports() -> None:

    """Runtime modules must not import Complaint / Workflow / Notification."""

    root = Path(__file__).resolve().parents[1] / "app" / "modules" / "execution"

    forbidden = (

        "app.modules.complaints",

        "app.modules.complaint",

        "app.modules.workflow",

        "app.modules.notification",

    )

    for name in ("runtime.py", "runtime_models.py", "run_store.py"):

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





def test_regression_plan_foundation_unchanged() -> None:

    """TASK-053 plan path still works; runtime is opt-in after plan."""

    plan_store = ExecutionPlanStore()

    run_store = ExecutionRunStore()

    runtime = ExecutionRuntime(store=run_store)



    plan = ExecutionPlan(

        plan_id=uuid.uuid4(),

        source=ExecutionPlanSource.MANUAL_OPERATION.value,

        source_id=uuid.uuid4(),

        created_at=datetime.now(UTC),

        status=ExecutionPlanStatus.PLANNED,

        tasks=(

            ExecutionTask(

                task_id=uuid.uuid4(),

                order=1,

                task_type="NOOP",

                target="t",

                configuration=freeze_mapping({}),

            ),

        ),

        metadata=freeze_mapping({}),

    )

    plan_store.add(plan)

    assert plan.status == ExecutionPlanStatus.PLANNED

    assert plan.tasks[0].executed is False

    assert len(run_store) == 0



    run = runtime.prepare(plan)

    assert len(plan_store) == 1

    assert len(run_store) == 1

    assert run.status == ExecutionRunStatus.CREATED





def test_run_task_default_status() -> None:

    task = ExecutionRunTask(

        task_id=uuid.uuid4(),

        execution_task_id=uuid.uuid4(),

        order=1,

    )

    assert task.status == ExecutionRunTaskStatus.CREATED

    assert task.started_at is None

    assert task.finished_at is None

    assert task.result is None





def test_as_dict(runtime: ExecutionRuntime) -> None:

    run = runtime.prepare(_plan(task_count=1))

    data = run.as_dict()

    assert data["status"] == "CREATED"

    assert data["tasks"][0]["status"] == "CREATED"

    assert data["context"]["traceId"] == run.context.trace_id

    assert data["tasks"][0]["result"] is None


