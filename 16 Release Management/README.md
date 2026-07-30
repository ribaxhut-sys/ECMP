# 16 Release Management

| Field | Value |
|---|---|
| ID | REL-000 |
| Version | 0.3 |
| Owner | Release Manager |
| Reviewer | QA / Ops / Security |
| Approver | PMO |
| Status | 🟢 Active (canonical release entry point) |
| Last Review | 2026-07-30 |
| Next Review | 2027-01-30 |
| Task | TASK-PLATFORM-SECMIG-P6-004 / P6-005 |

## Purpose

**Canonical entry point** for ECMP release governance: planning, security Go/No-Go,
approvals, evidence, tagging, and links to deployment / operations companions.

Application stack for foundation releases: root `backend/`, `frontend/`, repo-root Compose.

## Owner

- Document Owner: Release Manager / PMO
- Reviewers: QA Lead, Operations Lead, Security Architect, Tech Lead, Architecture

## Operator navigation (official)

```text
Release (this folder / REL-SEC-001)
  → Deployment (DEP-CHK-V1 + docs/deployment hub)
  → Startup (START-CHK-001)
  → Security Operations (OPS-SEC-*)
  → Backup / Restore / Recovery
  → Rollback (RBK-V1-001)
```

## Documentation precedence (foundation cutover)

```text
REL-SEC-001  →  DEP-CHK-V1  →  START-CHK-001
```

| Order | ID | Document |
|---|---|---|
| 1 | REL-SEC-001 | [`ECMP_Release_Security_Gate_v1.0.md`](./ECMP_Release_Security_Gate_v1.0.md) |
| 2 | DEP-CHK-V1 | [`../docs/deployment-checklist.md`](../docs/deployment-checklist.md) |
| 3 | START-CHK-001 | [`../docs/deployment/STARTUP_CHECKLIST.md`](../docs/deployment/STARTUP_CHECKLIST.md) |

**Do not** use Historical DEP-CHK-001
([`../14 Deployment Standards/ECMP_Production_Deployment_Checklist_v0.1.md`](../14%20Deployment%20Standards/ECMP_Production_Deployment_Checklist_v0.1.md))
for foundation production cutover.

Hub: [`../docs/deployment/README.md`](../docs/deployment/README.md).

## Start here (order)

1. **[`ECMP_Release_Management_v0.1.md`](./ECMP_Release_Management_v0.1.md)** (REL-001) — versioning, slice Go/No-Go, changelog, rollback decision overview  
2. **[`ECMP_Release_Security_Gate_v1.0.md`](./ECMP_Release_Security_Gate_v1.0.md)** (REL-SEC-001) — mandatory security/ops gates for shared/prod  
3. **[`ECMP_Release_Approval_Matrix_v1.0.md`](./ECMP_Release_Approval_Matrix_v1.0.md)** (REL-APR-001) — who must sign  
4. **[`ECMP_Release_Evidence_Template_v1.0.md`](./ECMP_Release_Evidence_Template_v1.0.md)** (REL-EVID-001) — evidence pack  
5. Tag / RC mechanics as needed (below)

## Contents

### Release security (SECMIG-P6-004) — Active

- [`ECMP_Release_Security_Gate_v1.0.md`](./ECMP_Release_Security_Gate_v1.0.md) (REL-SEC-001)
- [`ECMP_Release_Approval_Matrix_v1.0.md`](./ECMP_Release_Approval_Matrix_v1.0.md) (REL-APR-001)
- [`ECMP_Release_Evidence_Template_v1.0.md`](./ECMP_Release_Evidence_Template_v1.0.md) (REL-EVID-001)

### Core release mechanics

