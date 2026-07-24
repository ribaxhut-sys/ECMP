# Workflow Guide (TASK-052)

| Field | Value |
|---|---|
| ID | ARCH-WF-GUIDE-001 |
| Version | 1.0 |
| Owner | Solution Architect / Tech Lead |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-052) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## What this is

Foundation for workflow **planning** against Complaint lifecycle events.

## What this is NOT

- Not Administration Workflow Config (status transition matrix)
- Not an executor / state machine runner
- Not a bus, queue, or durable store
- Not an HTTP API

## Model

### WorkflowTrigger

| Trigger | Event type value |
|---|---|
| `COMPLAINT_CREATED` | `ComplaintCreated` |
| `COMPLAINT_ASSIGNED` | `ComplaintAssigned` |
| `COMPLAINT_ACCEPTED` | `ComplaintAccepted` |
| `COMPLAINT_IN_PROGRESS` | `ComplaintInProgress` |
| `COMPLAINT_RESOLVED` | `ComplaintResolved` |
| `COMPLAINT_CLOSED` | `ComplaintClosed` |
| `COMPLAINT_ESCALATED` | `ComplaintEscalated` |

### WorkflowStep

| Field | Notes |
|---|---|
| `step_id` | UUID |
| `name` | Human-readable step name |
| `order` | Sort key for the recorded plan |
| `action_type` | Opaque string (e.g. `NOTIFY`) — **not executed** |
| `configuration` | Frozen mapping of planned parameters |

### WorkflowDefinition

| Field | Notes |
|---|---|
| `workflow_id` | UUID |
| `name` | Definition name |
| `trigger` | `WorkflowTrigger` |
| `steps` | Ordered tuple of `WorkflowStep` |
| `metadata` | Frozen mapping |

### WorkflowInstance

| Field | Notes |
|---|---|
| `instance_id` | UUID |
| `workflow_id` | Source definition |
| `trigger_event` | Event type string that matched |
| `created_at` | UTC timestamp |
| `status` | Always `CREATED` |
| `steps` | Copy of planned steps |
| `metadata` | Includes `eventId`, `complaintId`, `plannedActions` (`executed: false`) |

## Matching rules

1. Handler accepts only `ComplaintEvent` instances; others are ignored.
2. `event.event_type.value` must equal a `WorkflowTrigger` value.
3. `WorkflowRegistry.match(trigger)` returns **all** definitions with that
   trigger (exact string equality).
4. Engine creates **one** `WorkflowInstance` per matched definition.
5. If zero definitions match → no instance (not an error).
6. Multiple definitions on the same trigger → multiple instances.
7. Steps are recorded in ascending `order` (then name); **never executed**.

## Registration (composition root)

```text
get_event_dispatcher()
  → register_notification_handler(...)
  → register_dashboard_projection_handler(...)
  → register_kpi_projection_handler(...)
  → register_workflow_handler(registry=..., store=...)
```

`ComplaintService` must never import the workflow module.

## Example (in-process)

```python
from app.modules.workflow import (
    WorkflowTrigger,
    build_definition,
    build_step,
    register_workflow_handler,
)
from app.modules.event_dispatcher import EventDispatcher

registry = ...  # WorkflowRegistry
store = ...     # WorkflowInstanceStore

registry.register(
    build_definition(
        name="On Created",
        trigger=WorkflowTrigger.COMPLAINT_CREATED,
        steps=[
            build_step(
                name="plan-notify",
                order=1,
                action_type="NOTIFY",
                configuration={"template": "complaint.created"},
            )
        ],
    )
)

dispatcher = EventDispatcher()
register_workflow_handler(dispatcher, registry=registry, store=store)
# dispatcher.dispatch(complaint_event) → CREATED instance in store
```

## Out of scope (STOP)

Execution, persistence, HTTP, TASK-053+.
