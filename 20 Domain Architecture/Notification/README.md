# Domain Architecture — Notification

| Field | Value |
|---|---|
| ID | DOM-NOTIF-001 |
| Version | 1.0 |
| Owner | Notification PO / Integration Lead |
| Reviewer | Solution Architect |
| Approver | Architecture Board |
| Status | 🟢 Approved (baseline) |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Objective
Notifikasi event-driven dengan template, routing, delivery log, dan retry. Opt-in: hanya event yang dikonfigurasi eksplisit yang memicu notifikasi (BR-NOTIF-01 → delivery BR-004).

## Bounded Context
Konteks Messaging/Delivery: subscribe domain events → match rule/template → resolve recipients dinamis (role/assignment/organisasi, bukan daftar statis — BR-NOTIF-02) → deliver → log.

## In Scope
- Event subscription/routing (configurable, BR-004)
- Templates
- Multi-channel delivery, phase-based (in-app/email dulu; email gateway opsional)
- Delivery logs wajib disimpan (BR-NOTIF-03) + retry saat gagal (BR-NOTIF-04)

## Out of Scope
- Menghasilkan domain event bisnis; menentukan isi/aturan bisnis case

## Key Components
- Event Subscriber (idempotent consumer), Notification Rule engine, Template renderer, Recipient Resolver, Delivery Adapter (in-app/email), Delivery Log + Retry scheduler.

## Key Flows
Event → Match Rule/Template → Resolve Recipients → Deliver → Log → Retry bila gagal (baseline DEC-004: retry maksimal 3x interval 5 menit; setelah max retry, eskalasi via email ke supervisor terkait).

## Data Ownership
Event Type (selaras `../../08 Event Catalog`), Notification Rule, Template, Delivery Log, Recipient = Notification.

## Integrations
- **Events consumed** (per events.yaml): EVT-001 CaseCreated (notify assignee pool/supervisor), EVT-002 CaseAssigned, EVT-003 StatusChanged, EVT-004 SLABreached (eskalasi supervisor/manager), EVT-005 CaseClosed, EVT-007 CaseReopened.
- **Events produced:** tidak ada.
- **Email Gateway (opsional):** integrasi outbound; lihat `../../09 Integration Catalog`.

## NFR Considerations
At-least-once delivery (ADR-001) → dedup wajib di consumer; delivery log memuat kontak penerima (PII) — perhatikan akses.

## Diagram Links
- Source: `../../23 Assets/mermaid/ecmp-context.mmd`
- Export: —

## Open Questions
- Kebijakan retry dan channel fallback eskalasi (BR-NOTIF-04) — **ditutup** baseline DEC-004: 3x interval 5 menit; eskalasi email ke supervisor.
