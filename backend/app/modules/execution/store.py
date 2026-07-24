"""ExecutionPlanStore — in-memory plan buffer (TASK-053).

No database, queue, or scheduler.
"""

from __future__ import annotations

import uuid

from app.modules.execution.models import ExecutionPlan


class ExecutionPlanStore:
    """Process-local list of recorded execution plans."""

    def __init__(self) -> None:
        self._items: list[ExecutionPlan] = []

    def add(self, plan: ExecutionPlan) -> None:
        if not isinstance(plan, ExecutionPlan):
            raise TypeError(
                f"plan must be ExecutionPlan, got {type(plan).__name__}"
            )
        self._items.append(plan)

    def get(self, plan_id: uuid.UUID) -> ExecutionPlan | None:
        for item in self._items:
            if item.plan_id == plan_id:
                return item
        return None

    def all(self) -> list[ExecutionPlan]:
        return list(self._items)

    def by_source(self, source: str) -> list[ExecutionPlan]:
        return [p for p in self._items if p.source == source]

    def by_source_id(self, source_id: uuid.UUID) -> list[ExecutionPlan]:
        return [p for p in self._items if p.source_id == source_id]

    def clear(self) -> None:
        self._items.clear()

    def __len__(self) -> int:
        return len(self._items)
