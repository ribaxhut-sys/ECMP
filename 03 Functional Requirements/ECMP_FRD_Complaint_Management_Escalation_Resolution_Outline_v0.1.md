# FRD Outline — Complaint Management Escalation & Resolution (post–Batch 1)

| Field | Value |
|---|---|
| Document ID | FRD-CM-ESC-OUTLINE-001 |
| Version | 0.1 |
| Status | 🟡 Outline — FR content superseded by FRD-CM-002 Draft v0.1 |
| Date | 2026-07-29 |
| Owner | Business Analyst / Domain PO ECMF |
| Depends on | BR-CM-CAT-001 Draft v1.1, **DEC-F4**, ADR-014/015 |
| Does not modify | FRD-CM-001 v1.1 LOCKED (Batch 1) |

## Purpose

Skeleton for the next FRD batch that implements **Escalation** and **Resolution** under DEC-F4. Use this to open Draft FRD work after Architecture Board countersign on DEC-F4.

## Proposed FR candidates (IDs TBD at Draft)

| Candidate | Intent | Primary BR | DEC-F4 |
|---|---|---|---|
| FR-ESC-01 | Escalate Case Cabang → Pusat with Escalation Package | BR-007 | F4.1 |
| FR-ESC-02 | Return Escalation (`return_reason_code` + `return_note`) | BR-007 A4/E6 | F4.4, F4.5 |
| FR-ESC-03 | Pusat handler work queue (escalated-only) | BR-007 | F4 |
| FR-RES-01 | Resolve Case (incl. Pusat path) | BR-008 | — |
| FR-RES-02 | Set `result_visibility` at Pusat Resolve | BR-008 | F4.2, F4.3 |
| FR-RES-03 | Change `result_visibility` after Resolve + audit | BR-008 A4 | F4.3a |
| FR-VIS-01 | Enforce search/list/get/export by visibility + org scope | BR-007/008 | F4…F4.3 |

## Must-include acceptance themes

1. No Regional escalate target under DEC-F4.  
2. No Information Lost on escalate and on return.  
3. Return rejected without code or note.  
4. Origin branch always reads after Pusat resolve.  
5. `ORIGIN_BRANCH` vs `ALL_BRANCHES` enforced on all read surfaces.  
6. Visibility change post-resolve audited.  
7. Return does not set `result_visibility`.

## Explicit non-goals (this outline)

- Batch 1 FR-001…FR-004 redesign  
- Customer Master write-back  
- Choosing SSO protocol (ADR-014 open questions)  
- Activating Regional escalate path (needs separate DEC)

## Drafting checklist

- [ ] DEC-F4 Architecture Board countersign  
- [ ] Map candidate FRs to UC / SCR / API-CM / EVT-CM IDs  
- [ ] Update RTM namespace for Escalation batch  
- [ ] Link `TC-CAT-CM-F4-001` (UAT-F4) as Planned TC set  
- [ ] OpenAPI + Event Catalog entries in same change as Draft FRD  

## Related

- `18 Architecture Governance/reviews/ECMP_DEC_F4_Escalation_Visibility_Return_v1.0.md`
- `26 Traceability/ECMP_IMPACT_DEC_F4_v1.0.md`
- `03 Functional Requirements/ECMP_FRD_Complaint_Management_Escalation_Resolution_v0.1.md` (**Draft FRD — use this**)
- `13 Test Strategy/ECMP_UAT_Catalog_DEC_F4_v1.0.md`
- `03 Functional Requirements/ECMP_FRD_Complaint_Management_Batch1_v1.1.md` (LOCKED — do not edit for DEC-F4)
