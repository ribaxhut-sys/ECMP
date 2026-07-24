"""Execution Plan foundation value objects (TASK-053).

Immutable plans and tasks. Nothing executes, sends, or schedules.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping, Sequence


class ExecutionPlanStatus(StrEnum):
    """Execution plan lifecycle for TASK-053 (planned only)."""

    PLANNED = "PLANNED"


class ExecutionPlanSource(StrEnum):
    """Known producers of execution plans (extensible)."""

    WORKFLOW = "WORKFLOW"
    SCHEDULED_JOB = "SCHEDULED_JOB"
    SLA_ENGINE = "SLA_ENGINE"
    AI_DECISION = "AI_DECISION"
    MANUAL_OPERATION = "MANUAL_OPERATION"
    INTEGRATION = "INTEGRATION"


@dataclass(frozen=True, slots=True)
class ExecutionTask:
    """Immutable planned task. ``executed`` defaults to False (TASK-053)."""

    task_id: uuid.UUID
    order: int
    task_type: str
    target: str
    configuration: Mapping[str, Any]
    executed: bool = False

    def as_dict(self) -> Mapping[str, object]:
        """Diagnostic serialization (not an HTTP / execution contract)."""
        return MappingProxyType(
            {
                "taskId": str(self.task_id),
                "order": self.order,
                "taskType": self.task_type,
                "target": self.target,
                "configuration": dict(self.configuration),
                "executed": self.executed,
            }
        )


@dataclass(frozen=True, slots=True)
class ExecutionPlan:
    """Immutable execution plan. Status is PLANNED only (TASK-053)."""

    plan_id: uuid.UUID
    source: str
    source_id: uuid.UUID
    created_at: datetime
    status: ExecutionPlanStatus
    tasks: tuple[ExecutionTask, ...]
    metadata: Mapping[str, Any]

    def as_dict(self) -> Mapping[str, object]:
        """Diagnostic serialization (not an HTTP / execution contract)."""
        return MappingProxyType(
            {
                "planId": str(self.plan_id),
                "source": self.source,
                "sourceId": str(self.source_id),
                "createdAt": self.created_at.isoformat(),
                "status": self.status.value,
                "tasks": [dict(t.as_dict()) for t in self.tasks],
                "metadata": dict(self.metadata),
            }
        )


def freeze_mapping(data: Mapping[str, Any] | None) -> Mapping[str, Any]:
    """Freeze a mapping for immutable value objects."""
    return MappingProxyType(dict(data or {}))


def freeze_tasks(tasks: Sequence[ExecutionTask]) -> tuple[ExecutionTask, ...]:
    """Normalize and freeze tasks ordered by ``order`` then task_type."""
    return tuple(sorted(tasks, key=lambda t: (t.order, t.task_type, str(t.task_id))))
