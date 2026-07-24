"""ExecutionRuntime — prepare ExecutionRun from ExecutionPlan (TASK-054).



Creates run, expands tasks, attaches context, stores run.

Does NOT invoke handlers, registry, Notification, Assignment, or externals.

Does not know Complaint, Workflow, or Notification.

"""



from __future__ import annotations



import uuid

from datetime import UTC, datetime



from app.core.logging import get_logger

from app.modules.execution.models import ExecutionPlan, freeze_mapping

from app.modules.execution.run_store import ExecutionRunStore

from app.modules.execution.runtime_models import (

    ExecutionContext,

    ExecutionRun,

    ExecutionRunStatus,

    ExecutionRunTask,

    ExecutionRunTaskStatus,

)



logger = get_logger(__name__)





def build_execution_context(

    *,

    trace_id: str | None = None,

    correlation_id: str | None = None,

    tenant_id: str | None = None,

    user_id: str | None = None,

    metadata: dict[str, object] | None = None,

) -> ExecutionContext:

    """Create an immutable generic ExecutionContext."""

    return ExecutionContext(

        trace_id=trace_id if trace_id is not None else str(uuid.uuid4()),

        correlation_id=(

            correlation_id if correlation_id is not None else str(uuid.uuid4())

        ),

        tenant_id=tenant_id,

        user_id=user_id,

        metadata=freeze_mapping(metadata),

    )





class ExecutionRuntime:

    """Prepare ExecutionRun from ExecutionPlan. No handler invocation."""



    def __init__(self, store: ExecutionRunStore | None = None) -> None:

        self._store = store if store is not None else ExecutionRunStore()



    @property

    def store(self) -> ExecutionRunStore:

        return self._store



    def prepare(

        self,

        plan: ExecutionPlan,

        context: ExecutionContext | None = None,

    ) -> ExecutionRun:

        """Create ExecutionRun from plan: expand tasks, attach context, store.



        Does not execute tasks, invoke registry handlers, or send anything.

        """

        if not isinstance(plan, ExecutionPlan):

            raise TypeError(

                f"plan must be ExecutionPlan, got {type(plan).__name__}"

            )

        if context is not None and not isinstance(context, ExecutionContext):

            raise TypeError(

                f"context must be ExecutionContext, got {type(context).__name__}"

            )



        attached = context if context is not None else build_execution_context(

            correlation_id=str(plan.plan_id),

            metadata={"planId": str(plan.plan_id), "source": plan.source},

        )



        tasks = tuple(

            ExecutionRunTask(

                task_id=uuid.uuid4(),

                execution_task_id=plan_task.task_id,

                order=plan_task.order,

                status=ExecutionRunTaskStatus.CREATED,

                started_at=None,

                finished_at=None,

                result=None,

            )

            for plan_task in sorted(

                plan.tasks, key=lambda t: (t.order, t.task_type, str(t.task_id))

            )

        )



        run = ExecutionRun(

            run_id=uuid.uuid4(),

            plan_id=plan.plan_id,

            created_at=datetime.now(UTC),

            status=ExecutionRunStatus.CREATED,

            tasks=tasks,

            metadata=freeze_mapping(

                {

                    **dict(plan.metadata),

                    "planSource": plan.source,

                    "planStatus": plan.status.value,

                    "taskCount": len(tasks),

                    "runtime": "TASK-054",

                }

            ),

            context=attached,

        )



        self._store.add(run)

        logger.debug(

            "ExecutionRun prepared from ExecutionPlan (no execution)",

            extra={

                "extra_fields": {

                    "runId": str(run.run_id),

                    "planId": str(run.plan_id),

                    "status": run.status.value,

                    "taskCount": len(run.tasks),

                    "traceId": run.context.trace_id,

                    "correlationId": run.context.correlation_id,

                }

            },

        )

        return run


