"""Workflow Foundation package (TASK-052).

Orchestration planner only: match Complaint events → record WorkflowInstance.
No execution, transport, persistence, queue, scheduler, or HTTP API.
"""

from app.modules.workflow.engine import WorkflowEngine
from app.modules.workflow.factory import build_definition, build_step
from app.modules.workflow.handler import WorkflowEventHandler
from app.modules.workflow.models import (
    WorkflowDefinition,
    WorkflowInstance,
    WorkflowInstanceStatus,
    WorkflowStep,
    WorkflowTrigger,
)
from app.modules.workflow.registration import register_workflow_handler
from app.modules.workflow.registry import WorkflowRegistry
from app.modules.workflow.store import WorkflowInstanceStore

__all__ = [
    "WorkflowDefinition",
    "WorkflowEngine",
    "WorkflowEventHandler",
    "WorkflowInstance",
    "WorkflowInstanceStatus",
    "WorkflowInstanceStore",
    "WorkflowRegistry",
    "WorkflowStep",
    "WorkflowTrigger",
    "build_definition",
    "build_step",
    "register_workflow_handler",
]
