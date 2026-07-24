"""WorkflowRegistry — in-memory workflow definition catalog (TASK-052).

No persistence. Process-local only.
"""

from __future__ import annotations

import uuid

from app.modules.workflow.models import WorkflowDefinition, WorkflowTrigger


class WorkflowRegistry:
    """Register and match workflow definitions by trigger (in-memory)."""

    def __init__(self) -> None:
        self._by_id: dict[uuid.UUID, WorkflowDefinition] = {}

    def register(self, definition: WorkflowDefinition) -> None:
        """Register or replace a workflow definition by ``workflow_id``."""
        if not isinstance(definition, WorkflowDefinition):
            raise TypeError(
                f"definition must be WorkflowDefinition, got {type(definition).__name__}"
            )
        if not isinstance(definition.trigger, WorkflowTrigger):
            raise TypeError(
                f"trigger must be WorkflowTrigger, got {type(definition.trigger).__name__}"
            )
        self._by_id[definition.workflow_id] = definition

    def unregister(self, workflow_id: uuid.UUID) -> bool:
        """Remove a definition. Returns True if it existed."""
        return self._by_id.pop(workflow_id, None) is not None

    def get(self, workflow_id: uuid.UUID) -> WorkflowDefinition | None:
        """Return a registered definition or None."""
        return self._by_id.get(workflow_id)

    def all(self) -> list[WorkflowDefinition]:
        """Return all registered definitions (registration-id order unstable)."""
        return list(self._by_id.values())

    def match(self, trigger: WorkflowTrigger | str) -> list[WorkflowDefinition]:
        """Return all definitions whose trigger equals ``trigger``.

        Matching is exact on trigger value. Multiple definitions may match.
        """
        trigger_value = (
            trigger.value if isinstance(trigger, WorkflowTrigger) else str(trigger)
        )
        return [
            definition
            for definition in self._by_id.values()
            if definition.trigger.value == trigger_value
        ]

    def clear(self) -> None:
        """Remove all definitions (tests / diagnostics)."""
        self._by_id.clear()

    def __len__(self) -> int:
        return len(self._by_id)