- [`ECMP_Release_Management_v0.1.md`](./ECMP_Release_Management_v0.1.md) (REL-001)
- [`ECMP_Repository_Versioning_Policy_v0.1.md`](./ECMP_Repository_Versioning_Policy_v0.1.md) (REL-VER-001)
- [`ECMP_Git_Tag_Convention_v0.1.md`](./ECMP_Git_Tag_Convention_v0.1.md) (REL-TAG-001)
- [`ECMP_RC_Release_Checklist_v0.1.md`](./ECMP_RC_Release_Checklist_v0.1.md) (REL-RC-001) — internal DEV RC only
- [`ECMP_R6-01_Release_Artifact_Provenance_v1.0.md`](./ECMP_R6-01_Release_Artifact_Provenance_v1.0.md) (REL-R6-01)

## Companion links (canonical ops / deploy)

| Topic | Path |
|---|---|
| Deployment hub | [`../docs/deployment/README.md`](../docs/deployment/README.md) |
| Deployment guide | [`../docs/deployment/PRODUCTION_DEPLOYMENT_GUIDE.md`](../docs/deployment/PRODUCTION_DEPLOYMENT_GUIDE.md) |
| Startup | [`../docs/deployment/STARTUP_CHECKLIST.md`](../docs/deployment/STARTUP_CHECKLIST.md) |
| Deployment checklist (v1) | [`../docs/deployment-checklist.md`](../docs/deployment-checklist.md) |
| Secure config (P6-001) | [`../docs/deployment/ENVIRONMENT_VARIABLE_REFERENCE.md`](../docs/deployment/ENVIRONMENT_VARIABLE_REFERENCE.md) |
| Security test suite | [`../docs/deployment/SECURITY_TEST_SUITE.md`](../docs/deployment/SECURITY_TEST_SUITE.md) |
| Security operations | [`../15 Operations Runbook/ECMP_Security_Operations_Runbook_v1.0.md`](../15%20Operations%20Runbook/ECMP_Security_Operations_Runbook_v1.0.md) |
| Backup | [`../15 Operations Runbook/ECMP_Backup_Operations_Guide_v1.0.md`](../15%20Operations%20Runbook/ECMP_Backup_Operations_Guide_v1.0.md) |
| Restore | [`../15 Operations Runbook/ECMP_Restore_Verification_Procedure_v0.1.md`](../15%20Operations%20Runbook/ECMP_Restore_Verification_Procedure_v0.1.md) |
| Recovery | [`../15 Operations Runbook/ECMP_Recovery_Validation_Checklist_v1.0.md`](../15%20Operations%20Runbook/ECMP_Recovery_Validation_Checklist_v1.0.md) |
| Rollback | [`../docs/releases/ROLLBACK_v1.0.0.md`](../docs/releases/ROLLBACK_v1.0.0.md) |
| Ops index | [`../15 Operations Runbook/README.md`](../15%20Operations%20Runbook/README.md) |
| Deployment standards | [`../14 Deployment Standards/`](../14%20Deployment%20Standards/) |

## Minimum contents (v1+)

- [x] Release cadence & freeze — slice/gate (REL-001)
- [x] Slice Go/No-Go (REL-001 §3) + internal RC checklist (REL-RC-001)
- [x] **Release Security Gate** for shared/prod (REL-SEC-001) — P6-004
- [x] **Approval matrix** Tech Lead / Security / Ops / Release Manager (REL-APR-001)
- [x] **Evidence template** (REL-EVID-001)
- [x] Rollback decision criteria (REL-001 §5 → DEP-001 / ROLLBACK / REL-APR)
- [x] Documentation precedence + hub links (P6-005)
- [x] Release notes/changelog + SemVer tags
- [ ] Stakeholder communication template (external consumers — when needed)
- [ ] Post-release verification cadence (shared env operationalization)

## Naming

`ECMP_Release_<Topic>_vX.Y.md`  
`ECMP_Release_Notes_<Version>.md`

## Related

- `../13 Test Strategy`
- `../14 Deployment Standards`
- `../15 Operations Runbook`
- `../docs/deployment/`
- `../docs/releases/`
