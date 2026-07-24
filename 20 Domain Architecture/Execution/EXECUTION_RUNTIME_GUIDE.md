# Execution Runtime Guide (TASK-054)



| Field | Value |

|---|---|

| ID | ARCH-EXEC-RT-GUIDE-001 |

| Version | 1.0 |

| Owner | Solution Architect / Tech Lead |

| Reviewer | Tech Lead |

| Approver | Architecture Board (delegated via TASK-054) |

| Status | Approved |

| Last Review | 2026-07-24 |

| Next Review | 2026-10-24 |



## What this is



Generic **execution runtime** foundation: prepare what would run from a plan.



## What this is NOT



- Not an executor / worker / queue

- Not handler invocation (`ExecutionRegistry` stays dormant)

- Not Notification / Assignment / external I/O

- Not Workflow or Complaint domain logic

- Not an HTTP API / database / scheduler



## Model



### ExecutionRun



| Field | Notes |

|---|---|

| `run_id` | UUID |

| `plan_id` | Source `ExecutionPlan.plan_id` |

| `created_at` | UTC |

| `status` | **CREATED** only |

| `tasks` | Ordered tuple of `ExecutionRunTask` |

| `metadata` | Frozen mapping (includes plan snapshot keys) |

| `context` | Attached `ExecutionContext` |



### ExecutionRunTask



| Field | Notes |

|---|---|

| `task_id` | New UUID for the run task |

| `execution_task_id` | Links to plan `ExecutionTask.task_id` |

| `order` | Preserved from plan task |

| `status` | Default **CREATED** |

| `started_at` | Always `None` in TASK-054 |

| `finished_at` | Always `None` in TASK-054 |

| `result` | Always `None` in TASK-054 |



### ExecutionContext



| Field | Notes |

|---|---|

| `trace_id` | Opaque string (default UUID) |

| `correlation_id` | Opaque string (default = `plan_id`) |

| `tenant_id` | Optional |

| `user_id` | Optional |

| `metadata` | Frozen mapping |



### ExecutionResult (foundation only)



| Field | Notes |

|---|---|

| `success` | bool |

| `error_code` | optional |

| `message` | optional |

| `metadata` | Frozen mapping |



Not produced by `prepare()` in TASK-054.



## Runtime rules



1. Input must be an `ExecutionPlan`.

2. Output is an `ExecutionRun` with `status=CREATED`.

3. Each plan `ExecutionTask` → one `ExecutionRunTask`.

4. `execution_task_id` ← plan task `task_id`.

5. Run task `task_id` is newly generated.

6. Tasks keep plan order.

7. Attach provided `ExecutionContext`, or build a default via `build_execution_context`.

8. Store the run in `ExecutionRunStore` (in-memory).

9. **Never** call `ExecutionRegistry` handlers.

10. **Never** invoke Notification / Assignment / external systems.

11. Runtime modules must not import Complaint / Workflow / Notification.



## Usage (prepare only)



```text

plan = …  # from ExecutionPlanner / ExecutionPlanStore

runtime = ExecutionRuntime(store=ExecutionRunStore())

run = runtime.prepare(plan)                    # default context

run = runtime.prepare(plan, context=ctx)       # explicit context

```



## Composition



```text

get_execution_runtime()     → ExecutionRuntime (DI)

get_execution_run_store()   → ExecutionRunStore (DI)



Event path still ends at ExecutionPlanStore (TASK-053).

Runtime.prepare is not auto-invoked from WorkflowExecutionProducer.

```



## Out of scope (STOP)



Handler execution, retries, queues, persistence, HTTP, TASK-055+.


