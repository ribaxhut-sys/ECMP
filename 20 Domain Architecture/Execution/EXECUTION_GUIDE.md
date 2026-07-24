# Execution Guide (TASK-053)

| Field | Value |
|---|---|
| ID | ARCH-EXEC-GUIDE-001 |
| Version | 1.0 |
| Owner | Solution Architect / Tech Lead |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-053) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## What this is

Generic **execution plan** foundation: record what would run.

## What this is NOT

- Not an executor / worker / queue
- Not Notification delivery
- Not Workflow Config (ADR-008)
- Not an HTTP API

## Model

### ExecutionPlan

| Field | Notes |
|---|---|
| `plan_id` | UUID |
| `source` | Producer key (e.g. `WORKFLOW`) |
| `source_id` | Producer entity id (e.g. `WorkflowInstance.instance_id`) |
| `created_at` | UTC |
| `status` | **PLANNED** only |
| `tasks` | Ordered tuple of `ExecutionTask` |
| `metadata` | Frozen mapping (traceability) |

### ExecutionTask

| Field | Notes |
|---|---|
| `task_id` | UUID |
| `order` | Sort key |
| `task_type` | Opaque type (from workflow `action_type`) |
| `target` | Destination key |
| `configuration` | Frozen mapping |
| `executed` | Default **`false`** |

### ExecutionPlanSource (known keys)

`WORKFLOW` · `SCHEDULED_JOB` · `SLA_ENGINE` · `AI_DECISION` ·
`MANUAL_OPERATION` · `INTEGRATION`

## Planner rules (Workflow mapping)

1. Input must be a `WorkflowInstance`.
2. Each `WorkflowStep` → one `ExecutionTask`.
3. `task_type` ← `step.action_type`.
4. `order` ← `step.order` (tasks frozen sorted by order).
5. `target` ← `configuration["target"]` if present, else
   `workflow.step:{name}`.
6. `configuration` ← copy of step configuration.
7. `executed` always `false`.
8. Plan `source` = `WORKFLOW`, `source_id` = `instance.instance_id`.
9. Plan `status` = `PLANNED`.
10. **Never** call `ExecutionRegistry` handlers.
11. **Never** invoke Notification / Assignment / external systems.

## Registry rules

1. `register(task_type, handler)` stores a callable for future execution.
2. `get` / `has` / `task_types` are catalog reads only.
3. Registration and lookup **must not** invoke the handler.

## Composition

```text
get_event_dispatcher()
  → … existing consumers …
  → register_workflow_handler(..., on_instances=WorkflowExecutionProducer)
```

## Out of scope for TASK-053

Persistence, HTTP, handler execution.

Runtime prepare foundation is TASK-054 — see `EXECUTION_RUNTIME_GUIDE.md`.
