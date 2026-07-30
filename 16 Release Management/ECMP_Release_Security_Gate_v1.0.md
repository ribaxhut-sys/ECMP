# ECMP Release Security Gate

| Field | Value |
|---|---|
| ID | REL-SEC-001 |
| Version | 1.0.0 |
| Date | 2026-07-30 |
| Owner | Release Manager |
| Reviewer | Security Architect / Operations Lead / Tech Lead |
| Approver | PMO / Engineering Manager |
| Status | 🟢 Active |
| Task | TASK-PLATFORM-SECMIG-P6-004 |
| Stack | Foundation: root `backend/`, `frontend/`, repo-root Compose |

Documentation and release governance only. Does **not** change application code,
Compose, CI/CD workflows, or runtime behavior.

## 1. Purpose

Mandatory **Go / No-Go** security and operational gates for:

- Shared staging / UAT cutovers
- Production releases and production upgrades
- Any promotion that exposes the foundation stack beyond internal DEV-only RC

**Internal DEV RC** (`vX.Y.Z-rc.N` per REL-RC-001) may proceed with REL-RC-001 alone,
but **must not** claim shared/prod readiness until **all** gates below are PASS and
approvals in [`ECMP_Release_Approval_Matrix_v1.0.md`](./ECMP_Release_Approval_Matrix_v1.0.md)
are recorded.

Evidence is captured with [`ECMP_Release_Evidence_Template_v1.0.md`](./ECMP_Release_Evidence_Template_v1.0.md).

**After GO**, execute deploy checklists in order: **DEP-CHK-V1 → START-CHK-001**
([`../docs/deployment/README.md`](../docs/deployment/README.md)). Do not use Historical DEP-CHK-001 for foundation cutover.

## 2. Decision rule

| Outcome | Rule |
|---|---|
| **GO** | Every mandatory gate = **PASS**, evidence pack complete, all required approvers = Go |
| **NO-GO** | Any mandatory gate = **FAIL**, or any required approver = No-Go, or evidence incomplete |
| Conditional Go | **Forbidden** — no “Go with exceptions” without a new tagged candidate |

On NO-GO: fix-forward, re-run failed gates, cut a new evidence pack (and new RC/tag if source changed).

## 3. Mandatory gates

### 3.1 Configuration Validation

| | Criteria |
|---|---|
| **How** | `python scripts/validate-production-config.py --env-file .env --require-production` (staging/production). Companion: `docs/deployment/STARTUP_CHECKLIST.md`, P6-001. |
| **PASS** | Validator exits success; `ENVIRONMENT` staging/production; required AuthN/TLS/host vars present; Compose `config` valid for the target compose file. |
| **FAIL** | Validator non-zero, missing/weak secrets, AuthN mode invalid for environment, or Compose config invalid. |
| **NO-GO** | Any FAIL. Do not start or promote the release candidate. |

### 3.2 Authentication Validation

| | Criteria |
|---|---|
| **How** | Confirm `ECMP_AUTH_MODE=jwt` for staging/production; OIDC issuer/audience/JWKS set and reachable from backend network; startup log shows expected `auth_mode=jwt`; login + refresh smoke over HTTPS (or documented local shared-env URL). See P6-001 / Production Deployment Guide. |
| **PASS** | jwt mode enforced; OIDC endpoints configured; login/refresh succeed for a test principal; no fallback to `dev` mode. |
| **FAIL** | `dev` mode on shared/prod, missing OIDC, login/refresh broken, or startup AuthN guard failure. |
| **NO-GO** | Any FAIL. |

### 3.3 Authorization Validation

| | Criteria |
|---|---|
| **How** | From `backend/`: `python scripts/run_security_tests.py -q` (or `pytest -m security -q`) per `docs/deployment/SECURITY_TEST_SUITE.md`. Spot-check: unauthorized call → 403 `PERMISSION_DENIED`; bad Bearer → 401 `TOKEN_REJECTED` when HTTP smoke in suite runs. |
| **PASS** | Security-marked tests PASS on the release candidate SHA. |
| **FAIL** | Any security-marked test FAIL, or suite not executed / results not attached to evidence. |
| **NO-GO** | Any FAIL. |

### 3.4 Audit Validation

