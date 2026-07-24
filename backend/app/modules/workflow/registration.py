"""Register Workflow consumer on EventDispatcher (TASK-052/053).

ComplaintService must never import this module.
Composition roots (dependencies) perform registration.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from app.modules.event_dispatcher import EventDispatcher
from app.modules.workflow.engine import WorkflowEngine
from app.modules.workflow.handler import WorkflowEventHandler
from app.modules.workflow.models import WorkflowInstance
from app.modules.workflow.registry import WorkflowRegistry
from app.modules.workflow.store import WorkflowInstanceStore


def register_workflow_handler(
    dispatcher: EventDispatcher,
    *,
    registry: WorkflowRegistry | None = None,
    store: WorkflowInstanceStore | None = None,
    engine: WorkflowEngine | None = None,
    handler: WorkflowEventHandler | None = None,
    on_instances: Callable[[Sequence[WorkflowInstance]], Any] | None = None,
) -> WorkflowEventHandler:
    """Register WorkflowEventHandler if not already present on ``dispatcher``."""
    existing = [
        h
        for h in dispatcher.registered_handlers()
        if isinstance(h, WorkflowEventHandler)
    ]
    if existing:
        return existing[0]

    resolved = handler or WorkflowEventHandler(
        engine=engine,
        registry=registry,
        store=store,
        on_instances=on_instances,
    )
    dispatcher.register(resolved)
    return resolved
