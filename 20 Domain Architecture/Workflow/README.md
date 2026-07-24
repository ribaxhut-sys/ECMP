# Domain Architecture — Workflow

| Field | Value |
|---|---|
| ID | DOM-WF-001 |
| Version | 1.0 |
| Owner | Solution Architect / ECMF PO |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-052) |
| Status | 🟢 Approved (TASK-052 foundation) |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Objective

Provide an **orchestration planning layer** that reacts to Complaint lifecycle
events and records what *would* run — without executing actions, owning
Complaint business logic, or replacing Administration Workflow Config (ADR-008).

## Bounded Context

**Workflow (runtime orchestration)** ≠ **Workflow Config (Administration)**.

| Concept | Owner | Purpose |
|---|---|---|
| Workflow Config (status transitions) | Administration (ADR-008) | Allowed Case status transitions; ECMF enforces |
| Workflow Foundation (TASK-052) | Workflow module | Match Complaint events → record `WorkflowInstance` plans |

Workflow **must not** own Complaint aggregate rules, Assignment, Resolution,
Notification send, or Escalation logic.

## In Scope (TASK-052)

- `WorkflowDefinition`, `WorkflowStep`, `WorkflowTrigger`
- `WorkflowInstance` (status **CREATED** only)
- `WorkflowRegistry` (in-memory)
- `WorkflowEngine` (match + record plan)
- `WorkflowInstanceStore` (in-memory)
- `WorkflowEventHandler` implementing `EventHandler`

## Out of Scope (STOP)

- Action execution / automation
- Transport, queue, scheduler, retries
- Database persistence
- HTTP / OpenAPI endpoints
- Changes to Complaint aggregate, ComplaintContext, ComplaintEvent,
  EventDispatcher, Notification*, DashboardProjection, KpiProjection,
  Assignment, Resolution, Appointment, Escalation
- Execution runtime (TASK-053 provides ExecutionPlan; TASK-054+)

## Key Components

| Component | Responsibility |
|---|---|
| WorkflowRegistry | Register / match definitions by trigger |
| WorkflowEngine | Match event → create instance → store plan |
| WorkflowInstanceStore | Hold CREATED instances in process memory |
| WorkflowEventHandler | EventDispatcher consumer → engine |

## Key Flows

```text
ComplaintEvent
      │
      ▼
EventDispatcher
      │
      ▼
WorkflowEventHandler
      │
      ▼
WorkflowEngine
      │
      ▼
WorkflowInstanceStore  (CREATED plans only)
```

## Data Ownership

Runtime definitions and instances are **process-local** (lost on restart).
Authoritative status-transition config remains Administration (ADR-008).

## Integrations

- **Events consumed (runtime):** ComplaintCreated, ComplaintAssigned,
  ComplaintAccepted, ComplaintInProgress, ComplaintResolved, ComplaintClosed,
  ComplaintEscalated (via in-process dispatcher; not a broker).
- **Does not invoke:** Notification, Assignment, external systems.

## NFR Considerations

Foundation only — no durability, no at-least-once delivery beyond the
current in-process dispatcher contract (ADR-009 broker deferred).

## Diagram Links

- Workflow Guide: `WORKFLOW_GUIDE.md`
- Architecture detail: `WORKFLOW_ARCHITECTURE.md`

## Open Questions

- Durable workflow store / execution runtime — deferred to later tasks.
