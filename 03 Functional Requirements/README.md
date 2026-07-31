# 03 Functional Requirements

| Field | Value |
|---|---|
| ID | FRD-000 |
| Version | 0.3 |
| Owner | Business Analyst |
| Reviewer | QA / Architect |
| Approver | Business Owner |
| Status | 🟢 ECMF slice Approved; multi-domain Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Spesifikasi kebutuhan fungsional (FRD) per domain/modul ECMP.

## Current Artifacts
- [x] `ECMP_FRD_ECMF_v0.1.md` (FRD-001, versi terkini per metadata dokumen — **🟢 Approved**, Sprint-01 create/get)
- [x] `ECMP_Use_Cases_ECMF_v0.1.md` (UC-DOC-001 — UC-001 Create Case, UC-002 Get Case)
- [x] `ECMP_FRD_ECMF_Lifecycle_v0.1.md` (FRD-002 — 🟡 Draft; FR-003/FR-004)
- [x] `ECMP_FRD_CRM_Customer360_v0.1.md` (FRD-003 — 🟡 Draft; FR-010)
- [x] `ECMP_FRD_Notification_v0.1.md` (FRD-004 — 🟡 Draft; FR-020)
- [x] `ECMP_FRD_KPI_SLA_v0.1.md` (FRD-005 — 🟡 Draft; FR-030)
- [x] `ECMP_FRD_Dashboard_Queue_v0.1.md` (FRD-006 — 🟡 Draft; FR-040)
- [x] `ECMP_FRD_Administration_v0.1.md` (FRD-007 — 🟡 Draft; FR-050..FR-063: user/role/permission process, workflow/SLA/calendar/escalation/template/master-data/audit-config/settings, versioning + approval)
- [x] `ECMP_FRD_Complaint_Management_Batch1_v1.0.md` (FRD-CM-001 — Draft v1.0; superseded by v1.1)
- [x] `ECMP_FRD_Complaint_Management_Batch1_v1.1.md` (FRD-CM-001 — 🔒 **LOCKED**; Batch 1 SoT: FR-001…FR-004; CTO D-01…D-08; Claude Delta Review + CTO Approval complete; Case create deferred Batch 2)
- [x] `ECMP_FRD_Complaint_Management_Escalation_Resolution_Outline_v0.1.md` (FRD-CM-ESC-OUTLINE-001 — Outline; FR content superseded by Draft below)
- [x] `ECMP_FRD_Complaint_Management_Escalation_Resolution_v0.1.md` (FRD-CM-002 — 🟡 **Draft**; FR-CM-010…015; DEC-F4; API-520…526; EVT-CM-040…044)

> FRD Draft artifacts (FRD-002..007) **belum DoR**. FRD-CM-001 v1.1 is **LOCKED** as Complaint Aggregate Batch 1 SoT. Per **DEC-020** (Accepted): dual SoT under controlled coexistence — Aggregate intake uses `/api/v1/cm` (FRD-CM-001); foundation lifecycle remains `/api/v1/complaints`. Sprint delivery IDs MUST NOT be silently overwritten. **OQ-CM-B1-001 Closed**.
>
> **DEC-F4** (escalation visibility / return / result audience) is recorded under `18 Architecture Governance/reviews/ECMP_DEC_F4_Escalation_Visibility_Return_v1.0.md` and amends BR-CM-CAT-001 Draft BR-007/BR-008. It does **not** change FRD-CM-001 Batch 1; consume DEC-F4 in Batch 2+ FRD covering Escalation/Resolution.

## Planned
- [ ] FRD Core Platform
- [ ] FRD Complaint Management Batch 2+ (Case create, Assignment, SLA, Closure, Customer 360, dll.)
- [x] FRD-CM-002 Escalation & Resolution Draft (DEC-F4) — awaiting Architecture Board countersign for LOCK path

## Folder Status Note
**ECMF slice Approved; multi-domain Draft** (2026-07-21).

## Naming
`ECMP_FRD_<Domain>_vX.Y.md|docx`
