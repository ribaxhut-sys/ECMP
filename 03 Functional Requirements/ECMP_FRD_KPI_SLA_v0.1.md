# ECMP_FRD_KPI_SLA_v0.1

| Field | Value |
|---|---|
| ID | FRD-005 |
| Version | 0.1 |
| Owner | Business Analyst |
| Reviewer | Performance Owner / Operations Lead |
| Approver | Business Owner |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2026-10-21 |

> **Draft — belum DoR; implementasi menunggu gate per DEC-002.**

## 1. Overview
Pengukuran SLA otomatis dari event operasional dan deteksi breach (BP-005): SLA clock per kategori/prioritas, emisi `SLABreached` saat ambang terlampaui.

Domain: **KPI & Performance**.

## 2. Actors & Roles
| Actor | Role |
|---|---|
| System (KPI service) | Konsumsi event case, hitung SLA clock, deteksi & emit breach |
| Operations Lead | Pemilik konfigurasi SLA (kategori × prioritas) |
| Supervisor / Manager | Konsumen fakta breach (via Notification/Dashboard) |

## 3. Functional Requirements
| FR-ID | Requirement | Priority | BR Ref | API/Event | Test |
|---|---|---|---|---|---|
| FR-030 | System shall detect SLA threshold breach and emit SLABreached event | Must | BR-005 | EVT-004 (producer: KPI) | TC-030 |

## 4. Business Rules Reference
- **BR-005** (BR-ECMF-05): SLA dihitung otomatis dari konfigurasi kategori & prioritas; **kalender baseline 24x7** (DEC-004) — kalender kerja/jam operasional = konfigurasi fase berikut
- **BR-KPI-01/02**: setiap KPI wajib punya formula/owner/periode; perubahan via governance konfigurasi
- **BR-KPI-03 (baseline DEC-004)**: tidak ada KPI berinput manual di fase awal
- **BR-KPI-04**: setiap angka KPI traceable ke transaksi sumber

## 5. Event Flow
Konsumsi EVT-001 (start clock), EVT-003 (status clock), EVT-005 (stop/finalize), EVT-007 (restart saat reopen) → deteksi overdue → emit **EVT-004 SLABreached** (caseId, slaId, breachedAt, dueAt, severity). Idempoten per caseId + slaId; re-breach setelah reopen diperbolehkan (lihat `08 Event Catalog/events/events.yaml`).

## 6. Acceptance Criteria (ringkas, Gherkin)
```gherkin
Scenario: Breach terdeteksi
  Given case dengan SLA aktif (kategori+prioritas terkonfigurasi, kalender 24x7)
  When waktu berjalan melewati dueAt tanpa status pemenuhan
  Then EVT-004 SLABreached diemit tepat satu kali per caseId+slaId (TC-030)

Scenario: Clock berhenti saat closed
  Given case CLOSED sebelum dueAt
  Then tidak ada breach; performance fact difinalisasi dari EVT-005
```

## 7. Dependencies
- FR-004 (StatusChanged) dan konfigurasi SLA di `11 SLA and KPI Matrix` (sinkron dengan baseline DEC-004)
- Event bus operasional (lihat dependency FRD-004)
- Traceability: TRC-L-007 (Sprint-03, Planned)

## 8. Out of Scope (versi ini)
- Kalender kerja/jam operasional, KPI agregat eksekutif penuh, target scorecard per agent, input manual KPI.
