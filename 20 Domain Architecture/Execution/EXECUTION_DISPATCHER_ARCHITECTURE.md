# Execution Dispatcher Architecture (TASK-056)



| Field | Value |

|---|---|

| ID | ARCH-EXEC-DISP-001 |

| Version | 1.0 |

| Owner | Solution Architect |

| Reviewer | Tech Lead |

| Approver | Architecture Board (delegated via TASK-056) |

| Status | Approved |

| Last Review | 2026-07-24 |

| Next Review | 2026-10-24 |



## Purpose



Introduce a **generic dispatch planning layer** that connects `ExecutionRun`

tasks to `ExecutionRegistry` via immutable `DispatchRequest` objects.

Dispatcher validates readiness and **never invokes handlers**.



## Principles



1. Dispatch planning ≠ execution.

2. Registry is consulted for **availability** only (`has` / `get` catalog).

3. Immutable models; Open/Closed for future policies.

4. Must not call Complaint / Workflow / Notification / Assignment / AI / HTTP.

5. Must not modify ExecutionRuntime / ExecutionEngine / ExecutionLifecycle.



## Pipeline



```text

ExecutionRun (READY|RUNNING) + ExecutionTask + ExecutionRegistry

                    │

                    ▼

            DispatchValidator

              ├─ task on run?

              ├─ task_type present?

              ├─ handler registered?

              └─ status READY|RUNNING?

                    │

                    ▼

            ExecutionDispatcher

              ├─ build DispatchRequest

              └─ return DispatchResult

                    │

                    ▼

         Future executor (TASK-057+) — NOT in scope

```



## Components



| Component | Responsibility |

|---|---|

| `DispatchRequest` | Immutable planned unit |

| `DispatchResult` | success / handler_registered / reason |

| `DispatchValidator` | Readiness checks (no invoke) |

| `DispatchPolicy` | SEQUENTIAL only (foundation) |

| `ExecutionDispatcher` | Validate + build request |



## Guarantees



- No handler / registry execution

- No Notification / Assignment / Workflow / AI / HTTP

- No DB / queue / scheduler / retry

- No HTTP API



## Implementation



- `backend/app/modules/execution/dispatch_models.py`

- `backend/app/modules/execution/dispatch_validator.py`

- `backend/app/modules/execution/dispatcher.py`

- DI: `get_execution_dispatcher()`



## Related



- `EXECUTION_DISPATCH_POLICY_GUIDE.md`

- `EXECUTION_DISPATCHER_DEVELOPER_GUIDE.md`

- `EXECUTION_ENGINE_ARCHITECTURE.md`

- `../../04 Solution Architecture/ECMP_Solution_Architecture_v1.0.md`


