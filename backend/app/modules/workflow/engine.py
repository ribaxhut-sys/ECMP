"""WorkflowEngine — match events to definitions and record plans (TASK-052).

Does NOT execute steps, invoke Notification, Assignment, or external systems.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.core.logging import get_logger
from app.modules.complaint_events.models import ComplaintEvent
from app.modules.workflow.models import (
    WorkflowDefinition,
    WorkflowInstance,
    WorkflowInstanceStatus,
    WorkflowTrigger,
    freeze_mapping,
    freeze_steps,
)
from app.modules.workflow.registry import WorkflowRegistry
from app.modules.workflow.store import WorkflowInstanceStore

logger = get_logger(__name__)


class WorkflowEngine:
    """Orchestration planner: match → create instance → store. No execution."""

    def __init__(
        self,
        registry: WorkflowRegistry | None = None,
        store: WorkflowInstanceStore | None = None,
    ) -> None:
        self._registry = registry if registry is not None else WorkflowRegistry()
        self._store = store if store is not None else WorkflowInstanceStore()

    @property
    def registry(self) -> WorkflowRegistry:
        return self._registry

    @property
    def store(self) -> WorkflowInstanceStore:
        return self._store

    def process(self, event: ComplaintEvent) -> list[WorkflowInstance]:
        """Match ``event`` to registered definitions and record CREATED instances.

        Returns the list of newly created instances (empty when no match).
        Never runs step actions.
        """
        trigger_value = event.event_type.value
        try:
            trigger = WorkflowTrigger(trigger_value)
        except ValueError:
            logger.debug(
                "Skipping unsupported event for workflow",
                extra={"extra_fields": {"eventType": trigger_value}},
            )
            return []

        definitions = self._registry.match(trigger)
        if not definitions:
            logger.debug(
                "No workflow definitions matched event",
                extra={
                    "extra_fields": {
                        "eventType": trigger_value,
                        "eventId": str(event.event_id),
                    }
                },
            )
            return []

        created: list[WorkflowInstance] = []
        for definition in definitions:
            instance = self._create_instance(definition, event)
            self._store.add(instance)
            created.append(instance)
            logger.debug(
                "Workflow instance recorded (no execution)",
                extra={
                    "extra_fields": {
                        "instanceId": str(instance.instance_id),
                        "workflowId": str(instance.workflow_id),
                        "triggerEvent": instance.trigger_event,
                        "status": instance.status.value,
                        "stepCount": len(instance.steps),
                    }
                },
            )
        return created

    def _create_instance(
        self,
        definition: WorkflowDefinition,
        event: ComplaintEvent,
    ) -> WorkflowInstance:
        steps = freeze_steps(definition.steps)
        metadata = freeze_mapping(
            {
                "eventId": str(event.event_id),
                "complaintId": str(event.complaint_id),
                "complaintNumber": event.complaint_number,
                "currentStatus": event.current_status,
                "priority": event.priority,
                "workflowName": definition.name,
                "plannedActions": [
                    {
                        "stepId": str(s.step_id),
                        "name": s.name,
                        "order": s.order,
                        "actionType": s.action_type,
                        "configuration": dict(s.configuration),
                        "executed": False,
                    }
                    for s in steps
                ],
                "definitionMetadata": dict(definition.metadata),
            }
        )

        return WorkflowInstance(
            instance_id=uuid.uuid4(),
            workflow_id=definition.workflow_id,
            trigger_event=event.event_type.value,
            created_at=datetime.now(UTC),
            status=WorkflowInstanceStatus.CREATED,
            steps=steps,
            metadata=metadata,
        )
