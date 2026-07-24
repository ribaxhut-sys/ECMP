"""DispatchValidator — validate dispatch readiness (TASK-056).



Checks task presence, task type, handler registration, and run status.

Never invokes handlers.

"""



from __future__ import annotations



from dataclasses import dataclass



from app.modules.execution.dispatch_models import DispatchResult

from app.modules.execution.models import ExecutionTask

from app.modules.execution.registry import ExecutionRegistry

from app.modules.execution.runtime_models import (

    ExecutionRun,

    ExecutionRunStatus,

    ExecutionRunTask,

)



_DISPATCHABLE_STATUSES = frozenset(

    {

        ExecutionRunStatus.READY,

        ExecutionRunStatus.RUNNING,

    }

)





@dataclass(frozen=True, slots=True)

class DispatchValidation:

    """Internal validation outcome with optional resolved run task."""



    result: DispatchResult

    run_task: ExecutionRunTask | None = None





class DispatchValidator:

    """Validate dispatch inputs. Catalog lookup only — never call handlers."""



    def validate(

        self,

        run: ExecutionRun,

        task: ExecutionTask,

        registry: ExecutionRegistry,

    ) -> DispatchValidation:

        if not isinstance(run, ExecutionRun):

            raise TypeError(

                f"run must be ExecutionRun, got {type(run).__name__}"

            )

        if not isinstance(task, ExecutionTask):

            raise TypeError(

                f"task must be ExecutionTask, got {type(task).__name__}"

            )

        if not isinstance(registry, ExecutionRegistry):

            raise TypeError(

                f"registry must be ExecutionRegistry, got {type(registry).__name__}"

            )



        if run.status not in _DISPATCHABLE_STATUSES:

            return DispatchValidation(

                result=DispatchResult(

                    success=False,

                    handler_registered=False,

                    reason=(

                        f"INVALID_STATE: run status {run.status.value} "

                        "must be READY or RUNNING"

                    ),

                )

            )



        run_task = next(

            (t for t in run.tasks if t.execution_task_id == task.task_id),

            None,

        )

        if run_task is None:

            return DispatchValidation(

                result=DispatchResult(

                    success=False,

                    handler_registered=False,

                    reason=f"TASK_NOT_FOUND: execution_task_id={task.task_id}",

                )

            )



        task_type = (task.task_type or "").strip()

        if not task_type:

            return DispatchValidation(

                result=DispatchResult(

                    success=False,

                    handler_registered=False,

                    reason="UNKNOWN_TASK_TYPE: empty task_type",

                )

            )



        handler_registered = registry.has(task_type)

        if not handler_registered:

            return DispatchValidation(

                result=DispatchResult(

                    success=False,

                    handler_registered=False,

                    reason=f"HANDLER_NOT_REGISTERED: task_type={task_type}",

                )

            )



        return DispatchValidation(

            result=DispatchResult(

                success=True,

                handler_registered=True,

                reason=f"DISPATCH_READY: task_type={task_type}",

            ),

            run_task=run_task,

        )


