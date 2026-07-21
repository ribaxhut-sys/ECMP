# ECMP_ADR_001_Event_Driven_Domain_Integration_v1.0

| Field | Value |
|---|---|
| ID | ADR-001 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Leads, Security Architect |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

- ADR Status: Accepted (Architecture Board, 2026-07-21 — ARB review)
- Date: 2026-07-21
- Decision Owners: Solution Architect, Integration Lead
- Related Domains: Core Platform, ECMF, KPI & Performance, Dashboard & Analytics, Notification

## Context
`01 Business Blueprint` bagian 8 (Integrasi Antar Modul) sudah mendaftar event minimal yang harus mengalir antar domain (CaseCreated, CaseAssigned, StatusChanged, SLABreached, CaseClosed, ConfigChanged), dan menyatakan modul KPI, Dashboard, dan Notification "mengonsumsi data operasional" dari ECMF secara asinkron. Keputusan pola integrasi (event-driven vs synchronous request/response) belum diformalkan sebagai ADR meski sudah menjadi asumsi implisit di seluruh domain architecture.

## Decision Drivers
- ECMF adalah sumber kebenaran operasional bagi KPI, Dashboard, dan Notification â€” ketiganya tidak boleh memperlambat transaksi utama ECMF.
- SLA breach harus terdeteksi mendekati real-time untuk keperluan notifikasi dan eskalasi.
- Domain-domain harus bisa berkembang independen (deploy terpisah) tanpa saling mengunci pada skema API sinkron.

## Options Considered
### Option A â€” Synchronous REST antar domain
- Pros: Sederhana untuk diimplementasi, mudah di-debug, konsisten data langsung terlihat.
- Cons: ECMF menjadi bottleneck karena harus menunggu respons KPI/Dashboard/Notification; kegagalan salah satu consumer bisa memblok transaksi utama; sulit scale independen.

### Option B â€” Event-driven melalui message broker (asynchronous, at-least-once)
- Pros: ECMF tidak terkunci pada availability consumer lain; domain lain bisa consume ulang (replay) untuk audit/rekonsiliasi; selaras dengan daftar event minimal yang sudah ada di Blueprint.
- Cons: Perlu penanganan idempotency dan eventual consistency; menambah komponen infrastruktur (broker) yang perlu dikelola dan diawasi.

## Decision
Menggunakan **pola event-driven asynchronous** untuk integrasi antar domain, dengan ECMF (dan domain lain yang relevan) mempublikasikan domain event ke message broker; KPI, Dashboard, Notification, dan Core Platform (audit) berlangganan sebagai consumer independen. Detail teknologi broker (mis. Kafka/RabbitMQ) belum diputuskan â€” dicatat sebagai follow-up di `04 Solution Architecture`.

## Consequences
### Positive
- ECMF tetap responsif terhadap user meski KPI/Dashboard/Notification sedang down atau lambat.
- Domain baru dapat berlangganan event yang sama tanpa mengubah ECMF.
- Selaras dengan event minimal yang sudah didefinisikan di Blueprint â€” tidak perlu redesign scope.

### Negative / Trade-offs
- Dashboard dan KPI akan menampilkan data dengan lag (eventual consistency) â€” perlu ditandai "as of" sesuai BR-DASH-02.
- Perlu strategi idempotency/dedup di setiap consumer karena delivery guarantee minimal at-least-once.
- Menambah kompleksitas operasional: monitoring broker, dead-letter queue, replay tooling.

### Follow-up Actions
- [ ] Update Solution Architecture â€” tentukan teknologi broker dan pola delivery guarantee
- [ ] Update API/Event/Integration catalogs â€” formalkan skema payload tiap event (lihat `08 Event Catalog`)
- [ ] Communicate to impacted teams â€” ECMF, KPI, Dashboard, Notification, Core Platform (audit)
