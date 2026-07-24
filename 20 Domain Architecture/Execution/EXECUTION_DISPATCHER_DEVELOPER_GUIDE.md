# Execution Dispatcher — Developer Guide (TASK-056)



| Field | Value |

|---|---|

| ID | ARCH-EXEC-DISP-DEV-001 |

| Version | 1.0 |

| Owner | Tech Lead |

| Reviewer | Solution Architect |

| Approver | Architecture Board (delegated via TASK-056) |

| Status | Approved |

| Last Review | 2026-07-24 |

| Next Review | 2026-10-24 |



## Package



| Module | Role |

|---|---|

| `dispatch_models.py` | `DispatchRequest`, `DispatchResult`, `DispatchPolicy` |

| `dispatch_validator.py` | `DispatchValidator` |

| `dispatcher.py` | `ExecutionDispatcher` |



Do **not** modify `runtime.py`, `engine.py`, or `lifecycle.py` for dispatcher work.



## DI



```text

from app.dependencies.events import get_execution_dispatcher, get_execution_registry

```



Not auto-invoked from the event path.



## Typical flow



1. Runtime prepares `ExecutionRun` (CREATED).

2. Engine transitions to READY / RUNNING.

3. Dispatcher.`dispatch(run, plan_task)` → `(DispatchRequest|None, DispatchResult)`.

4. Future executor consumes requests (TASK-057+) — **not here**.



## Validation failures



| Reason prefix | Meaning |

|---|---|

| `INVALID_STATE` | Run not READY/RUNNING |

| `TASK_NOT_FOUND` | Plan task not linked on run |

| `UNKNOWN_TASK_TYPE` | Empty task_type |

| `HANDLER_NOT_REGISTERED` | Registry has no handler |



## Hard rules



- Never call `registry` handlers

- Reject unknown / unregistered task types

- Keep `DispatchRequest` frozen

- No HTTP / DB / queue / scheduler / retry



## Tests



```bash

cd backend

pytest tests/test_execution_dispatcher.py tests/test_execution_engine.py tests/test_execution_runtime.py tests/test_execution.py -q

```



Docker:



```bash

docker compose exec -T backend pytest tests/test_execution_dispatcher.py tests/test_execution_engine.py tests/test_execution_runtime.py tests/test_execution.py -q

```


