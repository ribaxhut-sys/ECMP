# ECMP Release Approval Matrix

| Field | Value |
|---|---|
| ID | REL-APR-001 |
| Version | 1.0.0 |
| Date | 2026-07-30 |
| Owner | Release Manager |
| Reviewer | Security Architect / Operations Lead / Tech Lead |
| Approver | PMO / Engineering Manager |
| Status | 🟢 Active |
| Task | TASK-PLATFORM-SECMIG-P6-004 |

Governance only — no runtime/CI/CD/application changes.

## 1. Purpose

Defines **who must sign** before a shared/staging/UAT/production release (or production upgrade) may be declared **GO** under [`ECMP_Release_Security_Gate_v1.0.md`](./ECMP_Release_Security_Gate_v1.0.md) (REL-SEC-001).

Internal DEV-only RC (REL-RC-001) retains its own Tech Lead / QA Lead / Release Manager table; it does **not** replace this matrix for shared/prod promotion.

## 2. Required approvers (shared / production)

| Role | Responsibility | Must approve for GO? |
|---|---|---|
| **Tech Lead** | Technical readiness: candidate SHA quality, catalog/contract awareness, AuthN/AuthZ smoke interpretation, rollback technical feasibility | **Yes** |
| **Security Officer / Security Architect** | Security gate integrity: configuration/AuthN/AuthZ/audit gates, secret handling, no audit-table abuse, security test evidence | **Yes** |
| **Operations Lead** | Operational readiness: backup artifact + checksum, recovery/OPS-RCV status, startup/smoke on target env, capacity to execute rollback | **Yes** |
| **Release Manager** | Process integrity: scope/version/tag, evidence pack complete, all gates scored, communication of GO/NO-GO, no conditional Go | **Yes** |

Optional (as needed):

| Role | When |
|---|---|
| Solution Architect | Schema-touching rollback, ADR/scope disputes, destructive DB restore beyond standard rollback package |
| QA Lead | Always welcome; required for REL-RC-001 internal RC; recommended for first shared UAT |
| Incident Commander | Live production incident rollback with DB restore (may be Operations Lead or designated on-call) |

## 3. Approval responsibilities (detail)

### 3.1 Tech Lead

- Confirms release candidate SHA and that REL-001 slice/quality expectations for the change set are met.
- Confirms Authentication + Authorization + Smoke gates are correctly interpreted (PASS/FAIL).
- Confirms rollback **package** exists and app-only rollback path is understood.
- **Does not** alone authorize production GO without Security and Operations.

### 3.2 Security Officer / Security Architect

- Confirms Configuration, Authentication, Authorization, and Audit gates PASS.
- Confirms security test evidence (`run_security_tests.py` / `-m security`) attached and trustworthy.
- Confirms sealed-secret / no-secret-in-git posture for this cut.
- For restore drills affecting audit tables: signs `audit_logs` (and `audit_logs_legacy` if in scope) integrity per OPS-RST / OPS-RCV.
- May issue **No-Go** on security residual risk even if tests are green (document reason).

### 3.3 Operations Lead

- Confirms Backup Validation (artifact path, checksum, OPS-BAK procedure).
- Confirms Recovery Validation status (OPS-RCV) appropriate to the environment.
- Confirms startup checklist / smoke execution on the target environment.
- Confirms on-call coverage for the release window and ability to execute rollback.
- For destructive DB restore: ensures incident commander approval is recorded before restore.

### 3.4 Release Manager

- Owns the evidence pack ([`ECMP_Release_Evidence_Template_v1.0.md`](./ECMP_Release_Evidence_Template_v1.0.md)).
- Ensures all four required roles have dated Go/No-Go marks.
- Publishes the decision; blocks tag promotion / cutover communication if any No-Go or incomplete evidence.
- Ensures CHANGELOG / release notes / tag convention satisfied (REL-VER / REL-TAG).

## 4. Rollback approval

| Rollback type | Approvers |
|---|---|
| Application-only (schema compatible) | Tech Lead + Release Manager; notify Operations Lead |
| Secret-only restore | Operations Lead + Security Officer (OPS-SEC-SEC-001); notify Release Manager |
| Database restore / destructive rollback | **Incident Commander** + Tech Lead + Solution Architect; **Security Officer** if `audit_logs` / `audit_logs_legacy` integrity at risk; Release Manager records decision |

Mechanics: `../docs/releases/ROLLBACK_v1.0.0.md`, OPS-RST-001, DEP-001 §4.

## 5. Sign-off table (copy into evidence)

| Role | Name | Date (UTC) | Go / No-Go | Notes |
|---|---|---|---|---|
| Tech Lead | | | | |
| Security Officer / Architect | | | | |
| Operations Lead | | | | |
| Release Manager | | | | |
| Solution Architect (if required) | | | | |

**Aggregate decision:** GO / NO-GO  
**Release Manager signature:** __________________

## 6. Related

- `./ECMP_Release_Security_Gate_v1.0.md` (REL-SEC-001)
- `./ECMP_Release_Evidence_Template_v1.0.md` (REL-EVID-001)
- `./ECMP_Release_Management_v0.1.md` (REL-001)
- `./ECMP_RC_Release_Checklist_v0.1.md` (REL-RC-001)
