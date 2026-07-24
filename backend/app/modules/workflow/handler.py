"""WorkflowEventHandler — EventDispatcher consumer (TASK-052/053).

Delegates to WorkflowEngine. Does not execute workflow actions.
Optional on_instances hook lets shared Execution Plan infrastructure
consume WorkflowInstance as a producer (TASK-053) without changing
WorkflowDefinition / WorkflowInstance models.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from app.core.logging import get_logger
from app.modules.complaint_events.models import ComplaintEvent
from app.modules.event_dispatcher.handler import EventHandler
from app.modules.workflow.engine import WorkflowEngine
from app.modules.workflow.models import WorkflowInstance
from app.modules.workflow.registry import WorkflowRegistry
from app.modules.workflow.store import WorkflowInstanceStore

logger = get_logger(__name__)

WorkflowInstanceObserver = Callable[[Sequence[WorkflowInstance]], Any]


class WorkflowEventHandler(EventHandler):
    """Consumes ComplaintEvent; records matching WorkflowInstance plans."""

    def __init__(
        self,
        engine: WorkflowEngine | None = None,
        registry: WorkflowRegistry | None = None,
        store: WorkflowInstanceStore | None = None,
        on_instances: WorkflowInstanceObserver | None = None,
    ) -> None:
        if engine is not None:
            self._engine = engine
        else:
            self._engine = WorkflowEngine(registry=registry, store=store)
        self._on_instances = on_instances

    @property
    def engine(self) -> WorkflowEngine:
        return self._engine

    @property
    def registry(self) -> WorkflowRegistry:
        return self._engine.registry

    @property
    def store(self) -> WorkflowInstanceStore:
        return self._engine.store

    def handle(self, event: Any) -> None:
        if not isinstance(event, ComplaintEvent):
            return

        instances = self._engine.process(event)
        if self._on_instances is not None and instances:
            self._on_instances(instances)

        logger.debug(
            "WorkflowEventHandler processed event",
            extra={
                "extra_fields": {
                    "eventType": event.event_type.value,
                    "eventId": str(event.event_id),
                    "instancesCreated": len(instances),
                }
            },
        )
