# CAP-008 Repository Baseline

| Field | Value |
|---|---|
| Document ID | GOV-CAP008-CLOSE-006 |
| Version | 1.0 |
| Date | 2026-08-01 |
| Status | 🔒 **Frozen baseline** for CAP-008 Mode A |
| Authority | Architecture Review Board |
| RC tip | `v1.2.0-rc.1` @ `6890f50d8243ba30589a3d88f0c0efcef791ce01` |

## 1. Baseline meaning

Paths and document statuses that define CAP-008 Mode A **as closed**. Changing them requires a new Change Request / Board decision — not silent edits.

## 2. Knowledge SoT

| Artifact | Path | Baseline status |
|---|---|---|
| BCS | `docs/product/CAP-008_Case_Management_Business_Capability_Specification_v1.0.md` | BUSINESS LOCK READY |
| FRD | `03 Functional Requirements/ECMP_FRD_Case_Management_Batch2_v1.0.md` | 🔒 LOCKED |
| BR | `02 Business Rules/ECMP_Business_Rules_Complaint_Management_Module_v1.0.md` | Locked (unchanged by closure) |
| OpenAPI | `07 API Catalog/openapi/cm-case-management.v1.yaml` | v1.0.0 Implemented (lab) |
| Catalog index | `07 API Catalog/README.md` | API-530…535 Implemented (lab) |
| Capability Register | `01 Business Blueprint/ECMP_Capability_Register_v0.1.md` | CAP-008 Implemented (lab) |
| Traceability | `26 Traceability/traceability.yaml` | TRC-L-011…016 Approved |
| BQ Lock | `18 Architecture Governance/reviews/ECMP_DEC_ModeA_Delivery_Baseline_BQ_Lock_Pack_v1.0.md` | APPROVED · Residual ZERO |

## 3. Engineering trees (read-only for this program)

| Tree | Path | Note |
|---|---|---|
| Backend module | `backend/app/modules/cm_case/` | DEC-019 canonical |
| Tests | `backend/tests/test_cm_case_mode_a.py` | REL-RC-001 suite |
| Frontend | `frontend/src/features/cases/` | Mode A surfaces |
| Migration | Alembic `0046_cm_case_management` | RC evidence |

This Program Closure pack **does not modify** Backend, Frontend, or OpenAPI.

## 4. Evidence baseline

| Evidence | Path |
|---|---|
| REL-RC-001 | `deploy/evidence/REL_RC_001_CAP-008_Mode_A_Assessment_20260801.md` |
| SoT Closure | `deploy/evidence/CAP-008_SoT_Closure_20260801.md` |
| Program Closure Index | `18 Architecture Governance/ECMP_PROGRAM_CAP008_000_Program_Closure_Index_v1.0.md` |
| CHANGELOG | `[1.2.0-rc.1]` + Unreleased SoT/Program notes |

## 5. Non-baseline (explicit)

- Production `.env` / OIDC values  
- Mode B adapters  
- EVT Aggregate catalog IDs  
- Formal TC-catalog IDs beyond lab suite citation  

---

*End of GOV-CAP008-CLOSE-006.*
