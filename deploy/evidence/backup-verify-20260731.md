# Backup verify — 2026-07-31

- Script: `deploy/backup-postgres.sh`
- Sample: `backups/ecmp_20260731T075156Z.sql.gz` — `gzip -t` PASS
- Fresh dump after Users/Reports work: see latest `backups/ecmp_*.sql.gz`
- Restore drill (full DB replace) not executed on live lab to avoid downtime; integrity check only.
