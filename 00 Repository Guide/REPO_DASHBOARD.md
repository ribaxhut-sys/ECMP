# Repository Health Dashboard

| Field | Value |
|---|---|
| ID | EAR-IDX-002 |
| Version | 1.1 |
| Owner | PMO / Enterprise Architecture |
| Reviewer | Architecture Board |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2026-08-21 |

## Overall Health
Use generated report as machine truth:

- Auto report: [`REPO_HEALTH_REPORT.md`](./REPO_HEALTH_REPORT.md)
- Run: `python tools/ear_repo_check.py --write-all`

Manual product maturity below remains for roadmap steering.

## Product Maturity (manual)

| Area | Maturity | Status | Notes |
|---|---|---|---|
| Business Blueprint | 85% | 🟢 Approved | v2.1 available |
| Glossary | 25% | 🟡 Draft | Starter terms exist |
| Templates | 50% | 🟢 Approved | Core templates ready |
| Repository Governance (00) | 90% | 🟡 Draft | Index/standards/automation |
| Traceability | 15% | 🟡 Draft | Matrix starter only |
| Solution Architecture | 5% | 🟡 Draft | Structure only |
| Reference Architecture | 10% | 🟡 Draft | Patterns starter |
| Domain Architecture | 10% | 🟡 Draft | Domain stubs |
| FRD | 0% | 🟡 Draft | Not started |
| Business Rules | 5% | 🟡 Draft | Folder ready |
| API Catalog | 10% | 🟡 Draft | OpenAPI starter + generator |
| Event Catalog | 20% | 🟡 Draft | events.yaml + generator |
| ADR | 10% | 🟡 Draft | Index generator ready |
| Security | 5% | 🟡 Draft | Folder ready |
| Test Strategy | 0% | 🟡 Draft | Not started |
| Deployment | 0% | 🟡 Draft | Not started |
| Operations Runbook | 0% | 🟡 Draft | Not started |
| Portal (MkDocs) | 30% | 🟡 Draft | Skeleton live |

## Domain Maturity (manual)

| Domain | Maturity | Bar |
|---|---|---|
| Core Platform | 15% | ███░░░░░░░ |
| CRM | 15% | ███░░░░░░░ |
| ECMF | 20% | ████░░░░░░ |
| Notification | 10% | ██░░░░░░░░ |
| Dashboard | 10% | ██░░░░░░░░ |
| KPI | 10% | ██░░░░░░░░ |
| Channel (boundary) | 5% | █░░░░░░░░░ |

## Progress Bars (text)

```text
Business Blueprint ...... █████████████████░  85%
Repository Governance ... ██████████████████  90%
Portal .................. ██████░░░░░░░░░░░░  30%
Glossary ................ █████░░░░░░░░░░░░░  25%
Event Catalog ........... ████░░░░░░░░░░░░░░  20%
Traceability ............ ███░░░░░░░░░░░░░░░  15%
API Catalog ............. ██░░░░░░░░░░░░░░░░  10%
FRD ..................... ░░░░░░░░░░░░░░░░░░   0%
Tests ................... ░░░░░░░░░░░░░░░░░░   0%
```

## Top Gaps (Priority)
1. Business Rules catalog
2. FRD ECMF
3. SLA/KPI matrix
4. Solution Architecture baseline
5. First real ADRs (auth, events, API style)

## Portal Direction
Target product: **ECMP Enterprise Architecture Portal**
Roadmap: `docs/portal-roadmap.md`
