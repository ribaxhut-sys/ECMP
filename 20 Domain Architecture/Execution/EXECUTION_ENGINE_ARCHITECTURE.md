# Execution Engine Architecture (TASK-055)



| Field | Value |

|---|---|

| ID | ARCH-EXEC-ENG-001 |

| Version | 1.0 |

| Owner | Solution Architect |

| Reviewer | Tech Lead |

| Approver | Architecture Board (delegated via TASK-055) |

| Status | Approved |

| Last Review | 2026-07-24 |

| Next Review | 2026-10-24 |



## Purpose



Introduce a **generic Execution Engine** that manages `ExecutionRun` lifecycle

**state transitions only**. No business handler execution, no sends, no externals.



## Principles



1. Engine is shared infrastructure (Clean Architecture / DDD / OCP).

2. Immutable domain models — transitions produce a **new** `ExecutionRun`.

3. Open/Closed: add transitions via `ExecutionLifecycle`; engine stays stable.

4. Dependency Injection for store + state machine.

5. Must not know / call Complaint, Workflow, Notification, Assignment, AI, HTTP, Queue.



## Pipeline



```text

ExecutionRuntime.prepare  →  ExecutionRun (CREATED)     ← TASK-054 (unchanged)

                │

                ▼

        ExecutionEngine.transition(to_state)

                │

                ├─ ExecutionStateMachine.validate

                │       └─ ExecutionLifecycle (allowed edges)

                ├─ replace(run, status=new)  → new immutable run

                ├─ ExecutionRunStore.replace (optional)

                └─ ExecutionEngineResult

```



## Components



| Component | Responsibility |

|---|---|

| `ExecutionLifecycle` | Catalog of allowed transitions (no business logic) |

| `ExecutionStateMachine` | Validate / reject transitions |

| `ExecutionTransition` | Immutable from→to descriptor |

| `ExecutionEngine` | Apply validated status change; return result |

| `ExecutionEngineResult` | `success`, `previous_state`, `new_state`, `reason` |



## Guarantees (TASK-055)



- Transition validation only — no real execution

- No registry / handler invocation

- No Notification / Assignment / Workflow / AI / HTTP / Queue

- No database / scheduler / retry

- No HTTP API

- `ExecutionRuntime` code path unchanged



## Implementation



- `backend/app/modules/execution/lifecycle.py`

- `backend/app/modules/execution/engine.py`

- DI: `get_execution_engine()` in `backend/app/dependencies/events.py`



## Related



- `EXECUTION_LIFECYCLE.md`

- `EXECUTION_STATE_MACHINE_GUIDE.md`

- `EXECUTION_ENGINE_DEVELOPER_GUIDE.md`

- `EXECUTION_RUNTIME_ARCHITECTURE.md`

- `../../04 Solution Architecture/ECMP_Solution_Architecture_v1.0.md`


