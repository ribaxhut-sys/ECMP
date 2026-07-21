# ECMP_ADR_003_Configuration_First_Principle_v1.0

| Field | Value |
|---|---|
| ID | ADR-003 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Leads, Administration Domain PO |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

- ADR Status: Accepted (Architecture Board, 2026-07-21 — ARB review)
- Date: 2026-07-21
- Decision Owners: Solution Architect, Administration Domain PO
- Related Domains: Administration, ECMF, KPI & Performance, Core Platform

## Context
Blueprint bagian 7.7 (Administration) menetapkan tujuan "mengelola parameter, referensi, dan konfigurasi aplikasi agar proses bisnis dapat diubah tanpa perubahan kode sepanjang memungkinkan", dan Business Rules (`02`) menandai banyak rule sebagai *Configuration* (workflow transition, SLA calculation, role-permission). Prinsip "configuration-first" ini disebut berulang tapi belum ada keputusan teknis tentang apa yang wajib configurable vs boleh hardcoded, dan bagaimana perubahan konfigurasi dikendalikan agar tidak menjadi risiko (perubahan tanpa approval, tanpa audit).

## Decision Drivers
- Perubahan proses bisnis (kategori, prioritas, SLA, workflow status) terjadi lebih sering daripada rilis kode â€” biaya development untuk tiap perubahan kecil terlalu tinggi bila hardcoded.
- Konfigurasi yang terlalu bebas (tanpa versioning/approval) berisiko terhadap konsistensi historis transaksi (BR-ADM-03, BR-ADM-04).
- Tim development butuh batas jelas: mana yang harus dibuat sebagai config engine, mana yang cukup sebagai code karena jarang berubah dan berisiko tinggi bila salah konfigurasi (mis. aturan keamanan inti).

## Options Considered
### Option A â€” Semua business rule dibuat configurable melalui rule engine generik
- Pros: Maksimal fleksibilitas, minim rilis kode untuk perubahan bisnis.
- Cons: Kompleksitas engineering tinggi di awal, risiko konfigurasi yang salah lebih besar dan lebih sulit diverifikasi (testing kombinatorial), waktu pengembangan awal lebih lama.

### Option B â€” Configuration-first untuk area yang sering berubah (kategori, prioritas, SLA, workflow status, role-permission, notification rule); hardcoded untuk aturan struktural/keamanan inti (autentikasi wajib, audit trail immutable, closure harus punya resolusi)
- Pros: Fleksibilitas di area yang benar-benar butuh, tanpa mengorbankan keamanan pada aturan yang seharusnya tidak bisa dinonaktifkan lewat konfigurasi; sejalan dengan klasifikasi Config/Hardcoded yang sudah dipakai di `02 Business Rules`.
- Cons: Perlu disiplin arsitektur untuk konsisten memisahkan dua kategori ini; ada risiko kategori bergeser seiring waktu dan perlu direview ulang.

## Decision
Mengadopsi **Option B**: rule yang tergolong *Configuration* pada `02 Business Rules` (workflow transition, SLA formula, kategori/prioritas, role-permission mapping, notification rule) dibangun di atas config engine dengan versioning dan effective date (BR-ADM-03). Rule yang tergolong *Hardcoded* (autentikasi wajib, audit trail immutable, dashboard read-only, resolusi wajib saat closure) tidak boleh dijadikan opsi konfigurasi yang bisa dimatikan.

## Consequences
### Positive
- Perubahan proses bisnis rutin (kategori baru, SLA baru) tidak membutuhkan deployment kode.
- Aturan keamanan/integritas inti tetap terlindungi dari kesalahan konfigurasi operasional.
- Klasifikasi yang sudah ada di `02 Business Rules` langsung actionable untuk desain data model config di `04 Solution Architecture`.

### Negative / Trade-offs
- Perlu dibangun UI/tooling admin untuk mengelola konfigurasi (bagian dari domain Administration) sebelum manfaat penuh terasa.
- Perubahan kritikal tetap memerlukan approval (BR-ADM-01) â€” ada latensi proses, bukan instan seperti hardcode ubah langsung oleh developer.

### Follow-up Actions
- [ ] Update Solution Architecture â€” desain config engine, versioning, dan effective-date mechanism
- [ ] Update API/Event/Integration catalogs â€” event `ConfigChanged` perlu payload yang mencatat nilai lama/baru
- [ ] Communicate to impacted teams â€” Administration, ECMF, KPI, Core Platform
