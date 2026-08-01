# ECMP_FRD_Dashboard_Queue_v0.1

| Field | Value |
|---|---|
| ID | FRD-006 |
| Version | 0.2 |
| Owner | Business Analyst |
| Reviewer | Dashboard PO / Solution Architect |
| Approver | Business Owner |
| Status | 🔒 **LOCKED** |
| Last Review | 2026-08-01 |
| Next Review | 2027-01-21 |
| Governing Decision | **DEC-CAP007-BQ-001** (`../deploy/evidence/B2-11_CAP-007_Business_Decision_Closure_20260801.md`) |
| Architecture SoT | B2-09 — API-040 = CAP-007 SoT; API-390 / API-513 / Visit Queue **out of scope** (`../deploy/evidence/B2-09_Queue_Architecture_Rationalization_20260801.md`) |
| Governance Closure | B2-12 — `../deploy/evidence/B2-12_CAP-007_FRD_Lock_Governance_Closure_20260801.md` |

> **LOCKED** under DEC-CAP007-BQ-001 (B2-11 READY → B2-12 applied).  
> **OpenAPI:** API-040 **NORMATIVE** — `../07 API Catalog/openapi/dashboard-queues.v1.yaml` **1.0.0** (B2-13).  
> Implementation: authorized against the normative contract (DEC-002 / catalog-first); not yet Implemented in code.

## 1. Overview
Dashboard antrian operasional untuk supervisor (BP-006): view queue/workload **Sprint ECMF Case** ter-scope role & organisasi, read-only.

**Case SoT (DEC-CAP007-BQ-001 §1):** Sprint `/v1/cases` + DOM-ECMF-003 status set. **Not** CAP-008 Aggregate Case. **Not** API-513.

**Drill-down (DEC-CAP007-BQ-001 §3):** read-only UX navigation to existing **API-002** / **API-005** only — no new dashboard mutation API.

Domain: **Dashboard & Analytics**. Capability: **CAP-007**.

## 2. Actors & Roles
| Actor | Role | CAP-007 v0.1 (DEC-CAP007-BQ-001 §4) |
|---|---|---|
| Supervisor | Monitoring antrian & beban **unit-nya** | **In scope** — unit-scoped only |
| Manager / Executive | View agregat lintas unit (sesuai scope) | **Deferred** — later FRD revision |
| System | Sajikan data ter-scope; tidak memutasi transaksi | In scope |

## 3. Functional Requirements
| FR-ID | Requirement | Priority | BR Ref | API/Event | Test |
|---|---|---|---|---|---|
| FR-040 | System shall show operational case queue dashboard scoped by role and organization | Must | BR-006 | API-040 | TC-040 |

## 4. Business Rules Reference
- **BR-006** (BR-DASH-01/04): tampilan mengikuti role & organisasi; data sensitif tetap tunduk otorisasi Core Platform (BR-CP-02)
- **BR-DASH-02**: angka agregat wajib reconcile dengan sumber; lag ditandai timestamp "as of"
- **BR-DASH-03**: dashboard **read-only** — tidak boleh mengubah data transaksi

## 5. Acceptance Criteria (ringkas, Gherkin)
```gherkin
Scenario: Supervisor melihat antrian unitnya
  Given user role Supervisor unit U
  When GET /v1/dashboard/queues
  Then 200 dengan antrian case unit U saja (role+org scoped, BR-006)

Scenario: Dashboard read-only
  Given endpoint dashboard apapun
  Then tidak tersedia operasi yang memutasi case/transaksi (BR-DASH-03)

Scenario: Data lag ditandai
  Given data agregat tidak real-time
  Then respons menyertakan timestamp "as of" (BR-DASH-02)
```

## 6. Dependencies
- FR-003/FR-004 (agar antrian punya status/assignment bermakna)
- **FR-030** kolom SLA: **Deferred** soft-dep (DEC-CAP007-BQ-001 §5) — not required for CAP-007 v0.1
- Permission **`dashboard:read`** (DEC-CAP007-BQ-001 §2; DEC-016; SEC-RAM-001 Planned Sprint-03)
- Traceability: TRC-L-008 (Sprint-03)

## 7. Out of Scope (versi ini)
- Dashboard eksekutif penuh, custom widget builder, export terjadwal, mutasi apa pun dari dashboard (dilarang permanen per BR-DASH-03).
- Manager/Executive cross-unit aggregates (DEC-CAP007-BQ-001 §4 Deferred).
- CAP-008 Aggregate Case feeds; API-513; API-390 Visit QueueTicket widget; Visit Queue API-360…381 (B2-09).
- New drill-down OpenAPI operations.

## 8. Document History
| Ver | Date | Change |
|---|---|---|
| 0.1 | 2026-07-21 | Initial Draft |
| 0.2 | 2026-08-01 | B2-12 LOCK — apply DEC-CAP007-BQ-001 (scope, permission, Case SoT, drill-down); no new AC/flows/validation invented |
| 0.2a | 2026-08-01 | B2-13 — API-040 normative pointer (`dashboard-queues.v1.yaml` 1.0.0); no FR business content change |
