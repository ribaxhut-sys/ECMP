# Domain Architecture — Notification

| Field | Value |
|---|---|
| ID | DOM-NOTIF-001 |
| Version | 1.4 |
| Owner | Notification PO / Integration Lead |
| Reviewer | Solution Architect |
| Approver | Architecture Board |
| Status | 🟢 Approved (baseline + TASK-047/048/049 + CAPABILITY-009) |
| Last Review | 2026-07-25 |
| Next Review | 2027-01-21 |

## Objective
Notifikasi event-driven dengan template, routing, delivery log, dan retry. Opt-in: hanya event yang dikonfigurasi eksplisit yang memicu notifikasi (BR-NOTIF-01 → delivery BR-004).

**TASK-047 (Notification Domain Foundation):** first in-process consumer of
`EventDispatcher`. Builds immutable `Notification` objects from Complaint
lifecycle events. **No channel delivery** in this task.

**CAPABILITY-009:** Persisted notification requests (`notification_queue`) with
lifecycle Pending → Sending (`PROCESSING`) → Sent / Failed / Cancelled,
stub `NotificationProvider`, REST retry/process (API-356/357), and
`NotificationPersistenceHandler` (Complaint unchanged). Real SMTP / WhatsApp /
SMS / Push / webhook remain out of scope.

## Bounded Context
Konteks Messaging/Delivery: subscribe domain events → match rule/template → resolve recipients dinamis (role/assignment/organisasi, bukan daftar statis — BR-NOTIF-02) → deliver → log.

TASK-047 scope is narrower: **consume → build Notification → hold in memory**.
Transport adapters remain future work.

## In Scope
- Event subscription/routing (configurable, BR-004)
- Templates (TASK-030 queue/template foundation)
- Multi-channel delivery, phase-based (in-app/email dulu; email gateway opsional) — **deferred past TASK-047**
- Delivery logs wajib disimpan (BR-NOTIF-03) + retry saat gagal (BR-NOTIF-04) — **deferred past TASK-047**
- **TASK-047:** `Notification` + `NotificationFactory` + `NotificationEventHandler` (in-memory)
- **TASK-048:** `NotificationIntent` + `NotificationIntentFactory` (preferred channels enum only)
- **TASK-049:** `NotificationDelivery` + `NotificationDeliveryFactory` (PLANNED plans only; no send)

## Out of Scope
- Menghasilkan domain event bisnis; menentukan isi/aturan bisnis case
- TASK-047: email / WhatsApp / SMS / Push / WebSocket delivery
- TASK-047: DB persistence of built `Notification` objects
- TASK-048: transport adapters / send workers / intent persistence
- TASK-049: sending, queue, scheduler, retry, statuses beyond PLANNED

## Key Components
- Event Subscriber (idempotent consumer), Notification Rule engine, Template renderer, Recipient Resolver, Delivery Adapter (in-app/email), Delivery Log + Retry scheduler.
- **TASK-047 runtime:** `NotificationEventHandler` → `NotificationFactory` → immutable `Notification` (+ `InMemoryNotificationStore` for diagnostics).
- **TASK-048 runtime:** `Notification` → `NotificationIntentFactory` → immutable `NotificationIntent` (preferred channels enum only; no transport).
- **TASK-049 runtime:** `NotificationIntent` → `NotificationDeliveryFactory` → immutable `NotificationDelivery` plans (`PLANNED` only; no send/queue).

## Key Flows
**Target (full domain):** Event → Match Rule/Template → Resolve Recipients → Deliver → Log → Retry bila gagal (baseline DEC-004: retry maksimal 3x interval 5 menit; setelah max retry, eskalasi via email ke supervisor terkait).

**TASK-047/048/049 (implemented):** ComplaintEvent → EventDispatcher → NotificationEventHandler → Notification → NotificationIntent → NotificationDelivery (PLANNED, in-memory). No transport send.

## Data Ownership
Event Type (selaras `../../08 Event Catalog`), Notification Rule, Template, Delivery Log, Recipient = Notification.

TASK-047 `Notification` objects are ephemeral in-process diagnostics only.

## Integrations
- **Events consumed** (per events.yaml): EVT-001 CaseCreated (notify assignee pool/supervisor), EVT-002 CaseAssigned, EVT-003 StatusChanged, EVT-004 SLABreached (eskalasi supervisor/manager), EVT-005 CaseClosed, EVT-007 CaseReopened.
- **TASK-047 also consumes in-process:** EVT-009…EVT-015 (`ComplaintCreated` … `ComplaintEscalated`) via `EventDispatcher` (not broker).
- **Events produced:** tidak ada.
- **Email Gateway (opsional):** integrasi outbound; lihat `../../09 Integration Catalog` — not used in TASK-047.

## NFR Considerations
At-least-once delivery (ADR-001) → dedup wajib di consumer; delivery log memuat kontak penerima (PII) — perhatikan akses.
TASK-047: synchronous in-process only; handler failure isolated by dispatcher.

## Diagram Links
- Source: `../../23 Assets/mermaid/ecmp-context.mmd`
- Export: —

## Detailed Docs
- `EVENT_CONSUMER.md` (ARCH-NOTIF-CONSUMER-001) — Notification Event Consumer Guide (TASK-047)
- `NOTIFICATION_INTENT.md` (ARCH-NOTIF-INTENT-001) — Notification Intent Foundation (TASK-048)
- `DELIVERY_FOUNDATION.md` (ARCH-NOTIF-DELIVERY-001) — Notification Delivery Foundation (TASK-049)

## Open Questions
- Kebijakan retry dan channel fallback eskalasi (BR-NOTIF-04) — **ditutup** baseline DEC-004: 3x interval 5 menit; eskalasi email ke supervisor.
