# Execution State Machine Guide (TASK-055)



| Field | Value |

|---|---|

| ID | ARCH-EXEC-SM-GUIDE-001 |

| Version | 1.0 |

| Owner | Solution Architect / Tech Lead |

| Reviewer | Tech Lead |

| Approver | Architecture Board (delegated via TASK-055) |

| Status | Approved |

| Last Review | 2026-07-24 |

| Next Review | 2026-10-24 |



## What this is



A validator for `ExecutionRunStatus` transitions backed by `ExecutionLifecycle`.



## What this is NOT



- Not a worker / executor

- Not handler / registry invocation

- Not persistence / scheduler / retry



## API (conceptual)



| Operation | Behavior |

|---|---|

| `can_transition(from, to)` | `True` / `False` |

| `validate(from, to)` | Returns `ExecutionTransition` or raises `ValueError` |



## Engine usage



```text

result, new_run = engine.transition(run, ExecutionRunStatus.READY)

# result.success → True|False

# on success: new_run is a new immutable snapshot; store.replace if wired

# on failure: new_run is the same instance; status unchanged

```



## Rejection



Invalid transitions yield `ExecutionEngineResult` with:



- `success=False`

- `previous_state` = current

- `new_state` = current (unchanged)

- `reason` = `INVALID_TRANSITION: <from> -> <to>` (unless custom reason provided)



## Rules



1. Only lifecycle-allowed edges succeed.

2. Produce a new frozen `ExecutionRun` via `dataclasses.replace` on success.

3. Never mutate the previous run instance.

4. Never invoke handlers / registry / Notification / externals.


