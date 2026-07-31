"""Execution lifecycle + state machine (TASK-055).



Defines allowed ExecutionRun status transitions only.
No business logic, no handler invocation, no side effects.
"""



from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from app.modules.execution.runtime_models import ExecutionRunStatus


@dataclass(frozen=True, slots=True)
class ExecutionTransition:
    """Immutable from → to transition descriptor."""



    from_state: ExecutionRunStatus
    to_state: ExecutionRunStatus



    def as_dict(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "fromState": self.from_state.value,
                "toState": self.to_state.value,
            }
        )





class ExecutionLifecycle:
    """Central catalog of allowed ExecutionRun transitions. No business logic."""



    _ALLOWED: frozenset[tuple[ExecutionRunStatus, ExecutionRunStatus]] = frozenset(
        {
            (ExecutionRunStatus.CREATED, ExecutionRunStatus.READY),
            (ExecutionRunStatus.READY, ExecutionRunStatus.RUNNING),
            (ExecutionRunStatus.RUNNING, ExecutionRunStatus.COMPLETED),
            (ExecutionRunStatus.RUNNING, ExecutionRunStatus.FAILED),
            (ExecutionRunStatus.READY, ExecutionRunStatus.CANCELLED),
            (ExecutionRunStatus.RUNNING, ExecutionRunStatus.CANCELLED),
        }
    )



    @classmethod
    def allowed_transitions(cls) -> frozenset[ExecutionTransition]:
        return frozenset(
            ExecutionTransition(frm, to) for frm, to in cls._ALLOWED
        )



    @classmethod
    def is_allowed(
        cls,
        from_state: ExecutionRunStatus,
        to_state: ExecutionRunStatus,
    ) -> bool:
        return (from_state, to_state) in cls._ALLOWED



    @classmethod
    def targets_from(cls, from_state: ExecutionRunStatus) -> frozenset[ExecutionRunStatus]:
        return frozenset(to for frm, to in cls._ALLOWED if frm == from_state)



    @classmethod
    def states(cls) -> frozenset[ExecutionRunStatus]:
        return frozenset(ExecutionRunStatus)





class ExecutionStateMachine:
    """Validates transitions using ExecutionLifecycle. Rejects invalid changes."""



    def __init__(self, lifecycle: type[ExecutionLifecycle] | None = None) -> None:
        self._lifecycle = lifecycle if lifecycle is not None else ExecutionLifecycle



    def can_transition(
        self,
        from_state: ExecutionRunStatus,
        to_state: ExecutionRunStatus,
    ) -> bool:
        if not isinstance(from_state, ExecutionRunStatus):
            raise TypeError(
                f"from_state must be ExecutionRunStatus, got {type(from_state).__name__}"
            )
        if not isinstance(to_state, ExecutionRunStatus):
            raise TypeError(
                f"to_state must be ExecutionRunStatus, got {type(to_state).__name__}"
            )
        return self._lifecycle.is_allowed(from_state, to_state)



    def validate(
        self,
        from_state: ExecutionRunStatus,
        to_state: ExecutionRunStatus,
    ) -> ExecutionTransition:
        """Return the transition if allowed; raise ValueError if invalid."""
        if not self.can_transition(from_state, to_state):
            raise ValueError(
                f"Invalid execution transition: {from_state.value} -> {to_state.value}"
            )
        return ExecutionTransition(from_state, to_state)


