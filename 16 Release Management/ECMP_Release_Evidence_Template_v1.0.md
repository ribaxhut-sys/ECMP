# ECMP Release Evidence Template

| Field | Value |
|---|---|
| ID | REL-EVID-001 |
| Version | 1.0.0 |
| Date | 2026-07-30 |
| Owner | Release Manager |
| Status | 🟢 Active |
| Task | TASK-PLATFORM-SECMIG-P6-004 |

Copy this template for each shared/staging/UAT/production release or production upgrade.
Store completed packs in the ops evidence location (prefer **outside git** if paths or redacted logs are sensitive). Do not commit secrets.

Companion: [`ECMP_Release_Security_Gate_v1.0.md`](./ECMP_Release_Security_Gate_v1.0.md), [`ECMP_Release_Approval_Matrix_v1.0.md`](./ECMP_Release_Approval_Matrix_v1.0.md).

---

## 0. Release identity

| Field | Value |
|---|---|
| Product / line | ECMP foundation |
| Version / tag | |
| Git commit SHA | |
| Target environment | staging / UAT / production |
| Compose file | e.g. `docker-compose.prod.yml` |
| `IMAGE_TAG` / `APP_VERSION` | |
| Change ticket / release id | |
| Operator | |
| UTC window (start → end) | |

## 1. Configuration validator PASS

| Item | Value |
|---|---|
| Command | `python scripts/validate-production-config.py --env-file .env --require-production` |
| Result | PASS / FAIL |
| `ENVIRONMENT` | |
| `ECMP_AUTH_MODE` | |
| Redacted stdout attached? | Yes / No |
| `docker compose … config` | PASS / FAIL |

## 2. Security test PASS (Authorization + suite)

| Item | Value |
|---|---|
| Command | `cd backend` → `python scripts/run_security_tests.py -q` |
| Candidate SHA | |
| Result | PASS / FAIL |
| Notes / failed node ids | |
| Reference | `docs/deployment/SECURITY_TEST_SUITE.md` |

## 3. Authentication validation

| Item | Value |
|---|---|
| `ECMP_AUTH_MODE=jwt` confirmed | Yes / No |
| OIDC issuer/audience/JWKS set | Yes / No |
| Startup log `auth_mode` | |
| Login smoke | PASS / FAIL |
| Refresh smoke | PASS / FAIL |

## 4. Audit validation

| Item | Value |
|---|---|
| Platform `audit_logs` acknowledged | Yes / No |
| Timestamp column used | `created_at` |
| `audit_logs_legacy` in scope? | Yes / No / N/A |
| If yes, timestamp column | `occurred_at` |
| No destructive audit maintenance planned | Yes / No |
| Security Officer note | |

## 5. Backup evidence

| Item | Value |
|---|---|
| Procedure | OPS-BAK-001 |
| Dump path (ops-managed) | |
| Format | `-Fc` (binary-safe) / plain `.sql` |
| Binary-safe method used for `-Fc`? | Yes / N/A (plain SQL) |
| Dump watermark (UTC) | |

## 6. Checksum evidence

| Item | Value |
|---|---|
| Algorithm | SHA-256 |
| Hash | |
| Source | `$dump.sha256` / ticket |
| Verified match | Yes / No |

## 7. Recovery status

| Item | Value |
|---|---|
| OPS-RCV-001 status | PASS / FAIL / N/A (DEV RC only) |
| Shared-env drill id / date | |
| `/live` + `/ready` on drill or target | PASS / FAIL / skipped (document) |
| `audit_logs` max(`created_at`) recorded | Yes / No |
| Measured RTO (if drill) | |
| Honest RPO statement | time since last dump = … (not DEC-005 15m unless WAL exists) |
| Evidence pack path | e.g. ops folder or `15 Operations Runbook/evidence/…` |

## 8. Smoke result

| Check | Result |
|---|---|
| `GET /live` | PASS / FAIL |
| `GET /ready` | PASS / FAIL |
| Login / refresh | PASS / FAIL |
| Critical path (complaint create/get or agreed smoke set) | PASS / FAIL |
| No secrets in logs | PASS / FAIL |
| `/docs` 404 on staging/production | PASS / FAIL / N/A |

## 9. Rollback readiness

| Item | Value |
|---|---|
| Rollback doc | `docs/releases/ROLLBACK_v1.0.0.md` (or version-specific) |
| Prior known-good tag / image | |
| Pre-change DB dump available | Yes / No |
| App-only vs DB restore decision tree understood | Yes / No |
| Approvers for rollback type identified (REL-APR-001 §4) | Yes / No |

## 10. Gate scorecard summary

| Gate | PASS / FAIL / N/A |
|---|---|
| Configuration Validation | |
| Authentication Validation | |
| Authorization Validation | |
| Audit Validation | |
| Backup Validation | |
| Recovery Validation | |
| Smoke Validation | |
| **Overall (REL-SEC-001)** | **GO / NO-GO** |

## 11. Approvals (from REL-APR-001)

| Role | Name | Date (UTC) | Go / No-Go |
|---|---|---|---|
| Tech Lead | | | |
| Security Officer / Architect | | | |
| Operations Lead | | | |
| Release Manager | | | |

**Final decision:** GO / NO-GO  
**Release Manager:** __________________ date __________

## 12. Related links (fill as used)

- Deployment: `docs/deployment/PRODUCTION_DEPLOYMENT_GUIDE.md`
- Startup: `docs/deployment/STARTUP_CHECKLIST.md`
- Security ops: `15 Operations Runbook/ECMP_Security_Operations_Runbook_v1.0.md`
- Backup: `15 Operations Runbook/ECMP_Backup_Operations_Guide_v1.0.md`
- Restore: `15 Operations Runbook/ECMP_Restore_Verification_Procedure_v0.1.md`
- Recovery: `15 Operations Runbook/ECMP_Recovery_Validation_Checklist_v1.0.md`
- Rollback: `docs/releases/ROLLBACK_v1.0.0.md`
