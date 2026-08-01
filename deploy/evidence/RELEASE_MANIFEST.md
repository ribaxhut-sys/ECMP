# RELEASE_MANIFEST.md — Mode A Batch-1 RC Documentation Pack

| Field | Value |
|---|---|
| Document ID | REL-MANIFEST-MA-B1-001 |
| Date | 2026-08-01 |
| Prepared by | Release Documentation Manager (lab) |
| Purpose | Freeze documentation identity for Mode A Batch-1 RC preparation |
| Approvals in this file | **None** — placeholders not used; humans sign elsewhere |
| Fabrication | Forbidden — no fake signatures / Go claims |

---

## Repository

| Item | Value |
|---|---|
| Repository | ECMP (workspace `/opt/ECMP`) |
| Remote (historical) | `https://github.com/ribaxhut-sys/ECMP.git` (per prior evidence) |
| Branch | `feature/cm-batch1-s2-persistence` |
| Full SHA | `16082454659d7f511e5296d0bd9531185766e6db` |
| Short SHA | `1608245` |
| Describe | `secmig-v1.0.0-14-g1608245` |
| RC SemVer | **`v1.1.0-rc.1`** (`EXT-HD-RC-MA-B1-20260801`) |
| Annotated RC tag | **CUT** `v1.1.0-rc.1` |
| Historical tags (context) | `v1.0.0-rc4`, `v1.0.0` (foundation line — not this RC) |

## Current Mode / Phase

| Item | Value |
|---|---|
| Mode | **Mode A** (Batch-1) |
| Mode B | **CLOSED** |
| Phase | Release Governance — RC documentation preparation |
| RC gate verdict | See `RC_GATE_REPORT.md` (re-gated this pass) |
| Phase 4 RAB (limited Phase 5) | **GO WITH WAIVERS** |
| Base SHA (RAB lock) | `2bf779d` (Phase 5 base; tip has advanced with docs/hardening) |

---

## Known Risks

| ID | Summary | Severity |
|---|---|---|
| DEC-ID | Duplicate DEC-020/021 — B-1 Option A recorded; BA-03 open | Medium |
| REL-TAG | B-2 Option B lab waiver recorded; tag not cut | Medium |
| W-SOD-1 | Single lab operator multi-role SoD | High (governance) |
| W-S03 | Prod env label + Mode A JWT | High (claim risk) |
| W-D07 | behind-14 unforensicked | High |
| Dual-tree | `backend/` vs `implementation/backend` SIT confusion | Medium |
| Impl-CI | `implementation/backend` excluded from `backend-ci.yml` | Medium |
| RTM-exec | Batch-1 RTM executed TC coverage historically 0% | Medium |
| IMS-gap | IMS-001 / Security Baseline absent on this tip (present on `main`) | Medium |
| Sec-drift | Security sign-off text vs post-P5 (W-S04 closed; `ECMP_AUTH_MODE` present) | Medium |

## Known Waivers

| ID | Status | Notes |
|---|---|---|
| W-SOD-1 | OPEN (disclosed) | Until second named reviewer |
| W-S03 | **OPEN** | Expires 2026-09-30 or Mode B contract |
| W-S04 | **CLOSED** (edge) | Closed by `W-S04_Caddy_Docs_Closed_20260801.md` — RAB register historically listed waiver; do not rewrite RAB body |
| W-S05 | OPEN (lab) | Single-node XFF trust |
| W-S07 | OPEN / DEFER promote | Users admin UI |
| W-D07 | OPEN | No bulk merge/rebase |
| W-EXEC-1 | Binding | Limited Phase 5 only |

---

## Evidence Pack

Index: `deploy/evidence/README_Release_Preparation_Pack_20260731.md`  
Status: `deploy/evidence/PACK_STATUS_20260801.md`

Primary gate / prep docs (this wave):

| Doc | Path |
|---|---|
| RC Gate Report | `deploy/evidence/RC_GATE_REPORT.md` |
| REL-RC-001 Assessment | `deploy/evidence/REL_RC_001_Mode_A_Batch1_Assessment_20260801.md` |
| RC Readiness | `deploy/evidence/Mode_A_Batch1_RC_Readiness_20260801.md` |
| Doc Sync Audit | `deploy/evidence/Doc_Sync_Audit_Findings_20260801.md` |
| DEC Collision | `deploy/evidence/DEC_ID_Collision_Register_20260801.md` |
| This Manifest | `deploy/evidence/RELEASE_MANIFEST.md` |
| Inventory | `deploy/evidence/RELEASE_INVENTORY.md` |
| Traceability | `deploy/evidence/RELEASE_TRACEABILITY.md` |
| Missing Approvals | `deploy/evidence/MISSING_APPROVALS.md` |
| Next Human Actions | `deploy/evidence/NEXT_HUMAN_ACTIONS.md` |
| Board Decision Package | `deploy/evidence/BOARD_DECISION_PACKAGE.md` |
| Board Decision Matrix | `deploy/evidence/BOARD_DECISION_MATRIX.md` |
| Board Meeting Agenda | `deploy/evidence/BOARD_MEETING_AGENDA.md` |
| Board Action Register | `deploy/evidence/BOARD_ACTION_REGISTER.md` |
| RC Final Checklist | `deploy/evidence/RC_FINAL_CHECKLIST.md` |
| Executive Status | `deploy/evidence/EXECUTIVE_STATUS.md` |

