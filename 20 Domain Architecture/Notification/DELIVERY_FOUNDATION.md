# Notification Delivery Foundation (TASK-049)

| Field | Value |
|---|---|
| ID | ARCH-NOTIF-DELIVERY-001 |
| Version | 1.0 |
| Owner | Notification PO / Integration Lead |
| Reviewer | Solution Architect / Tech Lead |
| Approver | Architecture Board (delegated via TASK-049) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Purpose

Introduce `NotificationDelivery` — one **planned** executable delivery action
derived from a `NotificationIntent`.

Delivery is **not** transport, **not** sending, and **not** a queue.

## What this is

- Immutable `NotificationDelivery`
- `NotificationDeliveryFactory.from_intent(intent)`
- Status enum with **PLANNED** only
- Channel reused from `NotificationIntentChannel`
- In-memory diagnostic store only

## What this is NOT

- Not email / WhatsApp / SMS / Push / WebSocket adapters
- Not a send worker, broker publish, scheduler, or retry engine
- Not a change to Notification, NotificationIntent, ComplaintEvent,
  or EventDispatcher
- Not an HTTP API change

## Principle

```text
NotificationEventHandler
      │
      ▼
Notification
      │
      ▼
NotificationIntent
      │
      ▼
NotificationDeliveryFactory.from_intent(intent)
      │
      ▼
NotificationDelivery × N  (one PLANNED plan per preferred channel)
      │
      └── Future transport / send (TASK-050+)
```

## NotificationDelivery fields

| Field | Description |
|---|---|
| `delivery_id` | UUID of the delivery plan |
| `created_at` | UTC timestamp |
| `intent_id` | Link to source NotificationIntent |
| `channel` | Single `NotificationIntentChannel` |
| `recipient_key` | Diagnostic recipient key |
| `priority` | Copied from intent priority |
| `template_key` | Copied from intent template key |
| `variables` | Copied template variables |
| `status` | Always `PLANNED` in TASK-049 |
| `metadata` | Trace metadata (intent/notification/channel) |

## Status enum

`PLANNED` only.

No `SENT` / `FAILED` / `RETRY` in this task.

## Channel mapping

`from_intent` expands `intent.preferred_channels` into **one delivery per
channel**, preserving order. Channel vocabulary is reused
(`EMAIL` · `WHATSAPP` · `PUSH` · `SMS` · `WEBSOCKET`).

## Implementation

- `backend/app/modules/notification/delivery_models.py`
- `backend/app/modules/notification/delivery_factory.py`
- `backend/app/modules/notification/delivery_memory.py`
- Handler wiring after Intent build
- Related: TASK-047, TASK-048

## Out of scope (STOP)

Transport adapters, sending, queue writes, schedulers, retries, status
transitions beyond PLANNED.
