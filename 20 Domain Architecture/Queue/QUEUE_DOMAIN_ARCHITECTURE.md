# Queue Domain Architecture (TASK-061)

| Field | Value |
|---|---|
| ID | DOM-QUEUE-001 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-061) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Purpose

Introduce **Queue** as a first-class ECMP bounded context.

This milestone creates the **core queue model only** — aggregate root,
ticket, counter, policy, status, and priority.

No REST API. No database. No display. No kiosk. No queue calling.

## Principles

1. Bounded Context — Queue is independent of Complaint / Delivery / Provider.
2. Aggregate Root — `Queue` owns identity + policy + operational status.
3. Immutable tickets — `QueueTicket` is a frozen value object.
4. Clean Architecture — domain model with no infrastructure adapters.
5. Must not modify Complaint / Workflow / Execution* / Delivery* / Transport* /
   Provider* / Dashboard / Notification / KPI.

## Bounded Context

| Concept | Role |
|---|---|
| `Queue` | Aggregate root |
| `QueueTicket` | Immutable ticket issued into a queue |
| `QueueCounter` | Service counter representation |
| `QueuePolicy` | FIFO · PRIORITY_QUEUE |
| `QueueStatus` | OPEN · PAUSED · CLOSED (queue / counter) |
| `QueueTicketStatus` | WAITING · CALLED · SERVING · COMPLETED · CANCELLED · SKIPPED |
| `QueuePriority` | NORMAL · PRIORITY · VIP |

## Pipeline (foundation)

```text
Queue (aggregate)
   ├─ status / policy
   ├─ QueueTicket (by queue_id) — immutable
   └─ QueueCounter — service point

Future (TASK-063+): persistence · API · display · kiosk · notification
```

## Guarantees

- No DB / repository / REST
- No display / kiosk / calling integration
- No mutable shared ticket state
- No scheduling beyond policy enum

## Implementation

- `backend/app/modules/queue/models.py`

## Related

- `QUEUE_MODEL.md`
- `QUEUE_DEVELOPER_GUIDE.md`
- `../../04 Solution Architecture/ECMP_Solution_Architecture_v1.0.md`
