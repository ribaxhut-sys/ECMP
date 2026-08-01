# ECMP_FRD_KPI_SLA_v0.1

| Field | Value |
|---|---|
| ID | FRD-005 |
| Version | 0.2 |
| Owner | Business Analyst |
| Reviewer | Performance Owner / Operations Lead |
| Approver | Business Owner |
| Status | 🔒 **LOCKED** |
| Last Review | 2026-08-01 |
| Next Review | 2027-01-21 |
| Capability | **CAP-006** (SLA Measurement & Breach Detection) |
| Governing Decision | **DEC-CAP006-BQ-001** (`../deploy/evidence/B2-15_CAP-006_Business_Decision_Closure_20260801.md`) |
| Governance Closure | B2-16 — `../deploy/evidence/B2-16_CAP-006_FRD_Lock_Governance_Closure_20260801.md` |

> **LOCKED** under DEC-CAP006-BQ-001 (B2-15 BUSINESS READY → B2-16 applied).  
> **SoT for CAP-006 / FR-030.** Implementation waits DEC-002 / sprint gate; does **not** invent APIs, events, scheduler, or SLA algorithm beyond existing catalogs (DEC-004/005, SLA-MTX-001, EVT-004).

## 1. Overview
Pengukuran SLA otomatis dari event operasional dan deteksi breach (**BP-005** / **CAP-006**): SLA clock per kategori/prioritas, emisi `SLABreached` (**EVT-004**) saat ambang terlampaui.

**Case SoT for CAP-006 v0.2 (DEC-CAP006-BQ-001 §1):** Sprint ECMF Case lifecycle events (EVT-001/003/005/007) + targets in `11 SLA and KPI Matrix` (SLA-MTX-001 / DEC-005).  
**Not** BR-CM-006 Working Day Aggregate Case SLA.  
**Not** DEC-012/013/014 complaint-stage SLA foundation (local status; EVT-004 deferred in that track).

Domain: **KPI & Performance**. Capability: **CAP-006**.

## 2. Actors & Roles
| Actor | Role |
|---|---|
| System (KPI service) | Konsumsi event case; evaluasi SLA clock; deteksi warning/breach; emit EVT-004 |
| Operations Lead | Pemilik konfigurasi SLA (kategori × prioritas) / governance target |
| Supervisor / Manager | Konsumen fakta breach (via Notification/Dashboard) |
| Administration | SoT runtime **SLA Config** (ADR-008; BR-ADM-01) |

## 2a. Architecture Ownership (separation of responsibility — not dual ownership)
Per `06 Data Dictionary` + Event Catalog + this FRD (DEC-CAP006-BQ-001 §11):

| Concern | Owner | Notes |
|---|---|---|
| SLA clock **attributes** on case (running timer facts / status history basis) | **ECMF** | Data Dictionary: entity SLA Clock → ECMF |
| SLA **Config** / rules parameters (targets, calendar binding when activated) | **Administration** | Data Dictionary SLA Config; KPI reads active values (e.g. via EVT-006) |
| Runtime **evaluation**, warning evaluation, breach detection, **EVT-004 emission** | **KPI** | FRD Actors; EVT-004 producer = KPI; Breach Event → KPI |

This is **separation of responsibility**, not competing dual SoT for the same function.

## 3. Functional Requirements
| FR-ID | Requirement | Priority | BR Ref | API/Event | Test |
|---|---|---|---|---|---|
| FR-030 | System shall detect SLA threshold breach and emit SLABreached event | Must | BR-005 | EVT-004 (producer: KPI) | TC-030 |

## 4. Business Rules Reference
- **BR-005** (BR-ECMF-05): SLA dihitung otomatis dari konfigurasi kategori & prioritas; **kalender baseline 24x7** (DEC-004) — kalender kerja/jam operasional = konfigurasi fase berikut
- **BR-KPI-01/02**: setiap KPI wajib punya formula/owner/periode; perubahan via governance konfigurasi
- **BR-KPI-03 (baseline DEC-004)**: tidak ada KPI berinput manual di fase awal
- **BR-KPI-04**: setiap angka KPI traceable ke transaksi sumber
- **Numeric targets / warning 80% / breach→EVT-004:** DEC-005 + SLA-MTX-001 (OQ-008 Resolved)

