# RELEASE_INVENTORY.md — Mode A Batch-1 RC Documentation

| Field | Value |
|---|---|
| Document ID | REL-INV-MA-B1-001 |
| Date | 2026-08-01 |
| SHA context | `1608245` / `feature/cm-batch1-s2-persistence` |
| Approvals in this file | **None** |

Status legend: **Ready (doc)** = document exists and usable · **Pending human** = needs signature/decision · **Superseded** = historical · **Gap** = missing on tip

---

## A. RC preparation pack (this wave)

| Document | Purpose | Owner | Status | Approval Required |
|---|---|---|---|---|
| `RELEASE_MANIFEST.md` | Identity of repo/SHA/mode/refs | Release Doc Manager | Ready (doc) | No (informational) |
| `RELEASE_INVENTORY.md` | Catalogue of release docs | Release Doc Manager | Ready (doc) | No |
| `RELEASE_TRACEABILITY.md` | End-to-end trace map | Release Doc Manager / QA | Ready (doc) | No |
| `MISSING_APPROVALS.md` | Open approvals only | Release Doc Manager | Ready (doc) | No |
| `NEXT_HUMAN_ACTIONS.md` | Prioritized human work | TPM / RM | Ready (doc) | No |
| `RC_GATE_REPORT.md` | RC gate verdict | Release / Governance | Re-gated 2026-08-01 (`v1.1.0-rc.1` sync) | Freeze + tag |
| `REL_RC_001_Mode_A_Batch1_Assessment_20260801.md` | Filled assessment vs REL-RC-001 | Release Manager | Ready (doc) — NOT PASS | Yes — §5 TL/QA/RM |
| `Mode_A_Batch1_RC_Readiness_20260801.md` | Blocker snapshot | Release Manager | Ready (doc) | No |
| `Doc_Sync_Audit_Findings_20260801.md` | Sync findings | Auditor | Ready (doc) | No |
| `DEC_ID_Collision_Register_20260801.md` | DEC ID collision options | Board / PMO | Ready (doc) — OPEN | **Yes — Board** |
| `BOARD_DECISION_PACKAGE.md` | Board Decision Package (≤5 sections) | Governance Coordinator | Ready (doc) — meeting prep | Board votes elsewhere |
| `BOARD_DECISION_MATRIX.md` | Decision options / impact matrix | Board / PMO | Ready (doc) | **Yes — Board** |
| `BOARD_MEETING_AGENDA.md` | Meeting agenda | Board chair | Ready (doc) | Schedule = human |
| `BOARD_ACTION_REGISTER.md` | Post-meeting actions | PMO / owners | Ready (doc) — all open | Human due dates |
| `RC_FINAL_CHECKLIST.md` | RC cut checklist; approvals blank | Release Manager | Ready (doc) — empty sign-off | **Yes — after Board** |
| `EXECUTIVE_STATUS.md` | One-page status dashboard | Board / executives | Ready (doc) | No |

## B. Canonical release management templates

| Document | Purpose | Owner | Status | Approval Required |
|---|---|---|---|---|
| `16 Release Management/README.md` | Entry point | Release Manager | Ready (doc) | No |
| `ECMP_Release_Management_v0.1.md` | REL-001 process | Release Manager | Approved template | Per release |
| `ECMP_Repository_Versioning_Policy_v0.1.md` | REL-VER-001 | Release Manager | Approved | SemVer choice pending |
| `ECMP_Git_Tag_Convention_v0.1.md` | REL-TAG-001 | Release Manager | Approved | Tag path decision pending |
| `ECMP_RC_Release_Checklist_v0.1.md` | REL-RC-001 | Release Manager | Approved template | Yes for RC cut |
| `ECMP_Release_Security_Gate_v1.0.md` | REL-SEC-001 shared/prod | Security / RM | Approved | Out of scope for this lab RC claim |
| `ECMP_Release_Approval_Matrix_v1.0.md` | REL-APR-001 | PMO | Approved | Yes for promote beyond DEV RC |
| `ECMP_Release_Evidence_Template_v1.0.md` | REL-EVID-001 | Release Manager | Approved | As needed |
| `ECMP_R6-01_Release_Artifact_Provenance_v1.0.md` | Provenance | Release Manager | Approved | R6-01 run pending |

## C. Phase 4–5 / lab evidence (selected)

