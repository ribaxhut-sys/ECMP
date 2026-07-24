"""ExecutionRegistry — register future task handlers (TASK-053).

Handlers are catalogued only. Do NOT invoke them.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


# Future executor may call handlers as (task, plan) -> None. Never invoked here.
ExecutionTaskHandler = Callable[..., Any]


class ExecutionRegistry:
    """In-memory catalog of task_type → handler for future execution."""

    def __init__(self) -> None:
        self._handlers: dict[str, ExecutionTaskHandler] = {}

    def register(self, task_type: str, handler: ExecutionTaskHandler) -> None:
        """Register or replace a handler for ``task_type``. Does not invoke it."""
        if not task_type or not str(task_type).strip():
            raise ValueError("task_type must be a non-empty string")
        if not callable(handler):
            raise TypeError(
                f"handler must be callable, got {type(handler).__name__}"
            )
        self._handlers[str(task_type)] = handler

    def unregister(self, task_type: str) -> bool:
        """Remove a handler. Returns True if it existed."""
        return self._handlers.pop(task_type, None) is not None

    def get(self, task_type: str) -> ExecutionTaskHandler | None:
        """Return a registered handler or None. Does not invoke it."""
        return self._handlers.get(task_type)

    def has(self, task_type: str) -> bool:
        return task_type in self._handlers

    def task_types(self) -> list[str]:
        return list(self._handlers.keys())

    def clear(self) -> None:
        self._handlers.clear()

    def __len__(self) -> int:
        return len(self._handlers)
