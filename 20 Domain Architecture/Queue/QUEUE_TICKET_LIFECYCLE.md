# Queue Ticket Lifecycle (TASK-062)

| Field | Value |
|---|---|
| ID | GUIDE-QUEUE-LIFE-001 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-062) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Statuses (`QueueTicketStatus`)

WAITING · CALLED · SERVING · COMPLETED · CANCELLED · SKIPPED

## Happy path

```text
IssueTicket → WAITING
     │
     ▼
CallNextTicket → CALLED
     │
     ├──────────────► CompleteTicket → COMPLETED
     │
     └─ (optional future) SERVING → CompleteTicket → COMPLETED
```

## Alternate paths

```text
WAITING ──CancelTicket──► CANCELLED
CALLED  ──CancelTicket──► CANCELLED
SERVING ──CancelTicket──► CANCELLED

WAITING / CALLED ──skip (domain)──► SKIPPED
CALLED / SERVING ──recall (domain)──► same status (re-announce)
```

## Forbidden transitions

| From | To | Rule |
|---|---|---|
| WAITING | COMPLETED | Must call first (no direct complete) |
| COMPLETED | WAITING | Completed ticket cannot return to WAITING |
| CANCELLED | CALLED | Cancelled ticket cannot be called |
| COMPLETED | CALLED | Terminal |
| SKIPPED | CALLED | Terminal |

## Selection

| Policy | Order |
|---|---|
| `FIFO` | Earliest `created_at` among WAITING |
| `PRIORITY_QUEUE` | VIP → PRIORITY → NORMAL, then FIFO within rank |

## Related

- `QUEUE_APPLICATION_ARCHITECTURE.md`
- `QUEUE_COMMAND_GUIDE.md`