| Document | Purpose | Owner | Status | Approval Required |
|---|---|---|---|---|
| `Phase4_RAB_GO_WITH_WAIVERS_20260801.md` | Limited Phase 5 auth | RAB | Complete (lab W-SOD-1) | Done for Phase 5 limited only |
| `Phase4_RAB_NOGO_20260731.md` | Prior NO-GO | RAB | Superseded for limited scope | No |
| `RAB_Readiness_Memo_20260801.md` | Re-RAB motion | RM | Complete | No |
| `Approval_Matrix_Signoff_20260801.md` | A-01…A-10 | Lab roles | Complete (lab) | Done (lab); not enterprise SoD |
| `Security_Review_Signoff_20260801.md` | S-01…S-09 | Sec Reviewer | CONDITIONAL PASS lab | Delta review optional |
| `Deployment_Review_Signoff_20260801.md` | D-01…D-08 | Deploy Lead | PASS lab | No for RC doc pack |
| `Residual_Risk_Acceptance_20260801.md` | RR acceptance | Gov / PO | Signed lab | No |
| `Rollback_Pack_APPROVED_20260801.md` | Rollback | Deploy / RM | APPROVED | No |
| `Base_SHA_Lock_APPROVED_20260801.md` | Base `2bf779d` | TL / RM | APPROVED | No |
| `Split_Plans_VPS_Mixed_APPROVED_20260801.md` | Split / DEFER | TL | APPROVED | No |
| `Compat_Review_Batch1_20260801.md` | Overlap VPS↔Batch-1 | TL | Complete | No |
| `Phase5_Execution_Limited_20260801.md` | Limited execution record | RM | Complete | No |
| `Phase5_Release_Execution_Runbook_PREAPPROVED_20260731.md` | Runbook | RM | Preapproved | Follow scope |
| `Post_P5_Hardening_Pack_20260801.md` | Post-P5 | Engineering | Complete | No |
| `PACK_STATUS_20260801.md` | Pack status | RM | Complete | No |
| `README_Release_Preparation_Pack_20260731.md` | Pack index | RM | Complete | No |

## D. Mode A technical / gate evidence

| Document | Purpose | Owner | Status | Approval Required |
|---|---|---|---|---|
| `G2_Mini_Gate_Mode_A_20260801.md` | G2 EXITED | SA / TL | Complete | No |
| `G1_Exit_Verified_20260801.md` | G1 exit | SA | Complete | No |
| `Mode_A_SIT_SoT_Choice_20260801.md` | Dual-tree SIT | SA | Binding | No |
| `Sprint03_Residual_Mode_A_DoD_20260801.md` | FR-030/040 DEFER | SA / PO | Scoped | Optional PO countersign |
| `U5_Signoff_Checklist_20260801.md` | G0 + FRD-002 DoR | TL / SA / BO | **Pending human** | **Yes — blank** |
| `W-S03_Status_20260801.md` | Waiver hygiene | Sec / Ops | OPEN | Closure later |
| `W-S04_Caddy_Docs_Closed_20260801.md` | W-S04 close | Deploy | CLOSED | No |
| `Mode_B_Blocked_Pending_IdP_Contract_20260801.md` | Mode B blocked | SA / Sec | BLOCKED | Board to lift C-7 later |
| `Observability_Minimum_20260801.md` | Obs floor | Engineering | Accepted Mode A | No |
| `implementation/backend/REGRESSION_PACK_G2.md` | Regression pack | QA / TL | Adopted | Evidence recorded |
| `implementation/backend/DEV_RUNBOOK.md` | Dev ops path | Engineering | Ready | No |

## E. Gaps / not on tip

| Document | Purpose | Owner | Status | Approval Required |
|---|---|---|---|---|
| IMS-001 | Integrated management system | Governance | **Gap on tip** (on `main`) | RM confirm ABSENT port |
| Security Baseline Standard | SEC baseline | Security | **Gap on tip** (on `main`) | RM / Sec confirm |
| Mode A Batch-1 `CHANGELOG` RC section | SemVer notes | RM | **Missing** | Human SemVer choice |
| `docs/releases/` Batch-1 RC notes | Release notes | RM | **Missing** | After SemVer |

## F. Historical foundation releases (do not confuse with this RC)

| Document | Purpose | Status |
|---|---|---|
| `docs/releases/v1.0.0*.md`, `RC1_REPORT.md` | Foundation v1.0.0 line | Historical |
| `docs/releases/ROLLBACK_v1.0.0.md` | Foundation rollback | Historical |

---

## Duplicate / collision notes (documentation only)

| Issue | Handling |
|---|---|
| Two `DEC-020` files | Cite **path + title**; Board options in collision register |
| Two `DEC-021` files | Same |
| Phase4 NO-GO vs GO WITH WAIVERS | GO WITH WAIVERS supersedes for **limited** scope only |
| W-S04 in RAB waiver table vs closed evidence | Prefer closure evidence; do not rewrite RAB body |
