"""Execution Engine Foundation tests (TASK-055)."""



from __future__ import annotations

import ast
import uuid
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from app.modules.execution import (
    ExecutionContext,
    ExecutionEngine,
    ExecutionEngineResult,
    ExecutionLifecycle,
    ExecutionPlan,
    ExecutionPlanSource,
    ExecutionPlanStatus,
    ExecutionRegistry,
    ExecutionRun,
    ExecutionRunStatus,
    ExecutionRunStore,
    ExecutionRunTask,
    ExecutionRunTaskStatus,
    ExecutionRuntime,
    ExecutionStateMachine,
    ExecutionTask,
    ExecutionTransition,
)
from app.modules.execution.models import freeze_mapping


def _run(*, status: ExecutionRunStatus = ExecutionRunStatus.CREATED) -> ExecutionRun:
    return ExecutionRun(
        run_id=uuid.uuid4(),
        plan_id=uuid.uuid4(),
        created_at=datetime.now(UTC),
        status=status,
        tasks=(
            ExecutionRunTask(
                task_id=uuid.uuid4(),
                execution_task_id=uuid.uuid4(),
                order=1,
                status=ExecutionRunTaskStatus.CREATED,
            ),
        ),
        metadata=freeze_mapping({"origin": "engine-test"}),
        context=ExecutionContext(
            trace_id="t-1",
            correlation_id="c-1",
            metadata=freeze_mapping({}),
        ),
    )





@pytest.fixture()
def store() -> ExecutionRunStore:
    return ExecutionRunStore()





@pytest.fixture()
def engine(store: ExecutionRunStore) -> ExecutionEngine:
    return ExecutionEngine(store=store)





def test_lifecycle_states_pass() -> None:
    states = ExecutionLifecycle.states()
    assert states == {
        ExecutionRunStatus.CREATED,
        ExecutionRunStatus.READY,
        ExecutionRunStatus.RUNNING,
        ExecutionRunStatus.COMPLETED,
        ExecutionRunStatus.FAILED,
        ExecutionRunStatus.CANCELLED,
    }





def test_valid_transitions_pass(engine: ExecutionEngine) -> None:
    path = [
        ExecutionRunStatus.READY,
        ExecutionRunStatus.RUNNING,
        ExecutionRunStatus.COMPLETED,
    ]
    run = _run()
    for target in path:
        result, run = engine.transition(run, target)
        assert result.success is True
        assert result.new_state == target
        assert run.status == target





def test_valid_failure_and_cancel_paths(engine: ExecutionEngine) -> None:
    run = _run()
    _, run = engine.transition(run, ExecutionRunStatus.READY)
    _, run = engine.transition(run, ExecutionRunStatus.RUNNING)
    result, failed = engine.transition(run, ExecutionRunStatus.FAILED)
    assert result.success is True
    assert failed.status == ExecutionRunStatus.FAILED



    run2 = _run()
    _, run2 = engine.transition(run2, ExecutionRunStatus.READY)
    result2, cancelled = engine.transition(run2, ExecutionRunStatus.CANCELLED)
    assert result2.success is True
    assert cancelled.status == ExecutionRunStatus.CANCELLED



    run3 = _run()
    _, run3 = engine.transition(run3, ExecutionRunStatus.READY)
    _, run3 = engine.transition(run3, ExecutionRunStatus.RUNNING)
    result3, cancelled_running = engine.transition(
        run3, ExecutionRunStatus.CANCELLED
    )
    assert result3.success is True
    assert cancelled_running.status == ExecutionRunStatus.CANCELLED





def test_invalid_transitions_pass(engine: ExecutionEngine) -> None:
    run = _run()
    result, same = engine.transition(run, ExecutionRunStatus.COMPLETED)
    assert result.success is False
    assert result.previous_state == ExecutionRunStatus.CREATED
    assert result.new_state == ExecutionRunStatus.CREATED
    assert same is run
    assert "INVALID_TRANSITION" in result.reason



    result2, same2 = engine.transition(run, ExecutionRunStatus.RUNNING)
    assert result2.success is False
    assert same2.status == ExecutionRunStatus.CREATED



    completed = _run(status=ExecutionRunStatus.COMPLETED)
    result3, same3 = engine.transition(completed, ExecutionRunStatus.READY)
    assert result3.success is False
    assert same3 is completed





