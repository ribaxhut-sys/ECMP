"""WorkflowInstanceStore — in-memory instance buffer (TASK-052).

No database, queue, or scheduler.
"""

from __future__ import annotations

import uuid

from app.modules.workflow.models import WorkflowInstance


class WorkflowInstanceStore:
    """Process-local list of recorded workflow instances."""

    def __init__(self) -> None:
        self._items: list[WorkflowInstance] = []

    def add(self, instance: WorkflowInstance) -> None:
        if not isinstance(instance, WorkflowInstance):
            raise TypeError(
                f"instance must be WorkflowInstance, got {type(instance).__name__}"
            )
        self._items.append(instance)

    def get(self, instance_id: uuid.UUID) -> WorkflowInstance | None:
        for item in self._items:
            if item.instance_id == instance_id:
                return item
        return None

    def all(self) -> list[WorkflowInstance]:
        return list(self._items)

    def by_workflow(self, workflow_id: uuid.UUID) -> list[WorkflowInstance]:
        return [i for i in self._items if i.workflow_id == workflow_id]

    def by_trigger_event(self, trigger_event: str) -> list[WorkflowInstance]:
        return [i for i in self._items if i.trigger_event == trigger_event]

    def clear(self) -> None:
        self._items.clear()

    def __len__(self) -> int:
        return len(self._items)
