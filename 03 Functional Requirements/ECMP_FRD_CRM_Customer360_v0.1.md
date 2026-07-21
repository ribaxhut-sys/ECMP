# ECMP_FRD_CRM_Customer360_v0.1

| Field | Value |
|---|---|
| ID | FRD-003 |
| Version | 0.1 |
| Owner | Business Analyst |
| Reviewer | CRM PO / Solution Architect |
| Approver | Business Owner |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2026-10-21 |

> **Draft — belum DoR; implementasi menunggu gate per DEC-002.**

## 1. Overview
Customer 360 read-only untuk mendukung penanganan case (BP-003): pencarian dan tampilan profil pelanggan dari Customer Master eksternal, diperkaya konteks interaksi/case ECMP.

Domain: **CRM**. ECMP bukan SoR pelanggan (BR-003 / DEC-001).

## 2. Actors & Roles
| Actor | Role |
|---|---|
| CS Agent | Search/view profil pelanggan saat menangani case |
| Role non-CS (Viewer, dsb.) | View dengan masking field kontak |
| Customer Master (external) | Sumber data master (read-only) |

## 3. Functional Requirements
| FR-ID | Requirement | Priority | BR Ref | API/Event | Test |
|---|---|---|---|---|---|
| FR-010 | System shall allow authorized user to search/view customer 360 profile (read-only) | Must | BR-003 | API-010 | TC-010 |

## 4. Business Rules Reference
- **BR-003** (BR-CRM-01/04): Customer Master read-only; tidak ada write-back; cache read-only diperbolehkan
- **BR-CRM-02 (baseline DEC-004)**: field kontak pelanggan (**phone/email**) **dimask** untuk role non-CS — need-to-know
- **BR-CRM-03 (baseline DEC-004)**: interaksi tertaut case wajib dicatat dan ditautkan ke Customer ID

## 5. Acceptance Criteria (ringkas, Gherkin)
```gherkin
Scenario: CS melihat profil pelanggan
  Given user dengan role CS Agent dan customerId valid
  When GET /v1/customers/{customerId}
  Then 200 dengan profil 360 (data master + case/interaksi terkait), tanpa masking

Scenario: Role non-CS melihat profil pelanggan
  Given user tanpa role CS
  When GET /v1/customers/{customerId}
  Then 200 dengan phone/email dimask sesuai BR-CRM-02 baseline

Scenario: Tidak ada mutasi data master
  Given endpoint customer apapun
  Then tidak tersedia operasi write terhadap data master (read-only, BR-003)
```

## 6. Dependencies
- Kontrak integrasi Customer Master (mode stub Sprint-01: `customerVerified=false`, FRD-001 §8)
- Permission read customer di Role Access Matrix (revisi SEC-RAM-001)
- Traceability: TRC-L-005 (Planned, Sprint-02 — implementasi menunggu G0 exit per DEC-002)

## 7. Out of Scope (versi ini)
- Edit/pengayaan data master, deduplication, segmentasi pelanggan, interaksi non-case (interaksi ringan tidak wajib dicatat per BR-CRM-03 baseline).
