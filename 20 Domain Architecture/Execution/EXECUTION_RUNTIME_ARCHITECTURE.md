# Execution Runtime Architecture (TASK-054)



| Field | Value |

|---|---|

| ID | ARCH-EXEC-RT-001 |

| Version | 1.0 |

| Owner | Solution Architect |

| Reviewer | Tech Lead |

| Approver | Architecture Board (delegated via TASK-054) |

| Status | Approved |

| Last Review | 2026-07-24 |

| Next Review | 2026-10-24 |



## Purpose



Introduce a **generic execution runtime foundation** as shared infrastructure.

Runtime consumes `ExecutionPlan` and prepares `ExecutionRun`. Nothing executes,

sends, or schedules.



## Principles



1. Execution Runtime is shared infrastructure (Clean Architecture / DDD).

2. Runtime **must not** know Complaint, Workflow, or Notification.

3. Prepare only — expand tasks, attach context, store run.

4. Open/Closed: future executors consume runs without changing this foundation.

5. Immutable models; dependency injection for store/runtime.



## Pipeline



```text

Producers (Workflow / Jobs / SLA / AI / Manual / Integrations)

                              │

                              ▼

                     ExecutionPlan (PLANNED)     ← TASK-053

                              │

                              ▼

                     ExecutionRuntime.prepare

                              │

                              ├─ Create ExecutionRun (CREATED)

                              ├─ Expand ExecutionRunTask(s)

                              ├─ Attach ExecutionContext

                              └─ Store via ExecutionRunStore

                              │

                              ▼

                     ExecutionRun (CREATED)      ← TASK-054

                              │

                              ▼

                     Future executor (TASK-055+) — NOT in scope

```



## Components



| Component | Responsibility |

|---|---|

| ExecutionRun | Immutable run (`status=CREATED`) |

| ExecutionRunTask | Immutable expanded task (`status=CREATED`) |

| ExecutionContext | Generic trace / correlation / tenant / user |

| ExecutionResult | Foundation result shape only (unused in prepare) |

| ExecutionRuntime | Plan → Run prepare pipeline |

| ExecutionRunStore | In-memory buffer |



## Guarantees (TASK-054)



- No handler / registry invocation

- No Notification / Assignment / external calls

- No HTTP API

- No database / queue / scheduler / retry

- No Complaint / Workflow / Notification imports in runtime modules

- Plan producer path (TASK-053) unchanged; runtime is opt-in after plan



## Implementation



- `backend/app/modules/execution/runtime_models.py`

- `backend/app/modules/execution/runtime.py`

- `backend/app/modules/execution/run_store.py`

- DI: `backend/app/dependencies/events.py` (`get_execution_runtime`, `get_execution_run_store`)



## Related



- `EXECUTION_ARCHITECTURE.md` (TASK-053 plan foundation)

- `EXECUTION_RUNTIME_GUIDE.md`

- `EXECUTION_GUIDE.md`

- `../../04 Solution Architecture/ECMP_Solution_Architecture_v1.0.md`


