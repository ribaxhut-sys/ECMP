# ECMP SLA Matrix v0.1

| Field | Value |
|---|---|
| ID | SLA-MTX-001 |
| Version | 0.1 |
| Owner | Operations Lead |
| Reviewer | Business Owner, BA Lead, Domain PO ECMF |
| Approver | Business Owner |
| Status | 🟢 Approved (baseline — target numerik ditutup per DEC-005) |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Matriks target SLA per case type × priority untuk case management (ECMF). Seluruh nilai adalah **baseline DEC-005** — setiap angka bertanda "(baseline ARB 2026-07-21 — dapat direvisi BO via DEC)". Matriks ini adalah sumber nilai untuk SLA Config runtime dan acuan deteksi breach FR-030.

> ⚠️ **Kolom *Resolution Target* di §1 disupersede oleh [DEC-031](../27%20Project%20Decisions/DEC-031_SLA_Resolution_Target_30_Calendar_Days_v0.1.md)** (2026-08-23, 🟡 Draft — menunggu tanda tangan Business Owner).
> DEC-031 menetapkan **satu target seragam: 30 hari kalender**, menggantikan 4 jam / 8 jam / 2 hari / 5 hari per prioritas di bawah, dan mengukurnya pada **Complaint** (bukan Case — deviasi tercatat dari BR-006).
> Kolom *First Response Target* **tidak** disentuh DEC-031 dan tetap seperti tertulis.
> Nilai per-prioritas di §1 dipertahankan sebagai riwayat baseline; jangan dipakai sebagai target berjalan begitu DEC-031 ditandatangani.

## 1. SLA Matrix (case type × priority)
Nilai baseline berlaku seragam untuk COMPLAINT dan INQUIRY (diferensiasi per case type = kandidat revisi BO via DEC). Semua durasi = waktu kalender 24x7 (lihat §2).

| Case Type | Priority | First Response Target | Resolution Target | Warning Threshold (80%) | Breach Action | Owner |
|---|---|---|---|---|---|---|
| COMPLAINT | CRITICAL | 30 menit | 4 jam | 24 menit / 3 jam 12 menit | Emit EVT-004 SLABreached + eskalasi supervisor (BR-NOTIF-04 baseline) | Operations Lead |
| COMPLAINT | HIGH | 1 jam | 8 jam | 48 menit / 6 jam 24 menit | Emit EVT-004 SLABreached + eskalasi supervisor (BR-NOTIF-04 baseline) | Operations Lead |
| COMPLAINT | MEDIUM | 4 jam | 2 hari (48 jam) | 3 jam 12 menit / 38,4 jam | Emit EVT-004 SLABreached + eskalasi supervisor (BR-NOTIF-04 baseline) | Operations Lead |
| COMPLAINT | LOW | 8 jam | 5 hari (120 jam) | 6 jam 24 menit / 96 jam | Emit EVT-004 SLABreached + eskalasi supervisor (BR-NOTIF-04 baseline) | Operations Lead |
| INQUIRY | CRITICAL | 30 menit | 4 jam | 24 menit / 3 jam 12 menit | Emit EVT-004 SLABreached + eskalasi supervisor (BR-NOTIF-04 baseline) | Operations Lead |
| INQUIRY | HIGH | 1 jam | 8 jam | 48 menit / 6 jam 24 menit | Emit EVT-004 SLABreached + eskalasi supervisor (BR-NOTIF-04 baseline) | Operations Lead |
| INQUIRY | MEDIUM | 4 jam | 2 hari (48 jam) | 3 jam 12 menit / 38,4 jam | Emit EVT-004 SLABreached + eskalasi supervisor (BR-NOTIF-04 baseline) | Operations Lead |
| INQUIRY | LOW | 8 jam | 5 hari (120 jam) | 6 jam 24 menit / 96 jam | Emit EVT-004 SLABreached + eskalasi supervisor (BR-NOTIF-04 baseline) | Operations Lead |

Semua nilai: baseline ARB 2026-07-21 per DEC-005 — dapat direvisi BO via DEC.

### Semantik breach & warning
- **Breach** = SLA clock melewati `dueAt` tanpa pemenuhan → **EVT-004 SLABreached** diemit tepat satu kali per caseId+slaId (FR-030, diverifikasi TC-030); re-breach setelah reopen diperbolehkan (lihat `../08 Event Catalog/events/events.yaml`).
- **Warning** = 80% waktu target terlewati → notifikasi warning ke assignee/supervisor melalui domain Notification. Warning adalah ambang konfigurasi SLA, **bukan** event enterprise baru.
- Kegagalan delivery alert mengikuti **BR-NOTIF-04 baseline** (retry maks 3x interval 5 menit; setelah max retry, eskalasi via email ke supervisor terkait).

## 2. Kalender Kerja / Business Calendar
- Baseline: **24x7** — semua durasi SLA dihitung waktu kalender (BR-ECMF-05, baseline DEC-004).
- Kalender kerja / jam operasional = **konfigurasi SLA fase berikut** (BR-ECMF-05); saat diaktifkan, durasi "hari" dibaca sebagai hari kerja dan SLA clock mengikuti jam layanan.
- SoT konfigurasi SLA = domain **Administration** (ADR-008 — Administration sebagai konfigurator); SLA config termasuk konfigurasi kritikal per BR-ADM-01 (baseline DEC-004).

## 3. Hubungan ke Konfigurasi & Artefak Lain
- **SLA Config runtime**: nilai matriks ini diangkat ke SLA Config (Administration); perubahan config efektif memancarkan **EVT-006 ConfigChanged**. Perubahan baseline enterprise tetap via DEC (bukan edit config langsung).
- **KPI Dictionary** ([`ECMP_KPI_Dictionary_v1.0.md`](./ECMP_KPI_Dictionary_v1.0.md), SLA-001): KPI-ECMF-03 (SLA achievement) dan KPI-ECMF-04 (overdue rate) mengukur pemenuhan target matriks ini.
- **FR-030 / TC-030** ([`../03 Functional Requirements/ECMP_FRD_KPI_SLA_v0.1.md`](../03%20Functional%20Requirements/ECMP_FRD_KPI_SLA_v0.1.md), FRD-005 🔒 **LOCKED** v0.2 / DEC-CAP006-BQ-001): deteksi breach dan emisi EVT-004.
- **NFR Specification** ([`../04 Solution Architecture/ECMP_NFR_Specification_v0.1.md`](../04%20Solution%20Architecture/ECMP_NFR_Specification_v0.1.md), NFR-001): NFR sistem (availability/latency) yang menopang SLA operasional ini.

## Open Items
- Diferensiasi target per case type (COMPLAINT vs INQUIRY) — menunggu data operasional; revisi BO via DEC.
- Aktivasi kalender kerja — menunggu konfigurasi SLA fase berikut (BR-ECMF-05).

## Related
- [`DEC-005`](../27%20Project%20Decisions/DEC-005_SLA_NFR_Baseline_Targets_v1.0.md) — keputusan baseline target numerik
- [`DEC-004`](../27%20Project%20Decisions/DEC-004_BR_Baseline_Defaults_v1.0.md) — baseline kalender 24x7 (BR-ECMF-05)
- `../02 Business Rules/ECMP_Business_Rules_v1.0.md`
- `../08 Event Catalog`