## 5. Definitions (repository-anchored)
| Term | Meaning (SoT) |
|---|---|
| `dueAt` | Batas waktu SLA dari konfigurasi kategori×prioritas (SLA-MTX / SLA Config) pada kalender baseline 24x7 |
| Warning (80%) | 80% target elapsed → Notification domain alert; **bukan** event enterprise baru (DEC-005) |
| Breach | Clock melewati `dueAt` tanpa pemenuhan → emit EVT-004 sekali per `caseId`+`slaId` per siklus; re-breach setelah reopen diizinkan |
| `slaId` | Identifier instance/aturan SLA pada payload EVT-004 (Event Catalog) |

## 6. Event Flow
Konsumsi EVT-001 (start clock), EVT-003 (status clock), EVT-005 (stop/finalize), EVT-007 (restart saat reopen) → deteksi overdue → emit **EVT-004 SLABreached** (caseId, slaId, breachedAt, dueAt, severity). Idempoten per caseId + slaId; re-breach setelah reopen diperbolehkan (lihat `08 Event Catalog/events/events.yaml`).

## 7. Acceptance Criteria (ringkas, Gherkin)
```gherkin
Scenario: Breach terdeteksi
  Given case dengan SLA aktif (kategori+prioritas terkonfigurasi, kalender 24x7)
  When waktu berjalan melewati dueAt tanpa status pemenuhan
  Then EVT-004 SLABreached diemit tepat satu kali per caseId+slaId (TC-030)

Scenario: Clock berhenti saat closed
  Given case CLOSED sebelum dueAt
  Then tidak ada breach; performance fact difinalisasi dari EVT-005
```

Targets numerik First Response / Resolution per prioritas: **SLA-MTX-001** (DEC-005) — tidak diulang sebagai angka baru di FRD ini.

## 8. Dependencies
- FR-004 (StatusChanged) dan konfigurasi SLA di `11 SLA and KPI Matrix` (sinkron dengan baseline DEC-004/005)
- Event bus operasional (lihat dependency FRD-004) — **evaluation mechanism** (job vs event-only) = engineering/ADR (DEC-CAP006-BQ-001 §10); not specified as business invention here
- Traceability: TRC-L-007 (Sprint-03, Planned until Implemented)
- DEC-CAP006-BQ-001; DEC-004; DEC-005

## 9. Out of Scope (versi ini)
- Kalender kerja/jam operasional (aktivasi **DEFERRED** — fase berikut).
- Pause / Resume clock (**DEFERRED / OOS** CAP-006 v1; BR-CM-006 track terpisah).
- Diferensiasi target COMPLAINT vs INQUIRY (**DEFERRED** — SLA-MTX Open Items).
- Complaint-stage SLA engine DEC-012/013/014 sebagai pemenuhan CAP-006/FR-030.
- KPI agregat eksekutif penuh, target scorecard per agent, input manual KPI.
- Inventaris API HTTP baru untuk FR-030 (contract-first terpisah bila dibutuhkan; TRC-L-007 `api: []` saat LOCK).
- Inventaris event enterprise baru selain EVT-004 yang sudah di katalog.

## 10. Repository & Decision References
| Artifact | Role |
|---|---|
| BP-005 / CAP-006 Capability Register | Capability statement |
| DEC-004 / DEC-005 | Calendar + numeric baseline + warning/breach policy |
| DEC-CAP006-BQ-001 (B2-15) | BQ closure |
| B2-16 evidence | FRD LOCK governance |
| SLA-MTX-001 | Numeric targets SoT |
| EVT-004 (Planned) | Breach event contract |
| TRC-L-007 / TC-030 | Trace + test (Planned) |
| DEC-012/013/014 | Separate complaint-stage scope (≠ this FRD fulfillment) |
| DEC-020 | Dual SoT coexistence context (not SLA calendar decision) |

## 11. Document History
| Ver | Date | Change |
|---|---|---|
| 0.1 | 2026-07-21 | Initial Draft |
| 0.2 | 2026-08-01 | B2-16 LOCK — apply DEC-CAP006-BQ-001 (SoT scope, ownership separation, OOS/DEFERRED); no new events/APIs/algorithms invented |
