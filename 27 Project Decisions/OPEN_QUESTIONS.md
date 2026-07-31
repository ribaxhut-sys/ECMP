# Open Questions

| Field | Value |
|---|---|
| ID | OQ-000 |
| Version | 0.1 |
| Owner | PMO |
| Reviewer | Product Owner |
| Approver | Business Owner |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
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
- **OQ-ORG-001:** Dilacak di **DEC-021** (Proposed) — interim: no descendant expansion; Recommend Option A exact-ref.
- **OQ-ORG-002:** Dilacak di **DEC-022** (Proposed) — interim: retain historical refs + fail-closed for new scoped actions.
