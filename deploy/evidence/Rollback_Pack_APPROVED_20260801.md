# Rollback Pack — APPROVED (WP-06)

| Field | Value |
|---|---|
| Date | 2026-08-01 |
| Status | **APPROVED** |
| Constraint | No rewrite of VPS `main` / SoT history |

## Procedures

### R-01 Edge lab
Stop Caddy / use compose without prod overlay per `deploy/README.md` rollback section.

### R-02 Release branch
If Phase 5 starts: revert picks newest-first on **release branch only**; or close PR; or reset release branch tip to locked base `2bf779d` (never force-push SoT/`main`).

### R-03 Abort criteria
- Conflict on DEFER path without Tech Lead exception  
- Security/Deploy withdrawal  
- Seed without backup  
- Scope creep beyond ABSENT/infra + evidence  

### R-04 Seed
Backup via `deploy/backup-postgres.sh` before any seed apply.

### R-05 On-call
Lab Operator (single-node lab).

### R-06 Sign-off
Below.

## Reverse order (if picks occur)

Evidence/rate-limit new files → infra ABSENT → never “undo” by merging VPS `main`.

## Approval

| Role | Name | Date | Decision |
|---|---|---|---|
| Deploy Lead | Lab Operator | 2026-08-01 | **Approve** |
| Release Manager | Lab Operator (W-SOD-1) | 2026-08-01 | **Approve** |
