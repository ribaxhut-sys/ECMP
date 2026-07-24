"""ExecutionEngine — lifecycle state transitions for ExecutionRun (TASK-055).



Validates transitions, produces new immutable ExecutionRun, returns EngineResult.
Does NOT invoke handlers, registry, Notification, Assignment, Workflow, AI,
HTTP, or queues.
"""



from __future__ import annotations



from dataclasses import dataclass, replace
from types import MappingProxyType
from typing import Mapping



from app.core.logging import get_logger
from app.modules.execution.lifecycle import ExecutionLifecycle, ExecutionStateMachine
from app.modules.execution.run_store import ExecutionRunStore
from app.modules.execution.runtime_models import ExecutionRun, ExecutionRunStatus



logger = get_logger(__name__)





@dataclass(frozen=True, slots=True)
class ExecutionEngineResult:
    """Result of a transition attempt. No execution side effects."""



    success: bool
    previous_state: ExecutionRunStatus
    new_state: ExecutionRunStatus
    reason: str



    def as_dict(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "success": self.success,
                "previousState": self.previous_state.value,
                "newState": self.new_state.value,
                "reason": self.reason,
            }
        )





class ExecutionEngine:
    """Controls ExecutionRun status transitions only (Milestone-1)."""



    def __init__(
        self,
        store: ExecutionRunStore | None = None,
        state_machine: ExecutionStateMachine | None = None,
    ) -> None:
        self._store = store
        self._sm = state_machine if state_machine is not None else ExecutionStateMachine()



    @property
    def store(self) -> ExecutionRunStore | None:
        return self._store



    @property
    def state_machine(self) -> ExecutionStateMachine:
        return self._sm



    def transition(
        self,
        run: ExecutionRun,
        to_state: ExecutionRunStatus,
        *,
        reason: str | None = None,
    ) -> tuple[ExecutionEngineResult, ExecutionRun]:
        """Validate transition and produce a new immutable ExecutionRun.



        On success: returns (result, new_run) and optionally upserts store.
        On failure: returns (result, same_run); store unchanged.
        Never executes task handlers or invokes the registry.
        """
        if not isinstance(run, ExecutionRun):
            raise TypeError(
                f"run must be ExecutionRun, got {type(run).__name__}"
            )
        if not isinstance(to_state, ExecutionRunStatus):
            raise TypeError(
                f"to_state must be ExecutionRunStatus, got {type(to_state).__name__}"
            )



        previous = run.status



        if not self._sm.can_transition(previous, to_state):
            result = ExecutionEngineResult(
                success=False,
                previous_state=previous,
                new_state=previous,
                reason=(
                    reason
                    if reason
                    else f"INVALID_TRANSITION: {previous.value} -> {to_state.value}"
                ),
            )
            logger.debug(
                "ExecutionEngine rejected transition",
                extra={
                    "extra_fields": {
                        "runId": str(run.run_id),
                        "previousState": previous.value,
                        "attemptedState": to_state.value,
                        "reason": result.reason,
                    }
                },
            )
            return result, run



        new_run = replace(run, status=to_state)
        if self._store is not None:
            self._store.put(new_run)



        result = ExecutionEngineResult(
            success=True,
            previous_state=previous,
            new_state=to_state,
            reason=reason if reason else f"TRANSITION: {previous.value} -> {to_state.value}",
        )
        logger.debug(
            "ExecutionEngine applied transition (no execution)",
            extra={
                "extra_fields": {
                    "runId": str(run.run_id),
                    "previousState": previous.value,
                    "newState": to_state.value,
                    "reason": result.reason,
                }
            },
        )
        return result, new_run



    def can_transition(
        self,
        run: ExecutionRun,
        to_state: ExecutionRunStatus,
    ) -> bool:
        if not isinstance(run, ExecutionRun):
            raise TypeError(
                f"run must be ExecutionRun, got {type(run).__name__}"
            )
        return self._sm.can_transition(run.status, to_state)



    def allowed_targets(self, run: ExecutionRun) -> frozenset[ExecutionRunStatus]:
        if not isinstance(run, ExecutionRun):
            raise TypeError(
                f"run must be ExecutionRun, got {type(run).__name__}"
            )
        return ExecutionLifecycle.targets_from(run.status)


