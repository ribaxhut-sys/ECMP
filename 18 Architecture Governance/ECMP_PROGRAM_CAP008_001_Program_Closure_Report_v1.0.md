# CAP-008 Program Closure Report

| Field | Value |
|---|---|
| Document ID | GOV-CAP008-CLOSE-001 |
| Title | CAP-008 Case Management Mode A — Program Closure Report |
| Version | 1.0 |
| Date | 2026-08-01 |
| Authority | Architecture Review Board |
| Status | 🔒 **CLOSED** |
| Capability | CAP-008 |
| Batch | Batch-2 Mode A |
| Index | `ECMP_PROGRAM_CAP008_000_Program_Closure_Index_v1.0.md` |

## 1. Program definition

Deliver Mode A **Case Management under Complaint Aggregate** (Create / Add / View / Update Status / Resolve / Close) for the Complaint Management Module, without unlocking Mode B or inventing Enterprise Platform contracts.

## 2. Entry conditions (met)

| Gate | Evidence |
|---|---|
| Business Lock READY | BCS CAP-008; DEC-MODEA-B2-001; BQ-001…014 LOCKED; Residual BQ ZERO |
| Board Unlock Mode A READY | DEC-MODEA-B2-001 APPROVED |
| BR-CM-CAT-001 LOCKED | `02 Business Rules/…` |
| FRD-CM-001 Batch-1 LOCKED | dual SoT DEC-020 coexistence |

## 3. Exit conditions (met for Mode A lab)

| Condition | Evidence |
|---|---|
| FRD-CM-B2-001 LOCKED | SoT Closure GOV-SOT-CAP008-001 |
| OpenAPI API-530…535 normative Implemented (lab) | `07 API Catalog/openapi/cm-case-management.v1.yaml` v1.0.0 |
| Implementation present | `backend/app/modules/cm_case/` (unchanged by this closure pack) |
| Lab RC PASS | REL-RC-001; tag `v1.2.0-rc.1` @ `6890f50` |
| Traceability | TRC-L-011…016 Approved |
| Capability Register | CAP-008 Implemented (lab) |

## 4. What this program closed

- CAP-008 Mode A **delivery program** (requirements → contract → lab RC → SoT sync → program closure pack)
- Documentation drift between RC-validated code and catalogs (SoT Closure Sprint)

## 5. What this program did **not** close

| Item | Status |
|---|---|
| Production cutover `v1.2.0` | NO-GO — external IdP/OIDC |
| Mode B | CLOSED by Board — not in program |
| Assignment / SLA / Notification engines | Out of CAP-008 Mode A scope |
| Formal EVT IDs / formal TC-catalog IDs | NOT SPECIFIED / deferred |
| Dual-SoT retirement | Requires separate Retirement DEC |

## 6. Chronology (repository evidence)

1. BQ Lock Pack DEC-MODEA-B2-001 — Residual BQ ZERO  
2. BCS CAP-008 BUSINESS LOCK READY  
3. FRD-CM-B2-001 authoring → Draft → **LOCKED** (SoT Closure)  
4. Implementation + Alembic `0046_cm_case_management`  
5. REL-RC-001 PASS → tag `v1.2.0-rc.1`  
6. SoT Closure Sprint (GOV-SOT-CAP008-001)  
7. This Program Closure pack (GOV-CAP008-CLOSE-*)

## 7. Disposition

**CAP-008 Mode A Program = CLOSED.**  
Follow-up engineering on CAP-008 FR body / OpenAPI / BR = **NONE** unless Board opens a new change request.  
Production promote and Mode B remain **outside** this closed program.

---

*End of GOV-CAP008-CLOSE-001.*
