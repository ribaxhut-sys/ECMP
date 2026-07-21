# ECMP NFR Specification v0.1

| Field | Value |
|---|---|
| ID | NFR-001 |
| Version | 0.1 |
| Owner | Solution Architect |
| Reviewer | Operations Lead, Security Officer, Tech Leads |
| Approver | Architecture Board / Business Owner |
| Status | 🟡 Draft (menunggu review Ops/BO — nilai baseline resmi per DEC-005) |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Spesifikasi non-functional requirements ECMP. Seluruh nilai numerik adalah **baseline DEC-005** (baseline ARB 2026-07-21 — dapat direvisi BO via DEC) dan resmi berlaku sebagai acuan meski dokumen ini masih Draft. Dokumen jujur soal fase: sebagian target hanya dapat diverifikasi saat shared environment / performance test aktif.

## Konteks Fase
- **Slice DEV/CI** (saat ini): docker-compose + GitHub Actions (`../14 Deployment Standards`); single service, tanpa environment shared. Sebagian NFR berlaku *best effort* dan belum diukur formal.
- **Target shared env** (SIT/UAT/Production): NFR menjadi target terukur; verifikasi latency/throughput menunggu performance test aktif (trigger di `../13 Test Strategy/ECMP_Test_Strategy_v0.1.md` §6 — kini target numerik tersedia via DEC-005, aktivasi menunggu environment SIT).

## 1. Availability
| Item | Baseline (DEC-005) | Fase |
|---|---|---|
| NFR-AV-01 | Availability **99.5%** jam layanan (≈ maks 3,6 jam downtime/bulan pada 24x7) | Target berlaku saat shared env ada; slice DEV/CI = best effort, tanpa SLO formal |

Jam layanan mengikuti kalender SLA: baseline 24x7 (BR-ECMF-05 / DEC-004); menyempit bila kalender kerja dikonfigurasi fase berikut.

## 2. Latency API
| Item | Baseline (DEC-005) | Fase |
|---|---|---|
| NFR-LT-01 | Operasi baca (mis. GET /v1/cases/{caseId}) p95 **< 300 ms** | Diverifikasi saat performance test aktif (Test Strategy §6) |
| NFR-LT-02 | Operasi tulis (mis. POST /v1/cases) p95 **< 800 ms** | Diverifikasi saat performance test aktif (Test Strategy §6) |

Berlaku untuk API katalog `/v1` (`../07 API Catalog`); diukur di sisi server, tidak termasuk latensi jaringan klien.

## 3. Throughput
| Item | Baseline (DEC-005) | Fase |
|---|---|---|
| NFR-TP-01 | **10 rps sustained** per service pada slice | Baseline slice; sizing ulang saat shared env & multi-service |

## 4. Kapasitas Data Tahun-1
| Item | Baseline (DEC-005) |
|---|---|
| NFR-CP-01 | ± **50.000 case** tahun pertama (asumsi: ± 200 case/hari kerja × 250 hari) |
| NFR-CP-02 | Ukuran database operasional **< 20 GB** tahun pertama (case + status history + audit log; tanpa lampiran biner besar) |

Estimasi kasar — asumsi volume belum divalidasi data channel nyata; revisi via DEC saat data operasional tersedia.

## 5. RTO / RPO (Disaster Recovery)
| Item | Baseline (DEC-005) |
|---|---|
| NFR-DR-01 | **RTO 4 jam** — layanan pulih maksimal 4 jam sejak deklarasi disaster |
| NFR-DR-02 | **RPO 15 menit** — kehilangan data maksimal 15 menit (menuntut backup/WAL archiving interval ≤ 15 menit) |

Nilai ini mengikat DR plan di `../15 Operations Runbook` (dokumen DR/backup menyusul di folder tersebut dan wajib memenuhi baseline ini).

## 6. Security
- Mengikuti model autentikasi **ADR-007** (`../05 Architecture Decision Records/ECMP_ADR_007_Authentication_Model_v1.0.md`): Bearer slice → JWT/OIDC sebelum shared UAT.
- Standar keamanan, role access matrix, dan register keterbatasan AuthN: `../10 Security and Access Standards` (ECMP_Security_Standards_v0.1, ECMP_Role_Access_Matrix_v0.1, ECMP_AuthN_Limitations_Register_v0.1).
- PII/masking mengikuti `../06 Data Dictionary` dan baseline BR-CRM-02 (DEC-004).

## 7. Auditability
- **BR-008** (BR-CP-03 / BR-ECMF-01): setiap write operation pada entity signifikan menghasilkan entri audit log **immutable** (append-only) — kontrol inti, bukan opsional (SA-001 prinsip #5).
- Target kelengkapan audit: **100%** aksi wajib-audit tercatat (selaras KPI-CP-04).

## 8. Observability
- Standar logging/observability: `../21 Technical Standards/ECMP_Observability_Standard_v0.1.md` (TS-OBS-001 — structured logging + correlation-id, aktivasi gate G1; aturan larangan PII berlaku sekarang) dan TS-001 §6.
- Saat pola async multi-service aktif, observability wajib mencakup event bus (lag, dead-letter queue) — lihat SA-001 §9.

## Verifikasi & Traceability
| NFR | Cara Verifikasi | Kapan |
|---|---|---|
| Availability | Monitoring uptime shared env | Saat shared env ada |
| Latency/Throughput | Performance test (Test Strategy §6) | Saat environment SIT tersedia |
| Kapasitas | Review pertumbuhan data berkala | Operasional |
| RTO/RPO | DR drill (folder 15) | Saat DR plan tersedia |
| Security/Audit | Security review + TC audit (BR-008) | Sprint berjalan |

## Related
- [`DEC-005`](../27%20Project%20Decisions/DEC-005_SLA_NFR_Baseline_Targets_v1.0.md) — keputusan baseline target numerik
- [`ECMP_SLA_Matrix_v0.1.md`](../11%20SLA%20and%20KPI%20Matrix/ECMP_SLA_Matrix_v0.1.md) — SLA operasional case (SLA-MTX-001)
- [`ECMP_Solution_Architecture_v1.0.md`](./ECMP_Solution_Architecture_v1.0.md) — SA-001
- `../13 Test Strategy` · `../14 Deployment Standards` · `../15 Operations Runbook`