| | Criteria |
|---|---|
| **How** | Confirm platform table **`audit_logs`** is present and append-only policy understood (OPS-RST-001 / OPS-SEC-AUD-001). Pre-release: no tooling planned that UPDATE/DELETE `audit_logs` or **`audit_logs_legacy`**. Timestamp columns: `audit_logs.created_at`; legacy `audit_logs_legacy.occurred_at` only when explicitly in scope. |
| **PASS** | Schema/migration head includes platform audit; operators acknowledge dual-table rules; Security Officer (or delegate) confirms audit gate criteria for this release. |
| **FAIL** | Ambiguous table naming in runbook for this cut, planned destructive audit maintenance, or SO declines audit readiness. |
| **NO-GO** | Any FAIL. |

### 3.5 Backup Validation

| | Criteria |
|---|---|
| **How** | Pre-release / pre-upgrade dump per [`../15 Operations Runbook/ECMP_Backup_Operations_Guide_v1.0.md`](../15%20Operations%20Runbook/ECMP_Backup_Operations_Guide_v1.0.md) (OPS-BAK-001). Prefer `-Fc` via **binary-safe** container file + `docker compose cp` (never PowerShell `>` on `-Fc`). Record path, UTC watermark, SHA-256. |
| **PASS** | Dump artifact exists off-git; checksum file/ticket matches `Get-FileHash`; format recorded; sealed config/secret backup policy acknowledged. |
| **FAIL** | No dump, checksum mismatch, binary dump corrupted / produced via text redirect, or secrets committed. |
| **NO-GO** | Any FAIL for staging/production promotion or upgrade. |

### 3.6 Recovery Validation

| | Criteria |
|---|---|
| **How** | [`../15 Operations Runbook/ECMP_Recovery_Validation_Checklist_v1.0.md`](../15%20Operations%20Runbook/ECMP_Recovery_Validation_Checklist_v1.0.md) (OPS-RCV-001) + OPS-RST-001. |
| **PASS** | **Shared/staging/UAT/prod path:** shared-env restore drill PASS (or prior drill still valid per Operations Lead for this release window) including `/live` + `/ready`, `audit_logs` checks, measured RTO/RPO honesty statement. **Production upgrade of an already-live env:** restore drill status reviewed current; rollback package tested or previously proven for this line. |
| **FAIL** | No shared-env drill before first shared UAT; OPS-RCV incomplete; probes still documented as legacy `/health` only; RPO falsely claimed as 15m without WAL. |
| **NO-GO** | Any FAIL for shared UAT entry or production cutover. DEV-only RC may defer shared drill but must mark Recovery = **N/A (DEV RC)** and must not promote. |

### 3.7 Smoke Validation

| | Criteria |
|---|---|
| **How** | `GET /live` → 200; `GET /ready` → 200 with startup/database ok; post-deploy smoke from `docs/deployment/PRODUCTION_DEPLOYMENT_GUIDE.md` / `docs/deployment-checklist.md` (login, critical complaint path, no secret leakage in logs). |
| **PASS** | All required smokes PASS on the target environment after deploy/upgrade. |
| **FAIL** | Probe failure, auth smoke failure, critical path failure, or secrets in logs. |
| **NO-GO** | Any FAIL — execute rollback per approval matrix; do not declare release successful. |

## 4. Gate scorecard (copy into evidence)

| # | Gate | Result (PASS / FAIL / N/A) | NO-GO if FAIL? | Evidence ref |
|---|---|---|---|---|
| 1 | Configuration Validation | | Yes | |
| 2 | Authentication Validation | | Yes | |
| 3 | Authorization Validation | | Yes | |
| 4 | Audit Validation | | Yes | |
| 5 | Backup Validation | | Yes (shared/prod) | |
| 6 | Recovery Validation | | Yes (shared/prod) | |
| 7 | Smoke Validation | | Yes | |

**Overall:** GO / NO-GO

## 5. Related procedures (do not duplicate)

| Topic | Canonical doc |
|---|---|
| Approval sign-off | `./ECMP_Release_Approval_Matrix_v1.0.md` |
| Evidence pack | `./ECMP_Release_Evidence_Template_v1.0.md` |
| Deploy / startup | `../docs/deployment/` |
| Security ops | `../15 Operations Runbook/ECMP_Security_Operations_Runbook_v1.0.md` |
| Backup / restore / recovery | OPS-BAK-001, OPS-RST-001, OPS-RCV-001 |
| Rollback | `../docs/releases/ROLLBACK_v1.0.0.md` (+ OPS-RST for DB) |

## 6. Related

- `./ECMP_Release_Management_v0.1.md` (REL-001)
- `./ECMP_RC_Release_Checklist_v0.1.md` (REL-RC-001)
- `../docs/deployment/SECURITY_TEST_SUITE.md` (SEC-TEST-001)
