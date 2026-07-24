# Dispatch Policy Guide (TASK-056)



| Field | Value |

|---|---|

| ID | ARCH-EXEC-DISP-POL-001 |

| Version | 1.0 |

| Owner | Solution Architect / Tech Lead |

| Reviewer | Tech Lead |

| Approver | Architecture Board (delegated via TASK-056) |

| Status | Approved |

| Last Review | 2026-07-24 |

| Next Review | 2026-10-24 |



## Purpose



Define how dispatch requests are **planned** (not executed).



## Supported policy (Milestone-1)



| Policy | Behavior |

|---|---|

| `SEQUENTIAL` | Plan tasks in ascending `order` (then `task_type`, `task_id`). No parallel planning batches. |



Any other policy is **rejected** at dispatcher construction.



## Sequential planning



```text

dispatch_sequential(run, tasks)

  → sort by (order, task_type, task_id)

  → dispatch() each task one-by-one

  → list[(DispatchRequest|None, DispatchResult)]

```



No worker threads, no fan-out, no queue writes.



## Out of scope



- Parallel / concurrent dispatch

- Priority / weighted policies

- Retry / backoff policies

- Handler invocation