def test_state_machine_validate_pass() -> None:
    sm = ExecutionStateMachine()
    assert sm.can_transition(
        ExecutionRunStatus.CREATED, ExecutionRunStatus.READY
    )
    transition = sm.validate(
        ExecutionRunStatus.READY, ExecutionRunStatus.RUNNING
    )
    assert isinstance(transition, ExecutionTransition)
    assert transition.from_state == ExecutionRunStatus.READY
    assert transition.to_state == ExecutionRunStatus.RUNNING
    with pytest.raises(ValueError, match="Invalid execution transition"):
        sm.validate(ExecutionRunStatus.CREATED, ExecutionRunStatus.COMPLETED)





def test_engine_result_pass(engine: ExecutionEngine) -> None:
    run = _run()
    result, new_run = engine.transition(
        run, ExecutionRunStatus.READY, reason="arm"
    )
    assert isinstance(result, ExecutionEngineResult)
    assert result.success is True
    assert result.previous_state == ExecutionRunStatus.CREATED
    assert result.new_state == ExecutionRunStatus.READY
    assert result.reason == "arm"
    data = result.as_dict()
    assert data["success"] is True
    assert data["previousState"] == "CREATED"
    assert data["newState"] == "READY"
    assert new_run is not run





def test_immutable_updates_pass(engine: ExecutionEngine, store: ExecutionRunStore) -> None:
    run = _run()
    store.add(run)
    result, new_run = engine.transition(run, ExecutionRunStatus.READY)
    assert result.success is True
    assert run.status == ExecutionRunStatus.CREATED
    assert new_run.status == ExecutionRunStatus.READY
    assert store.get(run.run_id) is new_run
    assert store.get(run.run_id) is not run
    with pytest.raises(Exception):
        new_run.status = ExecutionRunStatus.RUNNING  # type: ignore[misc]





def test_allowed_targets_pass(engine: ExecutionEngine) -> None:
    run = _run(status=ExecutionRunStatus.READY)
    assert engine.allowed_targets(run) == {
        ExecutionRunStatus.RUNNING,
        ExecutionRunStatus.CANCELLED,
    }





def test_no_execution_pass(engine: ExecutionEngine) -> None:
    registry = ExecutionRegistry()
    invoked = {"count": 0}



    def boom(*_a: object, **_k: object) -> None:
        invoked["count"] += 1
        raise AssertionError("handler must not be invoked")



    registry.register("ANY", boom)
    run = _run()



    with (
        patch("app.modules.notification.factory.NotificationFactory") as mock_notif,
        patch("app.modules.assignments.service.AssignmentService", create=True) as mock_assign,
        patch("app.modules.workflow.engine.WorkflowEngine", create=True) as mock_wf,
    ):
        result, new_run = engine.transition(run, ExecutionRunStatus.READY)
        result2, new_run = engine.transition(new_run, ExecutionRunStatus.RUNNING)
        result3, new_run = engine.transition(new_run, ExecutionRunStatus.COMPLETED)



    assert result.success and result2.success and result3.success
    assert invoked["count"] == 0
    mock_notif.assert_not_called()
    mock_assign.assert_not_called()
    mock_wf.assert_not_called()





def test_engine_modules_domain_agnostic() -> None:
    root = Path(__file__).resolve().parents[1] / "app" / "modules" / "execution"
    forbidden = (
        "app.modules.complaints",
        "app.modules.complaint",
        "app.modules.workflow",
        "app.modules.notification",
    )
    for name in ("engine.py", "lifecycle.py"):
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





def test_regression_runtime_prepare_unchanged(store: ExecutionRunStore) -> None:
    """ExecutionRuntime still prepares CREATED runs; engine is separate."""
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
    runtime = ExecutionRuntime(store=store)
    engine = ExecutionEngine(store=store)
    prepared = runtime.prepare(plan)
    assert prepared.status == ExecutionRunStatus.CREATED
    result, ready = engine.transition(prepared, ExecutionRunStatus.READY)
    assert result.success is True
    assert ready.status == ExecutionRunStatus.READY
    assert prepared.status == ExecutionRunStatus.CREATED





def test_lifecycle_allowed_set_exact() -> None:
    expected = {
        ExecutionTransition(ExecutionRunStatus.CREATED, ExecutionRunStatus.READY),
        ExecutionTransition(ExecutionRunStatus.READY, ExecutionRunStatus.RUNNING),
        ExecutionTransition(ExecutionRunStatus.RUNNING, ExecutionRunStatus.COMPLETED),
        ExecutionTransition(ExecutionRunStatus.RUNNING, ExecutionRunStatus.FAILED),
        ExecutionTransition(ExecutionRunStatus.READY, ExecutionRunStatus.CANCELLED),
        ExecutionTransition(ExecutionRunStatus.RUNNING, ExecutionRunStatus.CANCELLED),
    }
    assert ExecutionLifecycle.allowed_transitions() == expected


