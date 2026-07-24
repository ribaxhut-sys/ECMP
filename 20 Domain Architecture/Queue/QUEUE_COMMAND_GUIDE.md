# Queue Command Guide (TASK-062)

| Field | Value |
|---|---|
| ID | GUIDE-QUEUE-CMD-001 |
| Version | 1.0 |
| Owner | Tech Lead |
| Reviewer | Solution Architect |
| Approver | Architecture Board (delegated via TASK-062) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Commands

| Command | Effect |
|---|---|
| `CreateQueue` | Create aggregate in **CLOSED** with policy FIFO / PRIORITY_QUEUE |
| `OpenQueue` | Set queue status → **OPEN** |
| `PauseQueue` | Set queue status → **PAUSED** (not from CLOSED) |
| `CloseQueue` | Set queue status → **CLOSED** |
| `IssueTicket` | Issue WAITING ticket (queue must be OPEN) |
| `CallNextTicket` | Select next WAITING → **CALLED** (queue must be OPEN) |
| `CompleteTicket` | CALLED / SERVING → **COMPLETED** |
| `CancelTicket` | WAITING / CALLED / SERVING → **CANCELLED** |

## Rules enforced

- Queue must be **OPEN** before issuing a ticket
- Queue **CLOSED** rejects new tickets
- Queue **PAUSED** rejects calling
- No duplicate ticket numbers within one queue
- Cancelled tickets are not selectable for calling
- Completed tickets cannot return to WAITING

## Package

`backend/app/modules/queue/application/commands/`

## Related

- `QUEUE_APPLICATION_ARCHITECTURE.md`
- `QUEUE_TICKET_LIFECYCLE.md`
