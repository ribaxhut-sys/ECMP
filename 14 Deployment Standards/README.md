# 14 Deployment Standards

| Field | Value |
|---|---|
| ID | DEP-000 |
| Version | 0.2 |
| Owner | DevOps Lead |
| Reviewer | Security / SRE |
| Approver | Architecture Board |
| Status | 🟢 Active (DEP-001 foundation SoT) |
| Last Review | 2026-07-30 |
| Next Review | 2027-01-30 |
| Task note | SECMIG-P6-005 |

## Purpose

Standar deployment ECMP: environment, configuration, promotion rules, rollback policy.
**Executable** deploy/startup steps live under [`../docs/deployment/`](../docs/deployment/)
(hub: [`../docs/deployment/README.md`](../docs/deployment/README.md)).

## Owner

- Document Owner: DevOps / Platform Lead
- Reviewers: Solution Architect, Tech Leads, Ops, Security

## Status

Approved baseline — `ECMP_Deployment_Standards_v0.1.md` (DEP-001) updated for
**foundation stack** (root `backend/` / `frontend/` / Compose). Slice paths under
`implementation/` are Historical.

## Contents

- [`ECMP_Deployment_Standards_v0.1.md`](./ECMP_Deployment_Standards_v0.1.md) (DEP-001) — **Active**
- [`ECMP_Production_Deployment_Checklist_v0.1.md`](./ECMP_Production_Deployment_Checklist_v0.1.md) (DEP-CHK-001) — **Historical** (Sprint-08); not for foundation cutover

## Documentation precedence (foundation cutover)

```text
REL-SEC-001  →  DEP-CHK-V1  →  START-CHK-001
```

| Order | ID | Path |
|---|---|---|
| 1 | REL-SEC-001 | [`../16 Release Management/ECMP_Release_Security_Gate_v1.0.md`](../16%20Release%20Management/ECMP_Release_Security_Gate_v1.0.md) |
| 2 | DEP-CHK-V1 | [`../docs/deployment-checklist.md`](../docs/deployment-checklist.md) |
| 3 | START-CHK-001 | [`../docs/deployment/STARTUP_CHECKLIST.md`](../docs/deployment/STARTUP_CHECKLIST.md) |

## Operator navigation

Release → Deployment → Startup → Security Operations → Backup/Restore/Recovery → Rollback  
See [`../docs/deployment/README.md`](../docs/deployment/README.md).

## Related

- [`../15 Operations Runbook/`](../15%20Operations%20Runbook/)
- [`../16 Release Management/`](../16%20Release%20Management/)
- [`../10 Security and Access Standards/`](../10%20Security%20and%20Access%20Standards/)
- [`../docs/deployment/`](../docs/deployment/)
