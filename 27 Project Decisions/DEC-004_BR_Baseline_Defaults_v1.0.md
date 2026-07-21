# Decision Record — Business Rule Baseline Defaults (Penutupan [TBD])

| Field | Value |
|---|---|
| ID | DEC-004 |
| Version | 1.0 |
| Owner | BA Lead |
| Reviewer | Domain Product Owners / Operations / Security Officer |
| Approver | Business Owner |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

- Type: Project Decision (non-ADR)
- Status: Accepted
- Date: 2026-07-21
- Owner: BA Lead
- Participants: Architecture Review Board, Domain POs, Operations, Security Officer

## Context
Katalog enterprise `02 Business Rules/ECMP_Business_Rules_v1.0.md` (BR-CAT-001) menyimpan 10 butir `[TBD]` yang memblokir status Approved dan membuat FRD lanjutan (FRD-002..006) tidak bisa menulis acceptance criteria presisi. Menunggu keputusan bisnis final untuk tiap butir menunda baseline tanpa manfaat proporsional.

## Decision
Seluruh `[TBD]` ditutup dengan **nilai baseline yang wajar** (reviewed ARB 2026-07-21). Setiap nilai ditandai di katalog dengan "(baseline ARB 2026-07-21 — dapat direvisi BO via DEC)".

| Rule | Butir [TBD] | Nilai Baseline |
|---|---|---|
| BR-CP-02 | Proses override otorisasi | Override hanya oleh **Administrator** dengan justifikasi tercatat + audit trail |
| BR-CRM-02 | Field pelanggan yang dibatasi per role | Kontak pelanggan (**phone/email**) dimask untuk role non-CS |
| BR-CRM-03 | Ambang interaksi "penting" | Interaksi yang **tertaut ke case**; interaksi ringan tanpa case tidak wajib dicatat |
| BR-ECMF-02 | Aturan akses lintas unit | Aksi tulis hanya oleh **supervisor unit induk**; unit lain **read-only** |
| BR-ECMF-05 | Kalender kerja/jam operasional SLA | **24x7** dulu; kalender kerja = konfigurasi SLA fase berikut |
| BR-ECMF-06 | Kategori wajib evidence saat closure | Wajib untuk **COMPLAINT**, opsional untuk **INQUIRY** |
| BR-ECMF-07 | Jangka waktu reopen sejak closure | **30 hari kalender** |
| BR-NOTIF-04 | Kebijakan retry + channel fallback | Retry maksimal **3x interval 5 menit**; setelah max retry, eskalasi via **email ke supervisor** terkait |
| BR-KPI-03 | Daftar KPI berinput manual | **Tidak ada** KPI manual di fase awal (daftar kosong) |
| BR-ADM-01 | Daftar konfigurasi kritikal | **Workflow config, SLA config, role-permission** |

## Kewenangan Revisi
- **Business Owner (BO)** berwenang merevisi setiap nilai baseline di atas melalui **DEC baru** (bukan edit langsung katalog); katalog di-update mengikuti DEC tersebut.
- Revisi yang berdampak arsitektur (mis. mengubah model event/retry infrastruktur) tetap memerlukan ADR sesuai governance.
- Implementasi/tes hanya mengutip skema delivery `BR-0xx` (per DEC-003); nilai baseline ini mengalir ke delivery rule terkait via tabel mapping.

## Rationale
Menutup [TBD] dengan default konservatif membuka jalur Approved untuk BR-CAT-001 dan FRD Draft multi-domain, tanpa mengunci keputusan bisnis — semua nilai reversible via DEC.

## Impact
- `ECMP_Business_Rules_v1.0.md` naik ke v1.2, status 🟢 Approved (baseline).
- FRD-002..006 dapat merujuk nilai baseline (mis. masking BR-CRM-02, retry BR-NOTIF-04, kalender 24x7 BR-ECMF-05).
- `11 SLA and KPI Matrix` mewarisi baseline kalender 24x7 sampai konfigurasi kalender kerja dibangun.

## Follow-up
- [x] Update `ECMP_Business_Rules_v1.0.md` (tutup [TBD], status Approved, Open Items)
- [ ] Sinkronkan `11 SLA and KPI Matrix` saat matriks SLA dirinci
- [ ] Angkat nilai baseline ke delivery rule `BR-0xx` saat rule terkait masuk sprint

## Links
- Related: `02 Business Rules/ECMP_Business_Rules_v1.0.md`, DEC-001, DEC-002, DEC-003
