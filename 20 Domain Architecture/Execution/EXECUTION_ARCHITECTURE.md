# Execution Architecture (TASK-053)

| Field | Value |
|---|---|
| ID | ARCH-EXEC-001 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-053) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Purpose

Introduce a **generic execution plan model** as shared infrastructure.
Workflow is the first producer. Nothing executes, sends, or schedules.

## Principles

1. Execution Plan is shared infrastructure.
2. Producers emit plans; executors (future) consume them.
3. Planner only — no side effects in TASK-053.
4. Registry catalogs handlers for future use; **must not invoke** them.

## Producer landscape

```text
                    ┌─ Workflow (TASK-052/053)     ✅ current
                    ├─ Scheduled Jobs               (future)
Producers ─────────┼─ SLA Engine                    (future)
                    ├─ AI Decision Engine            (future)
                    ├─ Manual Operations             (future)
                    └─ Integrations                  (future)
                              │
                              ▼
                     ExecutionPlanner
                              │
                              ▼
                     ExecutionPlan (PLANNED)
                              │
                              ▼
                     ExecutionPlanStore (in-memory)
```

## Event / workflow flow (current producer)

```text
ComplaintEvent
      │
      ▼
EventDispatcher
      │
      ▼
WorkflowEventHandler
      │
      ├─ WorkflowEngine → WorkflowInstance (CREATED)
      └─ on_instances → WorkflowExecutionProducer
                              │
                              ▼
                     ExecutionPlanner.from_workflow
                              │
                              ▼
                     ExecutionPlanStore
```

`WorkflowDefinition` / `WorkflowInstance` models are unchanged. The producer
hook is an optional observer on `WorkflowEventHandler`.

## Components

| Component | Responsibility |
|---|---|
| ExecutionPlan | Immutable plan (`status=PLANNED`) |
| ExecutionTask | Immutable task (`executed=false`) |
| ExecutionPlanner | Map producer input → plan |
| ExecutionPlanStore | In-memory buffer |
| ExecutionRegistry | Register task handlers; never invoke |
| WorkflowExecutionProducer | Workflow → plan bridge |

## Guarantees (TASK-053)

- No HTTP API
- No database / queue / scheduler / retry
- No Notification / Assignment / external invocation
- Registry handlers remain dormant

## Implementation

- `backend/app/modules/execution/`
- Composition: `backend/app/dependencies/events.py`

## Related

- `EXECUTION_GUIDE.md`
- `EXECUTION_RUNTIME_ARCHITECTURE.md` (TASK-054)
- `EXECUTION_RUNTIME_GUIDE.md` (TASK-054)
- `../Workflow/WORKFLOW_ARCHITECTURE.md`
- `../../04 Solution Architecture/ECMP_Solution_Architecture_v1.0.md`
