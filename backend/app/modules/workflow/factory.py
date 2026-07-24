"""Helpers to build immutable workflow definitions (TASK-052)."""

from __future__ import annotations

import uuid
from typing import Any, Mapping, Sequence

from app.modules.workflow.models import (
    WorkflowDefinition,
    WorkflowStep,
    WorkflowTrigger,
    freeze_mapping,
    freeze_steps,
)


def build_step(
    *,
    name: str,
    order: int,
    action_type: str,
    configuration: Mapping[str, Any] | None = None,
    step_id: uuid.UUID | None = None,
) -> WorkflowStep:
    """Create an immutable WorkflowStep."""
    return WorkflowStep(
        step_id=step_id or uuid.uuid4(),
        name=name,
        order=order,
        action_type=action_type,
        configuration=freeze_mapping(configuration),
    )


def build_definition(
    *,
    name: str,
    trigger: WorkflowTrigger,
    steps: Sequence[WorkflowStep],
    metadata: Mapping[str, Any] | None = None,
    workflow_id: uuid.UUID | None = None,
) -> WorkflowDefinition:
    """Create an immutable WorkflowDefinition with ordered steps."""
    return WorkflowDefinition(
        workflow_id=workflow_id or uuid.uuid4(),
        name=name,
        trigger=trigger,
        steps=freeze_steps(steps),
        metadata=freeze_mapping(metadata),
    )
