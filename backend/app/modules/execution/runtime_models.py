"""Execution Runtime foundation value objects (TASK-054 / TASK-055).

Immutable run / task / context / result. Nothing executes, sends, or schedules.
Does not know Complaint, Workflow, or Notification.

TASK-055 expands ExecutionRunStatus for lifecycle transition validation only.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping


class ExecutionRunStatus(StrEnum):
    """Execution run lifecycle states (TASK-055 transition validation)."""

    CREATED = "CREATED"
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ExecutionRunTaskStatus(StrEnum):
    """Execution run-task lifecycle for TASK-054 (created only)."""

    CREATED = "CREATED"


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    """Foundation result object. No execution performed (TASK-054)."""

    success: bool
    error_code: str | None = None
    message: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    def as_dict(self) -> Mapping[str, object]:
        """Diagnostic serialization (not an HTTP / execution contract)."""
        return MappingProxyType(
            {
                "success": self.success,
                "errorCode": self.error_code,
                "message": self.message,
                "metadata": dict(self.metadata),
            }
        )


@dataclass(frozen=True, slots=True)
class ExecutionContext:
    """Generic runtime context. Domain-agnostic (TASK-054)."""

    trace_id: str
    correlation_id: str
    tenant_id: str | None = None
    user_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    def as_dict(self) -> Mapping[str, object]:
        """Diagnostic serialization (not an HTTP / execution contract)."""
        return MappingProxyType(
            {
                "traceId": self.trace_id,
                "correlationId": self.correlation_id,
                "tenantId": self.tenant_id,
                "userId": self.user_id,
                "metadata": dict(self.metadata),
            }
        )


@dataclass(frozen=True, slots=True)
class ExecutionRunTask:
    """Immutable run task expanded from a plan task. Status CREATED (TASK-054)."""

    task_id: uuid.UUID
    execution_task_id: uuid.UUID
    order: int
    status: ExecutionRunTaskStatus = ExecutionRunTaskStatus.CREATED
    started_at: datetime | None = None
    finished_at: datetime | None = None
    result: ExecutionResult | None = None

    def as_dict(self) -> Mapping[str, object]:
        """Diagnostic serialization (not an HTTP / execution contract)."""
        return MappingProxyType(
            {
                "taskId": str(self.task_id),
                "executionTaskId": str(self.execution_task_id),
                "order": self.order,
                "status": self.status.value,
                "startedAt": self.started_at.isoformat() if self.started_at else None,
                "finishedAt": self.finished_at.isoformat() if self.finished_at else None,
                "result": dict(self.result.as_dict()) if self.result else None,
            }
        )


@dataclass(frozen=True, slots=True)
class ExecutionRun:
    """Immutable execution run. Status managed by ExecutionEngine (TASK-055)."""

    run_id: uuid.UUID
    plan_id: uuid.UUID
    created_at: datetime
    status: ExecutionRunStatus
    tasks: tuple[ExecutionRunTask, ...]
    metadata: Mapping[str, Any]
    context: ExecutionContext

    def as_dict(self) -> Mapping[str, object]:
        """Diagnostic serialization (not an HTTP / execution contract)."""
        return MappingProxyType(
            {
                "runId": str(self.run_id),
                "planId": str(self.plan_id),
                "createdAt": self.created_at.isoformat(),
                "status": self.status.value,
                "tasks": [dict(t.as_dict()) for t in self.tasks],
                "metadata": dict(self.metadata),
                "context": dict(self.context.as_dict()),
            }
        )

