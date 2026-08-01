# RTM — Complaint Management Escalation & Resolution (DEC-F4) — Draft

| Field | Value |
|---|---|
| Document ID | RTM-CM-F4-001 |
| Version | 0.1 |
| Status | 🟡 Draft |
| Date | 2026-07-29 |
| FRD | FRD-CM-002 v0.1 Draft |
| DEC | GOV-DEC-F4 |
| BR | BR-CM-CAT-001 BR-007, BR-008 |
| UAT | TC-CAT-CM-F4-001 |

> Draft coverage matrix. Not LOCKED. Batch 1 RTM-CM-B1-001 unchanged.

## FR → BR → API → EVT → UAT

| FR | BR | API | EVT | UAT |
|---|---|---|---|---|
| FR-CM-010 | BR-007 | API-520 | EVT-CM-040 | UAT-F4-04 (+ escalate happy path in 01/05) |
| FR-CM-011 | BR-007 | API-521 | EVT-CM-041 | UAT-F4-05…09 |
| FR-CM-012 | BR-007 | API-522 | — | UAT-F4-03 |
| FR-CM-013 | BR-008 | API-523 | EVT-CM-042 | UAT-F4-01, 02 |
| FR-CM-014 | BR-008 | API-524 | EVT-CM-043 | UAT-F4-10, 11 |
| FR-CM-015 | BR-007, BR-008 | API-525, API-526 | EVT-CM-044 | UAT-F4-01, 02, 10, 11 |

## Coverage notes

- Case create / Assignment / SLA FRDs remain prerequisites (not covered here).
- Foundation escalate APIs (API-207/301) are **out of this RTM** until DEC remapping (OQ-CM-F4-001).

## Related

- `03 Functional Requirements/ECMP_FRD_Complaint_Management_Escalation_Resolution_v0.1.md`
- `26 Traceability/ECMP_IMPACT_DEC_F4_v1.0.md`
- `26 Traceability/ECMP_RTM_Complaint_Management_Batch1_v1.0.md` (LOCKED — separate)
