# Notification Intent Foundation (TASK-048)

| Field | Value |
|---|---|
| ID | ARCH-NOTIF-INTENT-001 |
| Version | 1.0 |
| Owner | Notification PO / Integration Lead |
| Reviewer | Solution Architect / Tech Lead |
| Approver | Architecture Board (delegated via TASK-048) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Purpose

Separate **Notification Domain** (what happened / what to tell) from
**Notification Delivery** (how to send it).

`NotificationIntent` describes **WHAT** should be delivered.
Future transport adapters decide **HOW**.

## What this is

- Immutable `NotificationIntent`
- `NotificationIntentFactory.from_notification(notification)`
- Preferred channel enum (no adapters)
- Priority mapped from `NotificationSeverity`
- Template key + variables + metadata
- In-memory diagnostic store only

## What this is NOT

- Not email / WhatsApp / SMS / Push / WebSocket adapters
- Not a send worker, queue write, or broker publish
- Not a change to `Notification`, Complaint aggregate, ComplaintEvent,
  or EventDispatcher
- Not an HTTP API change

## Principle

```text
NotificationEventHandler
      │
      ▼
NotificationFactory.from_event(event)
      │
      ▼
immutable Notification
      │
      ▼
NotificationIntentFactory.from_notification(notification)
      │
      ▼
immutable NotificationIntent (in memory only)
      │
      └── Future transport adapters (TASK-050+)
```

## Related

Delivery plans are materialized in TASK-049 (`DELIVERY_FOUNDATION.md`) as
`NotificationDelivery` with status `PLANNED` only — still no send.

## NotificationIntent fields

| Field | Description |
|---|---|
| `intent_id` | UUID of the intent |
| `created_at` | UTC timestamp |
| `notification_id` | Link to source Notification |
| `recipient_key` | Diagnostic recipient key (not a mailbox) |
| `preferred_channels` | Ordered channel preferences (enum only) |
| `priority` | Mirrors Notification severity |
| `template_key` | Logical template id (e.g. `complaint.created`) |
| `variables` | Template variables |
| `metadata` | Trace metadata (source event, type, …) |

## Channel enum (no implementation)

`EMAIL` · `WHATSAPP` · `PUSH` · `SMS` · `WEBSOCKET`

Defined as `NotificationIntentChannel` (intent vocabulary). Distinct from
TASK-030 queue `NotificationChannel` API literals so HTTP contracts stay
unchanged.

## Template mapping

| NotificationType | template_key |
|---|---|
| ComplaintCreated | `complaint.created` |
| ComplaintAssigned | `complaint.assigned` |
| ComplaintAccepted | `complaint.accepted` |
| ComplaintInProgress | `complaint.in_progress` |
| ComplaintResolved | `complaint.resolved` |
| ComplaintClosed | `complaint.closed` |
| ComplaintEscalated | `complaint.escalated` |

## Priority mapping

Reuses Notification severity → intent priority (`INFO`…`CRITICAL`).
Escalated notifications remain `CRITICAL`. Preferred channels widen with
priority (still preference only — no send).

## Implementation

- `backend/app/modules/notification/intent_models.py`
- `backend/app/modules/notification/intent_factory.py`
- `backend/app/modules/notification/intent_memory.py`
- Handler wiring: `handler.py` (after Notification build)
- Related: TASK-047 (`EVENT_CONSUMER.md`), TASK-030 (queue/templates)

## Out of scope (STOP)

Transport adapters, provider SDKs, persistence of intents, send workers.
