"""Execution Dispatcher foundation value objects (TASK-056).



Immutable dispatch planning models. Never invokes handlers.

"""



from __future__ import annotations



import uuid

from dataclasses import dataclass

from enum import StrEnum

from types import MappingProxyType

from typing import Any, Mapping



from app.modules.execution.runtime_models import ExecutionContext





class DispatchPolicy(StrEnum):

    """Dispatch ordering policy. Foundation supports sequential only."""



    SEQUENTIAL = "SEQUENTIAL"





@dataclass(frozen=True, slots=True)

class DispatchRequest:

    """Immutable planned dispatch unit. Not an execution call."""



    run_id: uuid.UUID

    task_id: uuid.UUID

    task_type: str

    target: str

    configuration: Mapping[str, Any]

    context: ExecutionContext



    def as_dict(self) -> Mapping[str, object]:

        return MappingProxyType(

            {

                "runId": str(self.run_id),

                "taskId": str(self.task_id),

                "taskType": self.task_type,

                "target": self.target,

                "configuration": dict(self.configuration),

                "context": dict(self.context.as_dict()),

            }

        )





@dataclass(frozen=True, slots=True)

class DispatchResult:

    """Outcome of dispatch planning / validation. No handler invocation."""



    success: bool

    handler_registered: bool

    reason: str



    def as_dict(self) -> Mapping[str, object]:

        return MappingProxyType(

            {

                "success": self.success,

                "handlerRegistered": self.handler_registered,

                "reason": self.reason,

            }

        )


