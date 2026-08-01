# Deployment Review Sign-off — Lab Operator (WP-05)

| Field | Value |
|---|---|
| Date | 2026-08-01 |
| Overall | **PASS (lab overlay)** with constraints |

| ID | Item | Result | Notes |
|---|---|---|---|
| D-01 | `docker-compose.prod.yml` | **PASS (lab)** | Caddy + localhost binds; **DEFER blind overwrite onto Batch-1** (WP-03) |
| D-02 | `deploy/Caddyfile` | **PASS (lab)** | `{$ECMP_DOMAIN}`; docs routes = W-S04 |
| D-03 | `backup-postgres.sh` | **PASS** | Lab dump to `backups/`; evidence exists |
| D-04 | `seed-lab-master-data.sql` | **PASS (lab-only)** | Must not run on non-lab without backup (R-04) |
| D-05 | `deploy/README.md` | **PASS** | Cutover/rollback lab documented |
| D-05b | Host/domain migration checklist | **PASS** | `Host_Domain_Migration_Checklist_20260731.md` + Full Lab Backup |
| D-06 | UFW out-of-git | **PASS** | Explicitly not in cherry-pick |
| D-07 | `behind 14` stance | **ACCEPTED (W-D07)** | No bulk merge/rebase; selective pick only |
| D-08 | Written sign-off | **PASS** | This document |

## Sign-off

| Role | Name | Date | Decision |
|---|---|---|---|
| Deploy Lead | Lab Operator (W-SOD-1) | 2026-08-01 | **PASS (lab)** |

Waiver W-D07: residual 14 remote commits un-forensicked — mitigated by ban on bulk merge (Phase 1).
