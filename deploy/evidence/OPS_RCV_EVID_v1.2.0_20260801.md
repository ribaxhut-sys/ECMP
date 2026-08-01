# OPS-RCV-001 / Recovery Evidence — ECMP v1.2.0 candidate

| Field | Value |
|---|---|
| ID | OPS-RCV-EVID-v1.2.0-20260801 |
| Procedures | OPS-RCV-001 + OPS-RST-001 |
| Date | 2026-08-01 |
| Candidate | `v1.2.0-rc.1` |
| Operator | Production Readiness Team (lab) |
| Result | **PASS (lab evidence complete)** / **NOT sufficient alone for prod GO** |

## 1. Prior shared-profile drill (still valid reference)

| Item | Value |
|---|---|
| Evidence | `15 Operations Runbook/evidence/restore-drill-20260730-shared/` |
| ID | OPS-RST-EVID-20260730-SHARED |
| Result | PASS (shared-profile; `/live` `/ready`; jwt profile; dual audit) |
| Explicit non-claim | Production cutover authorization **not** granted by that drill alone |

## 2. Candidate-bound backup for rollback package

| Item | Value |
|---|---|
| Dump evidence | `deploy/evidence/OPS_BAK_EVID_v1.2.0_20260801.md` |
| Artifact | `backups/ecmp_20260801T083202Z_v1.2.0-rc.1.dump` |
| SHA-256 | `31a4fa582f99d0e851fe4ae689dd36bae81fd43f39cfded65e714f1bb0457b6a` |
| Alembic | `0046_cm_case_management` |
| Rollback app path | `docs/releases/ROLLBACK_v1.0.0.md` + image pin `1.2.0-rc.1` |

## 3. Recovery readiness statement (honest)

| Criterion | Status |
|---|---|
| Known-good dump + checksum for candidate | **PASS** |
| Shared-profile restore drill on record | **PASS** (2026-07-30) |
| Remote dedicated SIT/UAT VM drill | **Not provisioned** |
| Production jwt AuthN stack restore smoke | **BLOCKED** — no bilateral IdP contract; cannot invent OIDC |
| Operations Lead window re-confirm for GO | **Pending** until AuthN gates close |

## 4. REL-SEC-001 §3.6 mapping

For **production cutover**: Recovery gate remains **FAIL / blocked** until AuthN production stack exists to execute restore+smoke under jwt.  
For **lab candidate evidence completeness**: dump + prior shared-profile drill + rollback docs = **documented**.

## Related

- `15 Operations Runbook/ECMP_Recovery_Validation_Checklist_v1.0.md`
- `deploy/evidence/Mode_B_Blocked_Pending_IdP_Contract_20260801.md`
