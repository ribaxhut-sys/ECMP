# ECMP Deployment Documentation Hub

| Field | Value |
|---|---|
| ID | DEP-HUB-001 |
| Version | 1.0.0 |
| Date | 2026-07-30 |
| Status | 🟢 Active |
| Task | TASK-PLATFORM-SECMIG-P6-005 |
| Stack | Foundation: root `backend/`, `frontend/`, repo-root Compose |

**Canonical hub** for foundation secure configuration and deploy procedures.
Governance standards live in `14 Deployment Standards`.
Release Go/No-Go starts in `16 Release Management`.

## Operator navigation (official)

```text
Release (REL-SEC-001)
  → Deployment checklist (DEP-CHK-V1)
  → Startup checklist (START-CHK-001)
  → Security Operations (OPS-SEC-*)
  → Backup / Restore / Recovery (OPS-BAK / OPS-RST / OPS-RCV)
  → Rollback (RBK-V1-001)
```

| Step | Document | ID |
|---|---|---|
| 1. Release security gate | `16 Release Management/ECMP_Release_Security_Gate_v1.0.md` | REL-SEC-001 |
| 2. Production deploy checklist | [`../deployment-checklist.md`](../deployment-checklist.md) | DEP-CHK-V1 |
| 3. Startup / smoke | [`./STARTUP_CHECKLIST.md`](./STARTUP_CHECKLIST.md) | START-CHK-001 |
| 4. Security operations | `15 Operations Runbook/ECMP_Security_Operations_Runbook_v1.0.md` | OPS-SEC-RB-001 |
| 5. Backup | `15 Operations Runbook/ECMP_Backup_Operations_Guide_v1.0.md` | OPS-BAK-001 |
| 6. Restore | `15 Operations Runbook/ECMP_Restore_Verification_Procedure_v0.1.md` | OPS-RST-001 |
| 7. Recovery validation | `15 Operations Runbook/ECMP_Recovery_Validation_Checklist_v1.0.md` | OPS-RCV-001 |
| 8. Rollback | [`../releases/ROLLBACK_v1.0.0.md`](../releases/ROLLBACK_v1.0.0.md) | RBK-V1-001 |

## Documentation precedence (foundation cutover)

For **shared staging / UAT / production** cutovers on the foundation stack:

1. **REL-SEC-001** — mandatory Go/No-Go (all gates PASS + approvals + evidence)
2. **DEP-CHK-V1** — production deployment checklist (`docs/deployment-checklist.md`)
3. **START-CHK-001** — pre/post start validation (`STARTUP_CHECKLIST.md`)

**Do not** use the Sprint-08 legacy checklist
`14 Deployment Standards/ECMP_Production_Deployment_Checklist_v0.1.md`
(**DEP-CHK-001**, Historical) for foundation production cutover.

Internal DEV RC only: REL-RC-001 (does not authorize shared/prod).

## Canonical documents in this folder

| Topic | Document | ID |
|---|---|---|
| Production deploy guide | [`PRODUCTION_DEPLOYMENT_GUIDE.md`](./PRODUCTION_DEPLOYMENT_GUIDE.md) | DEP-GUIDE-001 |
| Secure configuration / env matrix (P6-001) | [`ENVIRONMENT_VARIABLE_REFERENCE.md`](./ENVIRONMENT_VARIABLE_REFERENCE.md) | ENV-REF-001 |
| Startup checklist | [`STARTUP_CHECKLIST.md`](./STARTUP_CHECKLIST.md) | START-CHK-001 |
| TLS / reverse proxy | [`TLS_REVERSE_PROXY.md`](./TLS_REVERSE_PROXY.md) | — |
| Upgrade | [`UPGRADE_PROCEDURE.md`](./UPGRADE_PROCEDURE.md) | UPG-001 |
| Operational security (P5-005) | [`OPERATIONAL_SECURITY.md`](./OPERATIONAL_SECURITY.md) | OPS-SEC-001 |
| Security test suite (gate evidence) | [`SECURITY_TEST_SUITE.md`](./SECURITY_TEST_SUITE.md) | — |

## Related indexes

- `14 Deployment Standards/README.md` — DEP-001 standards
- `15 Operations Runbook/README.md` — ops / security / backup
- `16 Release Management/README.md` — release entry
- [`../releases/`](../releases/) — version notes + rollback package
