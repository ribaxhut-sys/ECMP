# Queue Migration Guide (TASK-063)

| Field | Value |
|---|---|
| ID | GUIDE-QUEUE-MIG-001 |
| Version | 1.0 |
| Owner | Tech Lead |
| Reviewer | Solution Architect |
| Approver | Architecture Board (delegated via TASK-063) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Revision

| Field | Value |
|---|---|
| Revision | `0027_queue_persistence` |
| Down revision | `0026_complaint_source_target` |
| Path | `backend/alembic/versions/0027_queue_persistence.py` |

## Creates

1. `queues`
2. `queue_tickets` (FK → `queues.queue_id`, unique ticket_number per queue)
3. `queue_counters` (FK → `queues.queue_id`)

## Rules

- Migration only — **no seed data**
- Use Alembic `op.create_table` / indexes / FKs (parameterized)
- Downgrade drops counters → tickets → queues

## Apply

```bash
cd backend
alembic upgrade head
```

## Verify

```bash
alembic current
# expect: 0027_queue_persistence
```
