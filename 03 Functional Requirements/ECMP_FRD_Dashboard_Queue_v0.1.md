# ECMP_FRD_Dashboard_Queue_v0.1

| Field | Value |
|---|---|
| ID | FRD-006 |
| Version | 0.1 |
| Owner | Business Analyst |
| Reviewer | Dashboard PO / Solution Architect |
| Approver | Business Owner |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2026-10-21 |

> **Draft — belum DoR; implementasi menunggu gate per DEC-002.**

## 1. Overview
Dashboard antrian operasional untuk supervisor (BP-006): view queue/workload case ter-scope role & organisasi, read-only, drill-down ke case.

Domain: **Dashboard & Analytics**.

## 2. Actors & Roles
| Actor | Role |
|---|---|
| Supervisor | Monitoring antrian & beban unit-nya |
| Manager / Executive | View agregat lintas unit (sesuai scope) |
| System | Sajikan data ter-scope; tidak memutasi transaksi |

## 3. Functional Requirements
| FR-ID | Requirement | Priority | BR Ref | API/Event | Test |
|---|---|---|---|---|---|
| FR-040 | System shall show operational case queue dashboard scoped by role and organization | Must | BR-006 | API-040 | — (TC menyusul saat DoR) |

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
- FR-003/FR-004 (agar antrian punya status/assignment bermakna) dan fakta KPI (FR-030) untuk kolom SLA
- Role Supervisor + scoping org di Role Access Matrix (revisi SEC-RAM-001)
- Traceability: TRC-L-008 (Sprint-03, Planned)

## 7. Out of Scope (versi ini)
- Dashboard eksekutif penuh, custom widget builder, export terjadwal, mutasi apa pun dari dashboard (dilarang permanen per BR-DASH-03).
