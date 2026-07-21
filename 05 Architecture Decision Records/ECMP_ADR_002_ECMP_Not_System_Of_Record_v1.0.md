# ECMP_ADR_002_ECMP_Not_System_Of_Record_v1.0

| Field | Value |
|---|---|
| ID | ADR-002 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Data Architect, CRM Domain PO |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

- ADR Status: Accepted (Architecture Board, 2026-07-21 — ARB review)
- Date: 2026-07-21
- Decision Owners: Solution Architect, Data Architect
- Related Domains: CRM, Core Platform

## Context
`01 Business Blueprint` (Scope dan bagian 7.2 CRM) menyatakan ECMP menyajikan Customer 360 dari data master yang sudah ada di sistem lain, dan secara eksplisit **Out of Scope**: "Menjadi system of record master pelanggan". Ini konsekuensi arsitektural besar (bagaimana data diakses, di-cache, dan disinkronkan) yang belum pernah diformalkan sebagai keputusan teknis dengan opsi dan trade-off yang eksplisit.

## Decision Drivers
- Menghindari duplikasi ownership data pelanggan yang bisa menyebabkan data pelanggan tidak konsisten antar sistem.
- CRM domain butuh performa baik untuk pencarian dan tampilan profil 360 tanpa selalu memanggil sistem master secara sinkron.
- Ketergantungan pada availability sistem master eksternal harus diminimalkan agar tidak menjadi single point of failure bagi ECMP.

## Options Considered
### Option A â€” Real-time read-through ke Customer Master, tanpa cache lokal
- Pros: Data selalu terbaru, tidak ada risiko data stale, tidak ada duplikasi penyimpanan.
- Cons: ECMP down/lambat total bila Customer Master down; latency tinggi untuk pencarian; ketergantungan penuh pada SLA sistem eksternal.

### Option B â€” Local read-only cache dengan sinkronisasi periodik/event-based, ECMP tetap bukan pemilik data
- Pros: Performa pencarian dan tampilan lebih baik; ECMP tetap bisa beroperasi terbatas saat Customer Master down (data terakhir yang di-cache); jelas batas ownership (cache â‰  SoR).
- Cons: Ada risiko data stale antara sinkronisasi; perlu mekanisme invalidasi/refresh cache dan indikator "last synced" ke user.

## Decision
Menggunakan **Option B â€” local read-only cache** untuk data pelanggan di domain CRM, disinkronkan dari Customer Master melalui integrasi resmi (event atau scheduled pull â€” detail teknis di `09 Integration Catalog`). ECMP tidak pernah melakukan write-back ke Customer Master kecuali melalui integrasi resmi yang eksplisit diizinkan (selaras BR-CRM-01 dan BR-CRM-04).

## Consequences
### Positive
- CRM tetap responsif meski Customer Master lambat/down sementara.
- Batas tanggung jawab data jelas: ECMP hanya konsumen, bukan pemilik â€” memudahkan audit kepatuhan data.
- Selaras dengan Out of Scope yang sudah disepakati stakeholder di Blueprint.

### Negative / Trade-offs
- Perlu UI yang menampilkan "data as of [timestamp]" agar user tidak menganggap data selalu real-time.
- Menambah kebutuhan job/consumer sinkronisasi yang harus dipantau (staleness, failure).
- Perlu kebijakan retensi dan PII untuk cache lokal (lihat `06 Data Dictionary`, `10 Security and Access Standards`).

### Follow-up Actions
- [ ] Update Solution Architecture â€” desain mekanisme sinkronisasi cache (event-driven mengikuti ADR-001 atau scheduled pull)
- [ ] Update API/Event/Integration catalogs â€” kontrak Customer Master read API
- [ ] Communicate to impacted teams â€” CRM, Data/Compliance, Security
