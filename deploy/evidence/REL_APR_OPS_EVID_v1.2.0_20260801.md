# REL-APR-001 Operational Evidence Pack — v1.2.0 candidate

| Field | Value |
|---|---|
| ID | REL-APR-OPS-v1.2.0-20260801 |
| Matrix | `16 Release Management/ECMP_Release_Approval_Matrix_v1.0.md` |
| Date | 2026-08-01 |
| Candidate | `v1.2.0-rc.1` @ `6890f50` |
| Overall | **No-Go** (AuthN/config gates) |

## Evidence attached for approvers

| Topic | Artifact | Status |
|---|---|---|
| Config closure attempt | `PROD_CFG_CLOSURE_v1.2.0_20260801.md` | PARTIAL |
| Backup | `OPS_BAK_EVID_v1.2.0_20260801.md` | PASS (lab dump) |
| Recovery | `OPS_RCV_EVID_v1.2.0_20260801.md` | PASS lab docs / blocked jwt smoke |
| Security suite | pytest `-m security` @ candidate | PASS (169) |
| REL-SEC scorecard | `REL_SEC_001_v1.2.0_Assessment_20260801.md` | NO-GO |
| REL-EVID pack | `REL_EVID_001_v1.2.0_Evidence_Pack_20260801.md` | Updated |
| IdP contract | `Mode_B_Blocked_Pending_IdP_Contract_20260801.md` | BLOCKED |

## Required approver marks (production GO)

| Role | Go / No-Go | Rationale |
|---|---|---|
| Tech Lead | **No-Go** | Production AuthN stack not configurable without IdP contract |
| Security Officer / Architect | **No-Go** | REL-SEC Configuration + Authentication FAIL; inventing OIDC forbidden |
| Operations Lead | **Conditional evidence OK / Go blocked** | Backup dump sealed; recovery docs complete; cannot smoke jwt prod restore |
| Release Manager | **No-Go** | Process integrity: cannot declare GO with FAIL mandatory gates |

## Fake signatures

**Forbidden.** No external human decision ID supplied for production GO on this candidate.

## Next action for humans

Provide bilateral IdP contract (or Board decision that changes AuthN SoT). Until then, retain **NOT READY FOR RELEASE**.
