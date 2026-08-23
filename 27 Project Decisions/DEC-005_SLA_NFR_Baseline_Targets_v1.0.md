# Decision Record — SLA & NFR Baseline Targets (Penutupan Target Numerik)

| Field | Value |
|---|---|
| ID | DEC-005 |
| Version | 1.0 |
| Owner | Operations Lead |
| Reviewer | BA Lead / Solution Architect / Domain Product Owners |
| Approver | Business Owner |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

- Type: Project Decision (non-ADR)
- Status: Accepted
- Date: 2026-07-21
- Owner: Operations Lead
- Participants: Architecture Review Board, Business Owner, BA Lead, Domain POs, Operations

## Context
Dua artefak enterprise masih terblokir karena tidak ada target numerik: (1) SLA Matrix di `11 SLA and KPI Matrix` (bagian 2 KPI Dictionary seluruhnya `[TBD]`, memblok BR-ECMF-05 / KPI-ECMF-03 / KPI-ECMF-04 dan desain eskalasi Notification), dan (2) NFR targets di `04 Solution Architecture` (checklist README "NFR targets" belum tercentang; checklist `07 API Catalog` "SLAs for API availability/latency" belum tertaut). Menunggu workshop Business Owner untuk tiap angka menunda baseline tanpa manfaat proporsional — pola yang sama sudah diselesaikan DEC-004 untuk `[TBD]` Business Rules.

## Decision
Seluruh target numerik SLA dan NFR ditutup dengan **nilai baseline konservatif** (reviewed ARB 2026-07-21). Setiap nilai ditandai di dokumen turunan dengan "(baseline ARB 2026-07-21 — dapat direvisi BO via DEC)".

### (a) SLA respon/resolusi case per prioritas

> ⚠️ **Kolom *Resolution Target* disupersede oleh [DEC-031](./DEC-031_SLA_Resolution_Target_30_Calendar_Days_v0.1.md)** (2026-08-23, 🟡 Draft) — satu target seragam **30 hari kalender**, diukur pada Complaint. Kolom *First Response Target* dan seluruh nilai NFR di §(c) **tidak** tersentuh.

Kalender: **24x7** (baseline BR-ECMF-05 per DEC-004) — semua durasi adalah waktu kalender; saat kalender kerja dikonfigurasi (fase berikut), durasi hari dibaca sebagai hari kerja.

| Priority | First Response Target | Resolution Target |
|---|---|---|
| CRITICAL | 30 menit | 4 jam |
| HIGH | 1 jam | 8 jam |
| MEDIUM | 4 jam | 2 hari (48 jam kalender) |
| LOW | 8 jam | 5 hari (120 jam kalender) |

Baseline berlaku seragam untuk semua case type (COMPLAINT, INQUIRY); diferensiasi per case type = kandidat revisi BO via DEC saat data operasional tersedia.

### (b) Threshold breach & eskalasi
| Item | Nilai Baseline |
|---|---|
| Definisi breach | SLA clock melewati `dueAt` tanpa pemenuhan → emit **EVT-004 SLABreached** tepat satu kali per caseId+slaId (FR-030/TC-030) |
| Warning threshold | **80%** dari waktu target terlewati → notifikasi warning ke assignee/supervisor (ambang konfigurasi SLA; tanpa event enterprise baru — memakai jalur domain Notification) |
| Eskalasi breach | Alert breach ke supervisor unit terkait; kegagalan delivery mengikuti **BR-NOTIF-04 baseline** (retry maks 3x interval 5 menit, lalu eskalasi email ke supervisor) |

### (c) NFR baseline
| NFR | Nilai Baseline | Catatan Fase |
|---|---|---|
| Availability | **99.5%** jam layanan | Berlaku sebagai target saat shared environment ada; slice DEV/CI = best effort |
| Latency API (p95) | Baca **< 300 ms**, tulis **< 800 ms** | Diverifikasi saat performance test aktif (Test Strategy §6) |
| Throughput | **10 rps sustained** (slice) | Naik mengikuti sizing shared env |
| Kapasitas data tahun-1 | ± **50.000 case**, DB < **20 GB** | Estimasi kasar; asumsi di NFR Spec |
| RTO / RPO | RTO **4 jam** / RPO **15 menit** | Mengikat DR plan `15 Operations Runbook` |

Detail lengkap (security, auditability, observability) didokumentasikan di `04 Solution Architecture/ECMP_NFR_Specification_v0.1.md` (NFR-001).

## Kewenangan Revisi
- **Business Owner (BO)** berwenang merevisi setiap nilai baseline di atas melalui **DEC baru** (bukan edit langsung matriks/spesifikasi); dokumen turunan di-update mengikuti DEC tersebut.
- Revisi yang berdampak arsitektur (mis. mengubah mekanisme SLA clock, model event, atau topologi DR) tetap memerlukan ADR sesuai governance.
- Nilai SLA operasional mengalir ke **SLA Config** (BR-ADM-01 konfigurasi kritikal; SoT config = Administration per ADR-008); perubahan config runtime memancarkan EVT-006 ConfigChanged — tidak menggantikan kewenangan DEC untuk mengubah baseline enterprise.

## Rationale
Menutup target numerik dengan default konservatif membuka jalur baseline untuk SLA Matrix (SLA-MTX-001), NFR Specification (NFR-001), dan trigger performance test (Test Strategy §6), tanpa mengunci keputusan bisnis — semua nilai reversible via DEC, konsisten dengan pola DEC-004.

## Impact
- `11 SLA and KPI Matrix/ECMP_SLA_Matrix_v0.1.md` (baru, SLA-MTX-001) — 🟢 Approved (baseline).
- `04 Solution Architecture/ECMP_NFR_Specification_v0.1.md` (baru, NFR-001) — nilai baseline resmi, dokumen 🟡 Draft menunggu review Ops/BO.
- KPI Dictionary (SLA-001): KPI-ECMF-03/04 dan bagian 2 dapat merujuk nilai baseline ini.
- `07 API Catalog` checklist SLA availability/latency dapat dicentang dengan link.
- Performance test (Test Strategy §6) kini punya target numerik; aktivasi tetap menunggu environment SIT.

## Follow-up
- [x] Buat `ECMP_SLA_Matrix_v0.1.md` (SLA-MTX-001) memakai nilai baseline ini
- [x] Buat `ECMP_NFR_Specification_v0.1.md` (NFR-001) memakai nilai baseline ini
- [ ] Sinkronkan KPI Dictionary (SLA-001) bagian 2 dengan SLA Matrix saat naik versi
- [ ] Angkat nilai SLA ke SLA Config runtime saat konfigurasi Administration masuk sprint
- [ ] Review Ops/BO untuk NFR-001 (naikkan status dari Draft)

## Links
- Related: `../11 SLA and KPI Matrix/ECMP_SLA_Matrix_v0.1.md`, `../04 Solution Architecture/ECMP_NFR_Specification_v0.1.md`, `../02 Business Rules/ECMP_Business_Rules_v1.0.md`, `../03 Functional Requirements/ECMP_FRD_KPI_SLA_v0.1.md`, DEC-004
