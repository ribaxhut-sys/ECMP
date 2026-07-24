# Execution Engine — Developer Guide (TASK-055)



| Field | Value |

|---|---|

| ID | ARCH-EXEC-ENG-DEV-001 |

| Version | 1.0 |

| Owner | Tech Lead |

| Reviewer | Solution Architect |

| Approver | Architecture Board (delegated via TASK-055) |

| Status | Approved |

| Last Review | 2026-07-24 |

| Next Review | 2026-10-24 |



## Package



| Module | Role |

|---|---|

| `lifecycle.py` | `ExecutionLifecycle`, `ExecutionStateMachine`, `ExecutionTransition` |

| `engine.py` | `ExecutionEngine`, `ExecutionEngineResult` |

| `runtime_models.py` | `ExecutionRunStatus` enum (expanded for lifecycle) |

| `run_store.py` | `replace(run)` for immutable snapshot swap |



**Do not modify** `runtime.py` (`ExecutionRuntime`) for engine work.



## DI



```text

from app.dependencies.events import get_execution_engine, get_execution_run_store

```



Engine is not auto-invoked from the event path.



## Typical flow



1. `ExecutionRuntime.prepare(plan)` → run `CREATED`

2. `engine.transition(run, READY)` → `READY`

3. `engine.transition(run, RUNNING)` → `RUNNING`

4. `engine.transition(run, COMPLETED|FAILED|CANCELLED)` → terminal



## Hard rules



- Transition validation only — no handler execution

- Reject invalid state changes

- Keep models frozen

- No Complaint / Workflow / Notification imports in engine modules

- No HTTP / DB / queue / scheduler / retry



## Tests



```bash

cd backend

pytest tests/test_execution_engine.py tests/test_execution_runtime.py tests/test_execution.py -q

```



Docker:



```bash

docker compose exec -T backend pytest tests/test_execution_engine.py tests/test_execution_runtime.py tests/test_execution.py -q

```



## Further reading



- `EXECUTION_ENGINE_ARCHITECTURE.md`

- `EXECUTION_LIFECYCLE.md`

- `EXECUTION_STATE_MACHINE_GUIDE.md`


