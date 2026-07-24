# Queue Query Guide (TASK-062)

| Field | Value |
|---|---|
| ID | GUIDE-QUEUE-QRY-001 |
| Version | 1.0 |
| Owner | Tech Lead |
| Reviewer | Solution Architect |
| Approver | Architecture Board (delegated via TASK-062) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Queries

| Query | Returns |
|---|---|
| `GetQueue` | `QueueDto` for `queue_id` |
| `GetQueueTickets` | All `QueueTicketDto` for the queue |
| `GetWaitingTickets` | Tickets with status **WAITING** only |

## Notes

- Queries read immutable DTOs — no side effects
- Missing queue raises `QueueApplicationError` (`QUEUE_NOT_FOUND`)
- No pagination / filtering beyond waiting status (foundation)

## Package

`backend/app/modules/queue/application/queries/`

## Related

- `QUEUE_APPLICATION_ARCHITECTURE.md`
- `QUEUE_APPLICATION_DEVELOPER_GUIDE.md`
