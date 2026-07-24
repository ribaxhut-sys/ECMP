"""Execution Foundation package (TASK-053 … TASK-056).



Shared execution-plan + runtime + engine + dispatcher infrastructure.

Dispatcher plans DispatchRequest only — never invokes handlers.

"""



from app.modules.execution.dispatch_models import (

    DispatchPolicy,

    DispatchRequest,

    DispatchResult,

)

from app.modules.execution.dispatch_validator import DispatchValidator

from app.modules.execution.dispatcher import ExecutionDispatcher

from app.modules.execution.engine import ExecutionEngine, ExecutionEngineResult

from app.modules.execution.lifecycle import (

    ExecutionLifecycle,

    ExecutionStateMachine,

    ExecutionTransition,

)

from app.modules.execution.models import (

    ExecutionPlan,

    ExecutionPlanSource,

    ExecutionPlanStatus,

    ExecutionTask,

)

from app.modules.execution.planner import ExecutionPlanner

from app.modules.execution.registry import ExecutionRegistry, ExecutionTaskHandler

from app.modules.execution.run_store import ExecutionRunStore

from app.modules.execution.runtime import ExecutionRuntime, build_execution_context

from app.modules.execution.runtime_models import (

    ExecutionContext,

    ExecutionResult,

    ExecutionRun,

    ExecutionRunStatus,

    ExecutionRunTask,

    ExecutionRunTaskStatus,

)

from app.modules.execution.store import ExecutionPlanStore

from app.modules.execution.workflow_producer import WorkflowExecutionProducer



__all__ = [

    "DispatchPolicy",

    "DispatchRequest",

    "DispatchResult",

    "DispatchValidator",

    "ExecutionContext",

    "ExecutionDispatcher",

    "ExecutionEngine",

    "ExecutionEngineResult",

    "ExecutionLifecycle",

    "ExecutionPlan",

    "ExecutionPlanSource",

    "ExecutionPlanStatus",

    "ExecutionPlanStore",

    "ExecutionPlanner",

    "ExecutionRegistry",

    "ExecutionResult",

    "ExecutionRun",

    "ExecutionRunStatus",

    "ExecutionRunStore",

    "ExecutionRunTask",

    "ExecutionRunTaskStatus",

    "ExecutionRuntime",

    "ExecutionStateMachine",

    "ExecutionTask",

    "ExecutionTaskHandler",

    "ExecutionTransition",

    "WorkflowExecutionProducer",

    "build_execution_context",

]


