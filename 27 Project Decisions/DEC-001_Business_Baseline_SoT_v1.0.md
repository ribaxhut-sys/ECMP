# Decision Record — Business Baseline Source of Truth

| Field | Value |
|---|---|
| ID | DEC-001 |
| Version | 1.0 |
| Owner | Business Owner |
| Reviewer | Solution Architect / PMO |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

- Type: Project Decision (non-ADR)
- Status: Accepted
- Date: 2026-07-21
- Owner: Business Owner (delegated via ARB review 2026-07-21)
- Participants: Architecture Review Board, Solution Architect, PMO

## Context
Sprint 0 discovery (`archive/ECMP_SPRINT0_DISCOVERY_REPORT.md`) menemukan dua baseline bisnis yang bertentangan:

1. **Baseline EKR** — Blueprint v2.1 + FRD-001: model CS/ECMF case lifecycle (create → assign → process → review → close), 7 domain, Customer Master eksternal read-only.
2. **Baseline brief discovery** — model "branch → Head Office escalation → schedule slot → work order", yang **tidak ada** di Blueprint, FRD, Business Rules, Data Dictionary, maupun Event Catalog yang di-approve. Dokumen sumber ("KAK") tidak ada di repositori.

## Options
- **A.** Blueprint v2.1 + FRD-001 sebagai satu-satunya baseline; brief discovery ditolak sebagai lingkup produk.
- **B.** Revisi Blueprint/FRD/katalog untuk mengadopsi model branch/HO/scheduling.
- **C.** Jalankan keduanya paralel (dual baseline).

## Decision
**Opsi A.** Baseline bisnis resmi ECMP adalah **`01 Business Blueprint/ECMP_Business_Blueprint_v2.1.docx` + `03 Functional Requirements/ECMP_FRD_ECMF_v0.1.md` (FRD-001)** beserta katalog turunannya (BR, API, Event, Data Dictionary).

- Konsep **Branch Officer / Head Office escalation / Schedule Slot / Appointment / Work Order** dinyatakan **di luar lingkup** sampai ada revisi Blueprint yang di-approve Architecture Board.
  - **Exception (DEC-007 / TASK-014):** Appointment **booking only** (API-305/306) is authorized; Calendar, Slots, Check-In, Completion, Notification, SLA, Auto Close, and Work Order remain out of scope.
- Dokumen KAK yang dirujuk brief discovery dinyatakan **superseded** oleh Blueprint v2.1 untuk keperluan implementasi. Bila KAK ditemukan dan relevan, ia masuk lewat proses revisi Blueprint, bukan langsung ke implementasi.
- Sprint 0/Build-1 berjalan pada slice Case create/get sesuai FRD-001 terlepas dari hasil penelusuran KAK.

## Rationale
Baseline EKR adalah satu-satunya yang ter-approve, konsisten lintas katalog, dan tertelusur (BP→BR→FR→API/EVT/TC). Mengkode terhadap model yang tidak terdokumentasi menghasilkan kerja buangan dan melanggar hard constraint "Do not invent Out of Scope features".

## Impact
- Engineer memiliki satu baseline yang tidak ambigu.
- Semua konsep branch/HO/scheduling **dilarang** dimodelkan (schema, endpoint, event, ADR) sampai revisi Blueprint di-approve.

## Follow-up
- [x] Catat non-goals Sprint 0/Build-1 di `DEC-002` (Build Authorization).
- [x] Tambah OQ-004 di `OPEN_QUESTIONS.md` dengan status Resolved.

## Links
- Related: `archive/ECMP_SPRINT0_DISCOVERY_REPORT.md`, `archive/ECMP_SPRINT0_SENIOR_ENGINEER_REVIEW.md`
- Related ADR (if later elevated): —
