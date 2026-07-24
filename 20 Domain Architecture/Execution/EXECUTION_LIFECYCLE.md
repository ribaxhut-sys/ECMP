# Execution Lifecycle (TASK-055)



| Field | Value |

|---|---|

| ID | ARCH-EXEC-LIFE-001 |

| Version | 1.0 |

| Owner | Solution Architect |

| Reviewer | Tech Lead |

| Approver | Architecture Board (delegated via TASK-055) |

| Status | Approved |

| Last Review | 2026-07-24 |

| Next Review | 2026-10-24 |



## Purpose



Central definition of allowed `ExecutionRun` status transitions.

**No business logic.** Validation only.



## States



| State | Meaning (Milestone-1) |

|---|---|

| `CREATED` | Prepared by `ExecutionRuntime` |

| `READY` | Armed for future execution |

| `RUNNING` | Marked running (no handlers invoked yet) |

| `COMPLETED` | Terminal success |

| `FAILED` | Terminal failure |

| `CANCELLED` | Terminal cancel |



## Allowed transitions



```text

CREATED  → READY

READY    → RUNNING

READY    → CANCELLED

RUNNING  → COMPLETED

RUNNING  → FAILED

RUNNING  → CANCELLED

```



All other edges are **invalid** and must be rejected.



## Terminal states



`COMPLETED`, `FAILED`, `CANCELLED` have no outbound transitions in TASK-055.



## Ownership



`ExecutionLifecycle` owns the allowed edge set.

`ExecutionStateMachine` / `ExecutionEngine` consume it; they do not invent edges.


