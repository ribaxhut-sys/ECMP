# Deployment Review Sign-off Template (D-01…D-08 / R5)

| Field | Value |
|---|---|
| Date | 2026-07-31 |
| Status | **UNSIGNED — checklist for reviewer** |

| ID | Item | Result (PASS/FAIL/N/A) | Notes |
|---|---|---|---|
| D-01 | `docker-compose.prod.yml` overlay | | |
| D-02 | `deploy/Caddyfile` routing | | |
| D-03 | `deploy/backup-postgres.sh` | | |
| D-04 | `deploy/seed-lab-master-data.sql` lab-only impact | | |
| D-05 | `deploy/README.md` cutover/rollback lab | | |
| D-05b | Host/domain migration checklist reviewed (`Host_Domain_Migration_Checklist_20260731.md`) — lab will move FQDN/host later | | |
| D-06 | UFW host hardening out of Git — not assumed in pick | | |
| D-07 | Impact / stance on `behind 14` remote commits | | |
| D-08 | Written Deployment Review sign-off | | |

## Sign-off

| Role | Name | Date | Decision |
|---|---|---|---|
| Deploy Lead | _pending_ | | PASS / FAIL |
