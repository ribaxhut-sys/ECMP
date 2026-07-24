# 08 Event Catalog


| Field | Value |
|---|---|
| ID | EVT-000 |
| Version | 0.2 |
| Owner | Integration Lead |
| Reviewer | Domain Tech Leads |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Katalog domain event ECMP untuk orkestrasi antar modul (notification, KPI, audit, integrations).

## Owner
- Document Owner: Solution Architect / Integration Lead
- Reviewers: Domain Tech Leads, Ops

## Status
Approved — single Source of Truth ditetapkan (DEC-001 governance; ARB 2026-07-21)

## Source of Truth
- [`events/events.yaml`](./events/events.yaml) — **satu-satunya katalog normatif**: payload (camelCase), producer, consumers, delivery guarantee, dan aturan idempotency per event.
- `ECMP_Event_Catalog_v1.0.yaml` (duplikat draft, payload snake_case) **dihapus 2026-07-21** untuk mengeliminasi dual-SoT. Konten consumers/idempotency sudah digabung ke `events/events.yaml`.
- `EVENT_CATALOG.generated.md` di-generate dari SoT via `python tools/eos.py --all` — jangan diedit manual.
- Setiap event kini memiliki field `status:` lifecycle per event (`Implemented` = sudah di-emit kode berjalan; `Planned` = disetujui, belum diproduksi; `Proposed` = menunggu persetujuan).

## Minimum Event Set (from Blueprint)
- [x] CaseCreated
- [x] CaseAssigned
- [x] StatusChanged
- [x] SLABreached
- [x] CaseClosed
- [x] ConfigChanged
- [x] CaseReopened — EVT-007, status Proposed (dibutuhkan BR-ECMF-07; tambahan di luar set minimal Blueprint)
- [x] Complaint Event Foundation (TASK-045) — EVT-009…EVT-015 (`ComplaintCreated` … `ComplaintEscalated`); in-memory factory only, no bus
- [x] In-Process Event Dispatcher (TASK-046) — same-process `EventDispatcher` / `EventHandler`; not a bus/broker/store
- [x] Notification Domain Foundation (TASK-047) — first dispatcher consumer; builds in-memory `Notification`; no channel delivery
- [x] Notification Intent Foundation (TASK-048) — `NotificationIntent` (what to deliver); channel enum only; no transport adapters
- [x] Notification Delivery Foundation (TASK-049) — `NotificationDelivery` (PLANNED plans per channel); no send/queue/retry
- [x] Dashboard Projection Foundation (TASK-050) — in-memory `DashboardProjection` from Complaint events; no HTTP projection API yet
- [x] KPI Projection Foundation (TASK-051) — in-memory `KpiProjection` from Complaint events; no HTTP projection API yet

## Template Fields (per event)
- Event Name
- Domain Producer
- Trigger
- Payload schema
- Consumers
- Delivery guarantee (at-least-once, etc.)
- Ordering / idempotency notes
- Version
- Status

## Naming
`ECMP_Event_<EventName>_vX.Y.json|md|yaml`

## Related
- `../07 API Catalog`
- `../09 Integration Catalog`
- `../04 Solution Architecture`
