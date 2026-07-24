# Execution Runtime — Developer Guide (TASK-054)



| Field | Value |

|---|---|

| ID | ARCH-EXEC-RT-DEV-001 |

| Version | 1.0 |

| Owner | Tech Lead |

| Reviewer | Solution Architect |

| Approver | Architecture Board (delegated via TASK-054) |

| Status | Approved |

| Last Review | 2026-07-24 |

| Next Review | 2026-10-24 |



## Package



`backend/app/modules/execution/`



| Module | Role |

|---|---|

| `runtime_models.py` | `ExecutionRun`, `ExecutionRunTask`, `ExecutionContext`, `ExecutionResult` |

| `runtime.py` | `ExecutionRuntime.prepare`, `build_execution_context` |

| `run_store.py` | `ExecutionRunStore` (in-memory) |

| `models.py` / `planner.py` / `store.py` / `registry.py` | TASK-053 plan foundation (unchanged contract) |



## DI helpers



```text

from app.dependencies.events import get_execution_runtime, get_execution_run_store

```



Runtime is **not** auto-invoked from `WorkflowExecutionProducer` or the event path.



## Prepare flow



1. Obtain an `ExecutionPlan` (planner / plan store / test fixture).

2. Optionally build `ExecutionContext` via `build_execution_context(...)`.

3. Call `ExecutionRuntime.prepare(plan, context=...)`.

4. Inspect `ExecutionRun` / `ExecutionRunStore` — status remains **CREATED**.



## Hard rules for contributors



- Do not invoke `ExecutionRegistry` handlers from runtime code.

- Do not import Complaint / Workflow / Notification into runtime modules.

- Do not add HTTP endpoints, persistence, queues, or retries in this task.

- Keep models frozen (`frozen=True`); metadata via `MappingProxyType`.



## Tests



```bash

cd backend

pytest tests/test_execution_runtime.py tests/test_execution.py -q

```



Docker:



```bash

docker compose exec -T backend pytest tests/test_execution_runtime.py tests/test_execution.py -q

```



## Further reading



- `EXECUTION_RUNTIME_ARCHITECTURE.md`

- `EXECUTION_RUNTIME_GUIDE.md`

- `EXECUTION_ARCHITECTURE.md` / `EXECUTION_GUIDE.md` (plan foundation)


