# Workflow Architecture (TASK-052)

| Field | Value |
|---|---|
| ID | ARCH-WF-001 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-052) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Purpose

Introduce a **non-executing** workflow orchestration layer that consumes
Complaint events and records immutable execution plans
(`WorkflowInstance` with status `CREATED`).

## Principles

1. Workflow reacts to Complaint events.
2. Workflow orchestrates **plans** for business processes.
3. Workflow **MUST NOT** own Complaint business logic.
4. No execution, automation, transport, or side effects in TASK-052.

## Event flow

```text
ComplaintService (Producer)
      │
      ▼
ComplaintEventFactory
      │
      ▼
EventDispatcher.dispatch(event)
      │
      ▼
WorkflowEventHandler.handle(event)
      │
      ▼
WorkflowEngine.process(event)
      │
      ├─ WorkflowRegistry.match(trigger)
      ├─ create WorkflowInstance (CREATED)
      └─ WorkflowInstanceStore.add(instance)
```

## Separation of concerns

| Layer | Owns | Does not own |
|---|---|---|
| Complaint / ECMF | Aggregate state, transitions (enforcer) | Workflow plans |
| Administration | Workflow Config (status matrix, ADR-008) | Runtime orchestration instances |
| Notification | Notification / Intent / Delivery plans | Workflow definitions |
| Workflow (this) | Definition registry + instance plans | Complaint mutations, sends, assigns |

## Components

### WorkflowDefinition

Immutable template: `workflow_id`, `name`, `trigger`, `steps`, `metadata`.

### WorkflowStep

Immutable planned step: `step_id`, `name`, `order`, `action_type`,
`configuration`.

### WorkflowTrigger

Exact match to Complaint event type strings:

- ComplaintCreated
- ComplaintAssigned
- ComplaintAccepted
- ComplaintInProgress
- ComplaintResolved
- ComplaintClosed
- ComplaintEscalated

### WorkflowInstance

Immutable recorded plan: `instance_id`, `workflow_id`, `trigger_event`,
`created_at`, `status`, `steps`, `metadata`.

**Status:** `CREATED` only.

### WorkflowRegistry

In-memory catalog of definitions. Match by trigger; multiple definitions
may match one event.

### WorkflowEngine

Match → create instance → store. **Does not** run `action_type`s.

### WorkflowEventHandler

Implements `EventHandler`. Registered from composition root
(`backend/app/dependencies/events.py`), never from `ComplaintService`.

## Guarantees (TASK-052)

- No HTTP API
- No database / queue / scheduler / retries
- No Notification / Assignment / external invocation
- Planned actions recorded with `executed: false` in instance metadata

## Downstream (TASK-053)

Optional `on_instances` observer on `WorkflowEventHandler` feeds
`WorkflowExecutionProducer` → `ExecutionPlanner` → `ExecutionPlan` (PLANNED).
`WorkflowDefinition` / `WorkflowInstance` models remain unchanged.

## Implementation

- `backend/app/modules/workflow/`
- Composition: `backend/app/dependencies/events.py`

## Related

- `WORKFLOW_GUIDE.md` — developer-oriented matching & model guide
- `../ECMF/EVENT_DISPATCHER.md`
- `../Execution/EXECUTION_ARCHITECTURE.md` — shared ExecutionPlan (TASK-053)
- `../../04 Solution Architecture/ECMP_Solution_Architecture_v1.0.md`
- ADR-008 (Workflow Config ownership ≠ this runtime layer)
- ADR-009 (broker deferred)
