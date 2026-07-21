# ECMP_ADR_009_Message_Broker_Deferral_v1.0

| Field | Value |
|---|---|
| ID | ADR-009 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Integration Lead / Tech Lead |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2026-10-21 |

- ADR Status: Accepted
- Date: 2026-07-21
- Decision Owners: Solution Architect, Integration Lead
- Related Domains: All (event backbone)

## Context
ADR-001 menetapkan integrasi event-driven; teknologi broker belum dipilih. Sprint-01 hanya punya satu event (EVT-001) tanpa consumer nyata. Memilih broker sekarang = keputusan tanpa data beban.

## Decision
1. **Pemilihan broker DITUNDA secara eksplisit** — bukan open question lagi, melainkan deferral yang diputuskan.
2. Sampai broker dipilih: pola **transactional outbox** adalah mekanisme resmi — event ditulis ke tabel `outbox` dalam transaksi yang sama dengan write bisnis; publisher in-process boleh menguras outbox di DEV.
3. **Trigger evaluasi broker** (mana yang lebih dulu): (a) consumer lintas-service pertama akan dibangun (Notification/KPI), atau (b) gate G2 dimulai. Kandidat dievaluasi saat itu: RabbitMQ, Kafka, cloud pub/sub.
4. Larangan: tidak membangun framework publisher generik (retry backoff, DLQ, abstraksi multi-broker) sebelum broker nyata ada.

## Consequences
- Sprint-01 tetap sesuai ADR-001 (durable emit via outbox) tanpa keputusan prematur.
- Migrasi outbox → broker adalah penambahan consumer/relay, bukan perombakan skema.
