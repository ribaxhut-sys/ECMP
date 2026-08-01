# Open Questions

| Field | Value |
|---|---|
| ID | OQ-000 |
| Version | 0.2 |
| Owner | PMO |
| Reviewer | Product Owner |
| Approver | Business Owner |
| Status | 🟡 Draft |
| Last Review | 2026-08-01 |
| Next Review | 2026-10-21 |

| ID | Question | Raised By | Date | Status | Owner | Target Decision Date |
|---|---|---|---|---|---|---|
| OQ-001 | Apakah Channel app masuk fase 1 atau hanya integration boundary? | Architecture | 2026-07-21 | Open | Business Owner | TBD |
| OQ-002 | Stack frontend/backend final untuk standar teknis? | Engineering | 2026-07-21 | Resolved (backend) | Tech Lead | 2026-07-21 |
| OQ-003 | Apakah CQRS diadopsi sekarang atau ditunda? | Architecture | 2026-07-21 | Resolved | Solution Architect | 2026-07-21 |
| OQ-004 | Baseline bisnis: Blueprint/FRD vs brief discovery (branch/HO/scheduling)? | ARB | 2026-07-21 | Resolved | Business Owner | 2026-07-21 |
| OQ-005 | Otorisasi build: Sprint-01 GO vs gate G0? | ARB | 2026-07-21 | Resolved | Engineering Manager | 2026-07-21 |
| OQ-006 | Skema ID Business Rule ganda (BR-0xx vs BR-Domain-NN)? | ARB | 2026-07-21 | Resolved | BA Lead | 2026-07-21 |
| OQ-007 | Audit-on-read: wajib atau ditunda? | ARB | 2026-07-21 | Resolved | Business Owner | 2026-07-21 |
| OQ-008 | Target numerik SLA (respon/resolusi per prioritas) dan NFR (availability/latency/RTO-RPO)? | Operations | 2026-07-21 | Resolved | Business Owner | 2026-07-21 |
| OQ-CM-B1-001 | DEC remapping: when does BR-CM-CAT-001 / Complaint Aggregate replace Sprint delivery SoT for implementation? | Architecture / FRD-CM-001 | 2026-07-29 | Closed | Architecture Board | 2026-07-30 |
| OQ-CM-B1-004 | Production policy for when Batch 2 Case create becomes mandatory after REGISTERED | Architecture / FRD-CM-001 | 2026-07-29 | **CLOSED** | Domain PO ECMF / Product Owner | 2026-08-01 |
| BQ-001 | Case State Machine SoT for Batch-2 Mode A: DOM-ECMF-003 vs BR-CM-CAT Definition B? | Architecture / CAP-008 | 2026-08-01 | **CLOSED** | Architecture Board / Business Owner | 2026-08-01 |
| BQ-002 … BQ-014 | Mode A Delivery Baseline residual BQs (Case Management Batch-2) | Product Owner Session | 2026-08-01 | **CLOSED** (all LOCKED) | Product Owner | 2026-08-01 |
| BQ-CAP006-01 … 15 | CAP-006 SLA Engine residual BQs (calendar, clock, pause, EVT-004, ownership, …) | ARB / B2-15 | 2026-08-01 | **CLOSED** (DEFERRED items explicit) | Business Owner / Performance Owner | 2026-08-01 |
| OQ-ORG-001 | Descendant org scope for AuthZ (ADR-018 O-06)? | Architecture | 2026-07-31 | Open — Proposed DEC-021 (exact-ref interim) | Solution Architect / BO | TBD |
| OQ-ORG-002 | Upstream org restructure / orphan remediation (ADR-018 O-07)? | Architecture | 2026-07-31 | Open — Proposed DEC-022 (retain + fail-closed interim) | Solution Architect / BO | TBD |

## Resolutions
- **OQ-002 (partial):** Backend stack dikunci di `ADR-004` (Python/FastAPI/PostgreSQL). Frontend tetap deferred.
- **OQ-003:** CQRS **ditunda** — tidak relevan untuk slice 2-endpoint; revisit saat ada kebutuhan read-model nyata (ADR-005 layering mencatat deferral).
- **OQ-004:** Blueprint v2.1 + FRD-001 = SoT; model branch/HO/scheduling di luar lingkup. Lihat `DEC-001`.
- **OQ-005:** GO = slice + G0 floor; Build-1 menunggu G0 exit. Lihat `DEC-002`.
- **OQ-006:** SoT delivery = `BR-0xx`; katalog enterprise jadi referensi dengan tabel pemetaan. Lihat `DEC-003`.
- **OQ-007:** Write-audit wajib (BR-008/FR-001c); read-audit ditunda; idempotency key di luar AC Sprint-01. Lihat FRD-001 §9 + `DEC-002`.
- **OQ-008:** Ditutup dengan nilai baseline konservatif (SLA per prioritas, warning 80%, NFR availability/latency/throughput/kapasitas/RTO-RPO) — reversible BO via DEC. Lihat `DEC-005`.
- **OQ-CM-B1-001:** **Closed — remapped by dual SoT (DEC-020)**. Tidak ada tanggal retirement tunggal; dual SoT + controlled coexistence + cutover hanya via Retirement DEC berikutnya. Lihat `DEC-020`.
- **OQ-CM-B1-004 / BQ-002:** **CLOSED** — Complaint MAY register without Case; MUST have ≥1 Case within **1 business day** after REGISTERED; Supervisor Queue MUST display exceedances. Lihat `DEC-MODEA-B2-001`.
- **BQ-001:** **CLOSED — Option O3 APPROVED** (DEC-BQ001). Sprint / case-centric Case SoT = DOM-ECMF-003; Aggregate Case SoT = BR-CM-CAT Definition B. Lihat `ECMP_DEC_BQ001_Case_State_Machine_O3_v1.0.md`.
- **BQ-002 … BQ-014 (Mode A Delivery Baseline):** **ALL LOCKED** — Product Owner Decision Session 2026-08-01. Capability ID final **CAP-008**. Residual BQ for Batch-2 Mode A Case Management = **ZERO**. Lihat `18 Architecture Governance/reviews/ECMP_DEC_ModeA_Delivery_Baseline_BQ_Lock_Pack_v1.0.md`.
- **BQ-CAP006-01 … 15:** **CLOSED** (with explicit DEFERRED: pause/resume v1, Working Day activation, case-type target split) — DEC-CAP006-BQ-001. FRD-005 **LOCKED** B2-16. Lihat `deploy/evidence/B2-15_CAP-006_Business_Decision_Closure_20260801.md` dan `deploy/evidence/B2-16_CAP-006_FRD_Lock_Governance_Closure_20260801.md`.
- **OQ-ORG-001:** Dilacak di **DEC-021** (Proposed) — interim: no descendant expansion; Recommend Option A exact-ref.
- **OQ-ORG-002:** Dilacak di **DEC-022** (Proposed) — interim: retain historical refs + fail-closed for new scoped actions.
