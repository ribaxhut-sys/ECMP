"""Workflow → ExecutionPlan producer bridge (TASK-053).

Workflow is one producer of ExecutionPlan. Does not execute tasks.
"""

from __future__ import annotations

from collections.abc import Sequence

from app.core.logging import get_logger
from app.modules.execution.models import ExecutionPlan
from app.modules.execution.planner import ExecutionPlanner
from app.modules.execution.store import ExecutionPlanStore
from app.modules.workflow.models import WorkflowInstance

logger = get_logger(__name__)


class WorkflowExecutionProducer:
    """Produces ExecutionPlan records from WorkflowInstance(s)."""

    def __init__(
        self,
        planner: ExecutionPlanner | None = None,
        store: ExecutionPlanStore | None = None,
    ) -> None:
        self._planner = planner if planner is not None else ExecutionPlanner()
        self._store = store if store is not None else ExecutionPlanStore()

    @property
    def planner(self) -> ExecutionPlanner:
        return self._planner

    @property
    def store(self) -> ExecutionPlanStore:
        return self._store

    def produce(
        self, instances: Sequence[WorkflowInstance]
    ) -> list[ExecutionPlan]:
        """Plan and store one ExecutionPlan per WorkflowInstance. No execution."""
        plans: list[ExecutionPlan] = []
        for instance in instances:
            plan = self._planner.from_workflow(instance)
            self._store.add(plan)
            plans.append(plan)
        logger.debug(
            "WorkflowExecutionProducer created plans",
            extra={"extra_fields": {"planCount": len(plans)}},
        )
        return plans

    def __call__(self, instances: Sequence[WorkflowInstance]) -> list[ExecutionPlan]:
        """Callable form for WorkflowEventHandler.on_instances hook."""
        return self.produce(instances)
