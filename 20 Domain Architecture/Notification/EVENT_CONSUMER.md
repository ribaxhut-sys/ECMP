# Notification Event Consumer (TASK-047)

| Field | Value |
|---|---|
| ID | ARCH-NOTIF-CONSUMER-001 |
| Version | 1.0 |
| Owner | Notification PO / Integration Lead |
| Reviewer | Solution Architect / Tech Lead |
| Approver | Architecture Board (delegated via TASK-047) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Purpose

Notification is the **first consumer** of the in-process `EventDispatcher`
(TASK-046). It consumes Complaint lifecycle events and **builds** immutable
`Notification` objects.

This foundation is **transport-independent**.

## What this is

- `Notification` immutable domain object
- `NotificationFactory.from_event(event)`
- `NotificationEventHandler` implementing `EventHandler`
- In-memory diagnostic store only
- Registration onto `EventDispatcher` from composition root

## What this is NOT

- Not email / WhatsApp / SMS / Push / WebSocket delivery
- Not a broker / queue / database persistence for these objects
- Not a change to Complaint aggregate, ComplaintEvent, or EventDispatcher
- Not an HTTP API change

## Principle

```text
NotificationEventHandler.handle(event)
      │
      ▼
NotificationFactory.from_event(event)
      │
      ▼
immutable Notification (in memory only)
      │
      ▼
NotificationIntentFactory.from_notification(notification)  ← TASK-048
      │
      ▼
immutable NotificationIntent (in memory only)
      │
      ▼
NotificationDeliveryFactory.from_intent(intent)  ← TASK-049
      │
      ▼
immutable NotificationDelivery × N (PLANNED only)
```

## Supported events

| ComplaintEvent | NotificationType |
|---|---|
| ComplaintCreated | ComplaintCreated |
| ComplaintAssigned | ComplaintAssigned |
| ComplaintAccepted | ComplaintAccepted |
| ComplaintInProgress | ComplaintInProgress |
| ComplaintResolved | ComplaintResolved |
| ComplaintClosed | ComplaintClosed |
| ComplaintEscalated | ComplaintEscalated |

## Registration rule

`ComplaintService` must **not** know Notification exists.

Composition root (`app/dependencies/events.py` + routers) obtains a shared
`EventDispatcher` and calls `register_notification_handler(...)`.

## Related

- Domain: `README.md` (DOM-NOTIF-001)
- Dispatcher: `../ECMF/EVENT_DISPATCHER.md`
- Events: `../ECMF/COMPLAINT_EVENTS.md`
- Module: `backend/app/modules/notification/` (`event_models`, `factory`, `handler`, `memory`, `registration`)
