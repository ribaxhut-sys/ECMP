# Architecture Review


| Field | Value |
|---|---|
| ID | AR-000 |
| Version | 0.1 |
| Owner | Architecture Board Chair |
| Reviewer | PMO |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Proses dan formulir review arsitektur ECMP. Bagian dari Governance (`18`), bukan folder terpisah.

## Contents
- Review checklist
- Architecture review form
- Exception request process
- Decision linkage ke ADR

## Templates
- `REVIEW_CHECKLIST.md`
- `ARCHITECTURE_REVIEW_FORM.md` (canonical copy also in `../../24 Templates/`)
- `EXCEPTION_REQUEST.md`

## Active decision / review packs
- Parent-folder Mode A lab COMPLETE evidence: [`../ECMP_PROGRAM_MODE_A_M3C_Module_Lab_COMPLETE_Evidence_Pack_v1.0.md`](../ECMP_PROGRAM_MODE_A_M3C_Module_Lab_COMPLETE_Evidence_Pack_v1.0.md) (GOV-MODEA-M3C-001) — lab/synthetic only; Mode B CLOSED
- Parent-folder audit addendum: [`../ECMP_AUDIT_ADDENDUM_Independent_Program_Audit_20260730_Fase0_v1.0.md`](../ECMP_AUDIT_ADDENDUM_Independent_Program_Audit_20260730_Fase0_v1.0.md) (AUDIT-ADD-20260730-F0) — Independent Program Audit 2026-07-30 Fase 0 / K-1 / K-2 remediated; Mode B CLOSED
- `ECMP_DEC_F4_Escalation_Visibility_Return_v1.0.md` (GOV-DEC-F4) — Cabang→Pusat path, HQ return, `result_visibility` (amends BR-007/BR-008 Draft; does **not** change LOCKED FRD-CM-001 Batch 1)
- `ECMP_DEC_F4_Architecture_Board_Countersign_Pack_v1.0.md` (GOV-CS-DEC-F4) — one-page Board sign-off
- Impact: `../../26 Traceability/ECMP_IMPACT_DEC_F4_v1.0.md` (GOV-IMPACT-DEC-F4)
- UAT: `../../13 Test Strategy/ECMP_UAT_Catalog_DEC_F4_v1.0.md` (TC-CAT-CM-F4-001)
- FRD Draft: `../../03 Functional Requirements/ECMP_FRD_Complaint_Management_Escalation_Resolution_v0.1.md` (FRD-CM-002)
- OpenAPI: `../../07 API Catalog/openapi/complaint-management-esc-res.v1.yaml`
- `ECMP_FRD_CM_001_v1.1_LOCKED_Release_Notes.md` — FRD-CM-001 Batch 1 LOCK
- `ECMP_ADR_014_Architecture_Review_v1.0.md` — ADR-014 review
- `ECMP_CM_Batch1_S3_Operational_Migrate_Gate_v1.0.md` (GOV-S3-CM-B1-MIG-001) — local Docker `ecmp` Alembic `0040→0043` + CM smoke
- `ECMP_CM_Batch1_S3_OPS01_Redeploy_Gate_v1.0.md` (GOV-S3-CM-B1-OPS01-001) — backend rebuild + HTTP CM smoke (supervisor) COMPLETE
- `ECMP_CM_Batch1_S3_Release_Exception_Pack_v1.0.md` (GOV-EX-CM-B1-S3-001 / EX-20260729-01) — Batch 1 residual exceptions **countersigned lab/synthetic-only**
- `ECMP_CM_Batch1_S3_OPS03_Customer_Provider_Stance_v1.0.md` (GOV-S3-CM-B1-OPS03-001) — CUSTOMER_PROVIDER=stub stance for lab/synthetic
- `ECMP_PLATFORM_TD_OPS_003_Admin_RBAC_Repair_v1.0.md` (GOV-PLATFORM-OPS-SEED-001) — ADMIN matrix repair (`0044`)
- `ECMP_PLATFORM_CI_COV_001_Coverage_Gate_v1.0.md` (GOV-PLATFORM-CI-COV-001) — restore CI coverage gate ≥90%
- `ECMP_ADR_012_Architecture_Board_Countersign_Pack_v1.0.md` (GOV-CS-ADR-012) — ADR-012 **Accepted** / Countersigned (TASK-PLATFORM-ADR012-ACCEPT-001 complete; no Keycloak/OIDC/JWT/code authorization)
- Backend Master Roadmap: `../BACKEND_MASTER_ROADMAP.md` (BMR-001)
