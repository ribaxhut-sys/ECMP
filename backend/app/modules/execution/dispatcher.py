"""ExecutionDispatcher — dispatch planning foundation (TASK-056).



Connects ExecutionRun tasks to ExecutionRegistry via DispatchRequest planning.

Validates handler availability. NEVER invokes handlers.

"""



from __future__ import annotations

from collections.abc import Sequence

from app.core.logging import get_logger
from app.modules.execution.dispatch_models import (
    DispatchPolicy,
    DispatchRequest,
    DispatchResult,
)
from app.modules.execution.dispatch_validator import DispatchValidator
from app.modules.execution.models import ExecutionTask, freeze_mapping
from app.modules.execution.registry import ExecutionRegistry
from app.modules.execution.runtime_models import ExecutionRun

logger = get_logger(__name__)





class ExecutionDispatcher:

    """Prepare DispatchRequest / DispatchResult. No handler execution."""



    def __init__(

        self,

        registry: ExecutionRegistry | None = None,

        validator: DispatchValidator | None = None,

        policy: DispatchPolicy = DispatchPolicy.SEQUENTIAL,

    ) -> None:

        if policy is not DispatchPolicy.SEQUENTIAL:

            raise ValueError(

                f"Unsupported dispatch policy for TASK-056: {policy!r} "

                "(only SEQUENTIAL is allowed)"

            )

        self._registry = registry if registry is not None else ExecutionRegistry()

        self._validator = validator if validator is not None else DispatchValidator()

        self._policy = policy



    @property

    def registry(self) -> ExecutionRegistry:

        return self._registry



    @property

    def policy(self) -> DispatchPolicy:

        return self._policy



    @property

    def validator(self) -> DispatchValidator:

        return self._validator



    def dispatch(

        self,

        run: ExecutionRun,

        task: ExecutionTask,

        registry: ExecutionRegistry | None = None,

    ) -> tuple[DispatchRequest | None, DispatchResult]:

        """Validate and build a DispatchRequest. Never invokes handlers."""

        reg = registry if registry is not None else self._registry

        validation = self._validator.validate(run, task, reg)

        result = validation.result



        if not result.success or validation.run_task is None:

            logger.debug(

                "ExecutionDispatcher rejected dispatch plan",

                extra={

                    "extra_fields": {

                        "runId": str(run.run_id) if isinstance(run, ExecutionRun) else None,

                        "reason": result.reason,

                        "handlerRegistered": result.handler_registered,

                    }

                },

            )

            return None, result



        request = DispatchRequest(

            run_id=run.run_id,

            task_id=validation.run_task.task_id,

            task_type=task.task_type.strip(),

            target=task.target,

            configuration=freeze_mapping(dict(task.configuration)),

            context=run.context,

        )

        logger.debug(

            "ExecutionDispatcher prepared DispatchRequest (no execution)",

            extra={

                "extra_fields": {

                    "runId": str(request.run_id),

                    "taskId": str(request.task_id),

                    "taskType": request.task_type,

                    "policy": self._policy.value,

                }

            },

        )

        return request, result



    def dispatch_sequential(

        self,

        run: ExecutionRun,

        tasks: Sequence[ExecutionTask],

        registry: ExecutionRegistry | None = None,

    ) -> list[tuple[DispatchRequest | None, DispatchResult]]:

        """Plan dispatches in task order (SEQUENTIAL policy). No parallel, no invoke."""

        if self._policy is not DispatchPolicy.SEQUENTIAL:

            raise ValueError("dispatch_sequential requires SEQUENTIAL policy")

        ordered = sorted(tasks, key=lambda t: (t.order, t.task_type, str(t.task_id)))

        return [self.dispatch(run, task, registry=registry) for task in ordered]


