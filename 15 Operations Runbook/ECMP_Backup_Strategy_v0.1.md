# ECMP Backup Strategy

| Field | Value |
|---|---|
| ID | OPS-BAK-001 |
| Version | 0.1 |
| Owner | Operations Lead |
| Reviewer | DevOps Lead |
| Approver | Operations Lead |
| Status | 🟡 Draft / Planned (no automation in Sprint-08) |
| Last Review | 2026-07-22 |
| Related | OPS-DR-001, ADR-010, DEC-005 |

Documentation only. **Do not** implement backup cron jobs, WAL shipping scripts, or
storage automation in this sprint (ADR-010 / TS-001 §7 — no speculative platform build).

## 1. Scope

| Environment | Backup? | Rationale |
|---|---|---|
| DEV (local) | **No** | Synthetic/disposable data; recreate via compose + `alembic upgrade head` |
| CI | **No** | Ephemeral service container |
| SIT / UAT / PROD | **Yes (Planned)** | Activates with ADR-010 shared env |

## 2. Targets (when shared env exists)

Aligned with OPS-DR-001 / DEC-005:

| Mechanism | Purpose | Target |
|---|---|---|
| Daily `pg_dump` (logical) | Full recoverable snapshot | Entire `ecmp` database |
| Continuous WAL archiving | Point-in-time recovery | RPO ≤ **15 minutes** |
| Off-box storage | Survive VM loss | Separate from app VM |
| Retention / encryption | Compliance | Set at SIT/UAT activation review |

## 3. What must be protected

Priority order mirrors OPS-DR-001 §4:

1. PostgreSQL data (`cases`, `audit_log`, outbox, notes, notification log)
2. Application config/secrets (vault — not in image/repo)
3. Alembic revision alignment with restored schema

**`audit_log` is append-only (BR-CP-03 / BR-008)** — backups must not truncate history;
restore policy is in the Restore Verification Procedure.

## 4. Explicit non-goals (Sprint-08)

- No backup automation scripts in this repository
- No cloud storage / bucket provisioning
- No scheduled GitHub Actions backup jobs

## Related

- `./ECMP_DR_BCP_Plan_v0.1.md` (OPS-DR-001 §2)
- `./ECMP_Restore_Verification_Procedure_v0.1.md`
- `../14 Deployment Standards/ECMP_Production_Deployment_Checklist_v0.1.md`
