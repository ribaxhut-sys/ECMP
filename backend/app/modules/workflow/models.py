"""Workflow foundation value objects (TASK-052).

Immutable definitions, steps, and instances. No execution, no side effects.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping, Sequence


class WorkflowTrigger(StrEnum):
    """Complaint lifecycle events that may start a workflow (TASK-052)."""

    COMPLAINT_CREATED = "ComplaintCreated"
    COMPLAINT_ASSIGNED = "ComplaintAssigned"
    COMPLAINT_ACCEPTED = "ComplaintAccepted"
    COMPLAINT_IN_PROGRESS = "ComplaintInProgress"
    COMPLAINT_RESOLVED = "ComplaintResolved"
    COMPLAINT_CLOSED = "ComplaintClosed"
    COMPLAINT_ESCALATED = "ComplaintEscalated"


class WorkflowInstanceStatus(StrEnum):
    """Workflow instance lifecycle for TASK-052 (created plan only)."""

    CREATED = "CREATED"


@dataclass(frozen=True, slots=True)
class WorkflowStep:
    """Immutable planned step. Recorded only — never executed in TASK-052."""

    step_id: uuid.UUID
    name: str
    order: int
    action_type: str
    configuration: Mapping[str, Any]

    def as_dict(self) -> Mapping[str, object]:
        """Diagnostic serialization (not an HTTP / execution contract)."""
        return MappingProxyType(
            {
                "stepId": str(self.step_id),
                "name": self.name,
                "order": self.order,
                "actionType": self.action_type,
                "configuration": dict(self.configuration),
            }
        )


@dataclass(frozen=True, slots=True)
class WorkflowDefinition:
    """Immutable workflow template registered in WorkflowRegistry."""

    workflow_id: uuid.UUID
    name: str
    trigger: WorkflowTrigger
    steps: tuple[WorkflowStep, ...]
    metadata: Mapping[str, Any]

    def as_dict(self) -> Mapping[str, object]:
        """Diagnostic serialization (not an HTTP contract)."""
        return MappingProxyType(
            {
                "workflowId": str(self.workflow_id),
                "name": self.name,
                "trigger": self.trigger.value,
                "steps": [dict(s.as_dict()) for s in self.steps],
                "metadata": dict(self.metadata),
            }
        )


@dataclass(frozen=True, slots=True)
class WorkflowInstance:
    """Immutable recorded execution plan. Status is CREATED only (TASK-052)."""

    instance_id: uuid.UUID
    workflow_id: uuid.UUID
    trigger_event: str
    created_at: datetime
    status: WorkflowInstanceStatus
    steps: tuple[WorkflowStep, ...]
    metadata: Mapping[str, Any]

    def as_dict(self) -> Mapping[str, object]:
        """Diagnostic serialization (not an HTTP / execution contract)."""
        return MappingProxyType(
            {
                "instanceId": str(self.instance_id),
                "workflowId": str(self.workflow_id),
                "triggerEvent": self.trigger_event,
                "createdAt": self.created_at.isoformat(),
                "status": self.status.value,
                "steps": [dict(s.as_dict()) for s in self.steps],
                "metadata": dict(self.metadata),
            }
        )


def freeze_mapping(data: Mapping[str, Any] | None) -> Mapping[str, Any]:
    """Freeze a mapping for immutable value objects."""
    return MappingProxyType(dict(data or {}))


def freeze_steps(steps: Sequence[WorkflowStep]) -> tuple[WorkflowStep, ...]:
    """Normalize and freeze steps ordered by ``order`` then name."""
    return tuple(sorted(steps, key=lambda s: (s.order, s.name)))