Core Phase 4–5 evidence (non-exhaustive): G2 exit, G1 exit, RAB GO WITH WAIVERS, Approval Matrix, Security/Deploy sign-offs, Residual Risk, Rollback APPROVED, Phase 5 limited, Post-P5, U5 checklist (unsigned), W-S03/W-S04 status, Mode B blocked, SIT SoT, Sprint-03 residual DoD.

---

## Release Documents (canonical templates)

| ID | Path |
|---|---|
| REL-001 | `16 Release Management/ECMP_Release_Management_v0.1.md` |
| REL-VER-001 | `16 Release Management/ECMP_Repository_Versioning_Policy_v0.1.md` |
| REL-TAG-001 | `16 Release Management/ECMP_Git_Tag_Convention_v0.1.md` |
| REL-RC-001 | `16 Release Management/ECMP_RC_Release_Checklist_v0.1.md` |
| REL-SEC-001 | `16 Release Management/ECMP_Release_Security_Gate_v1.0.md` |
| REL-APR-001 | `16 Release Management/ECMP_Release_Approval_Matrix_v1.0.md` |
| REL-EVID-001 | `16 Release Management/ECMP_Release_Evidence_Template_v1.0.md` |
| REL-R6-01 | `16 Release Management/ECMP_R6-01_Release_Artifact_Provenance_v1.0.md` |
| Folder README | `16 Release Management/README.md` |

---

## Referenced DEC (by file path — disambiguate ID collisions)

| File | Status (in file) | Role for Mode A Batch-1 RC |
|---|---|---|
| `DEC-006_Contract_Freeze_G1_Sprint02A_v1.0.md` | Accepted | G1 freeze; U-5 open |
| `DEC-019_Engineering_Foundation_Canonical_Trees_EPIC001_v1.0.md` | Accepted | Canonical trees |
| `DEC-020_Complaint_Implementation_SoT_Namespace_Remapping_v1.0.md` | Accepted | Dual SoT remapping |
| `DEC-020_Lab_Auth_Local_Then_SSO_Target_v1.0.md` | Accepted (ops) | Lab auth phasing — **ID collision** |
| `DEC-021_G2_Mini_Gate_Mode_A_v1.0.md` | Accepted (Mode A lab) | G2 exit — **ID collision** |
| `DEC-021_Organization_Hierarchy_Descendant_Scope_O06_v0.1.md` | Proposed | O-06 — **ID collision** |
| `DEC-022_Org_Restructure_Orphan_Remediation_O07_v0.1.md` | Proposed | O-07 |
| `DEC-002_Build_Authorization_G0_v1.0.md` | Accepted | G0 / U-5 prerequisite |

## Referenced ADR

| ADR | Role |
|---|---|
| ADR-006 | API versioning |
| ADR-007 / ADR-012 family | Auth model (Mode A path; Mode B not unlocked) |
| ADR-008 | RBAC SoT |
| ADR-009 + Addendum G2 | Outbox / broker deferral extended in-process |
| ADR-010 | Deployment platform baseline (context) |
| ADR-014 v1.4 | Enterprise module — Accepted with Conditions; Mode B CLOSED |
| ADR-015 v1.3 | Identity contract — Accepted with Conditions; Implementation Deferred |

## Referenced Standards / Policies

| Item | Path / note |
|---|---|
| Observability (Mode A floor) | `21 Technical Standards/ECMP_Observability_Standard_v0.1.md` + `Observability_Minimum_20260801.md` |
| Security lab posture | `Lab_Security_Posture_Temporary_Host_20260731.md` |
| SEC Baseline / IMS-001 | **Missing on this tip**; on `main` @ `57dfae8` |
| CLAUDE / constitution | Root `CLAUDE.md` (Mode A module boundaries) |

## Referenced Runbooks

| Item | Path |
|---|---|
| Phase 5 execution (preapproved) | `deploy/evidence/Phase5_Release_Execution_Runbook_PREAPPROVED_20260731.md` |
| Case-service DEV | `implementation/backend/DEV_RUNBOOK.md` |
| CM Batch-1 staging TTL | `15 Operations Runbook/ECMP_CM_Batch1_Staging_TTL_Cleanup_v0.1.md` |
| Deploy README / smoke | `deploy/README.md`, `deploy/smoke-lab.sh` |
| Rollback pack | `deploy/evidence/Rollback_Pack_APPROVED_20260801.md` |
| Historical prod rollback notes | `docs/releases/ROLLBACK_v1.0.0.md` (foundation — not this RC) |

## Referenced Checklists

| Item | Path |
|---|---|
| REL-RC-001 template | `16 Release Management/ECMP_RC_Release_Checklist_v0.1.md` |
| REL-RC-001 assessment (unsigned) | `deploy/evidence/REL_RC_001_Mode_A_Batch1_Assessment_20260801.md` |
| U-5 (unsigned) | `deploy/evidence/U5_Signoff_Checklist_20260801.md` |
| Approval Matrix A-01…A-10 | `deploy/evidence/Approval_Matrix_Signoff_20260801.md` |
| Host/domain migration | `deploy/evidence/Host_Domain_Migration_Checklist_20260731.md` |
| Full lab backup | `deploy/evidence/Full_Lab_Backup_Checklist_20260731.md` |
| DEP-CHK-V1 hub | `docs/deployment-checklist.md` |

---

## Explicit non-claims

- Not Production Enterprise Ready  
- Not Mode B complete  
- SemVer `v1.1.0-rc.1` recorded; tag not cut until freeze + explicit permission  
- See `RC_GATE_REPORT.md` for current gate verdict  
