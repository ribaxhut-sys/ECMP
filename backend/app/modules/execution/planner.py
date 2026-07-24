"""ExecutionPlanner — build ExecutionPlan from producers (TASK-053).

Planner only. Does not execute tasks or invoke ExecutionRegistry handlers.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.core.logging import get_logger
from app.modules.execution.models import (
    ExecutionPlan,
    ExecutionPlanSource,
    ExecutionPlanStatus,
    ExecutionTask,
    freeze_mapping,
    freeze_tasks,
)
from app.modules.workflow.models import WorkflowInstance, WorkflowStep

logger = get_logger(__name__)


def _target_for_step(step: WorkflowStep) -> str:
    raw = step.configuration.get("target")
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    return f"workflow.step:{step.name}"


class ExecutionPlanner:
    """Maps producer outputs to immutable ExecutionPlan (no execution)."""

    def from_workflow(self, instance: WorkflowInstance) -> ExecutionPlan:
        """Map a WorkflowInstance to a PLANNED ExecutionPlan.

        Each WorkflowStep becomes an ExecutionTask with ``executed=False``.
        Tasks preserve step order. Registry handlers are never consulted.
        """
        if not isinstance(instance, WorkflowInstance):
            raise TypeError(
                f"instance must be WorkflowInstance, got {type(instance).__name__}"
            )

        tasks = freeze_tasks(
            [
                ExecutionTask(
                    task_id=uuid.uuid4(),
                    order=step.order,
                    task_type=step.action_type,
                    target=_target_for_step(step),
                    configuration=freeze_mapping(dict(step.configuration)),
                    executed=False,
                )
                for step in instance.steps
            ]
        )

        metadata = freeze_mapping(
            {
                "producer": ExecutionPlanSource.WORKFLOW.value,
                "workflowId": str(instance.workflow_id),
                "workflowInstanceId": str(instance.instance_id),
                "triggerEvent": instance.trigger_event,
                "workflowStatus": instance.status.value,
                "complaintId": instance.metadata.get("complaintId"),
                "eventId": instance.metadata.get("eventId"),
                "workflowName": instance.metadata.get("workflowName"),
                "taskCount": len(tasks),
            }
        )

        plan = ExecutionPlan(
            plan_id=uuid.uuid4(),
            source=ExecutionPlanSource.WORKFLOW.value,
            source_id=instance.instance_id,
            created_at=datetime.now(UTC),
            status=ExecutionPlanStatus.PLANNED,
            tasks=tasks,
            metadata=metadata,
        )

        logger.debug(
            "ExecutionPlan recorded from WorkflowInstance (no execution)",
            extra={
                "extra_fields": {
                    "planId": str(plan.plan_id),
                    "source": plan.source,
                    "sourceId": str(plan.source_id),
                    "status": plan.status.value,
                    "taskCount": len(plan.tasks),
                }
            },
        )
        return plan
