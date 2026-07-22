# 14 Deployment Standards


| Field | Value |
|---|---|
| ID | DEP-000 |
| Version | 0.1 |
| Owner | DevOps Lead |
| Reviewer | Security / SRE |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Standar deployment ECMP: environment, CI/CD, configuration management, promotion rules.

## Owner
- Document Owner: DevOps / Platform Lead
- Reviewers: Solution Architect, Tech Leads, Ops, Security

## Status
Approved baseline — `ECMP_Deployment_Standards_v0.1.md` (DEP-001). SIT/UAT/PROD platform = open decision (dicatat jujur di dokumen).

## Contents
- `ECMP_Deployment_Standards_v0.1.md` (DEP-001)
- `ECMP_Production_Deployment_Checklist_v0.1.md` (DEP-CHK-001) — Sprint-08

## Minimum Contents (v1)
- [x] Environment topology — DEV + CI aktual; SIT/UAT/PROD open decision (DEP-001 §1)
- [x] CI/CD pipeline standard (DEP-001 §1 — `backend-ci.yml`)
- [x] Configuration & secrets handling (DEP-001 §2)
- [x] Promotion / approval gates (DEP-001 §3, terhubung REL-001)
- [x] Rollback strategy — alembic downgrade + redeploy (DEP-001 §4)
- [ ] Infrastructure baseline (menunggu keputusan platform SIT/UAT/PROD)
- [x] Observability requirements — `/health` + `/health/ready` + structured logging (Sprint-08)

## Template Sections
1. Environment Standards
2. Build & Deploy Pipeline
3. Config Management
4. Release Promotion Rules
5. Rollback & Recovery
6. Monitoring Hooks
7. Checklist

## Naming
`ECMP_Deployment_Standards_vX.Y.docx|md`

## Related
- `../15 Operations Runbook`
- `../16 Release Management`
- `../10 Security and Access Standards`
