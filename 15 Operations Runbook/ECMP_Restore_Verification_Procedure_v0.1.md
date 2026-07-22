# ECMP Restore Verification Procedure

| Field | Value |
|---|---|
| ID | OPS-RST-001 |
| Version | 0.2 |
| Owner | Operations Lead |
| Reviewer | DevOps Lead / Security Officer |
| Approver | Operations Lead |
| Status | 🟡 Draft — DEV scratch drill **PASS** (Sprint-09); shared-env drill still Planned |
| Last Review | 2026-07-22 |
| Related | OPS-DR-001, OPS-BAK-001, DEP-CHK-001, OPS-SHDN-001 |

Documentation + drill evidence. First **shared-environment** restore drill remains **required at least once before shared UAT** (OPS-DR-001 §7) after ADR-010 baseline activation. Sprint-09 executed a **DEV scratch** drill to prove dump/restore + `audit_log` checks (see §6).

## 1. Prerequisites

- Shared PostgreSQL with a known-good `pg_dump` (and WAL archive if PITR is in scope) — **or** disposable scratch Postgres 16 for DEV drills
- Application build/commit pinned and compatible with restored Alembic head
- Incident window / maintenance flag declared (shared env); for DEV scratch: stop local writers per OPS-SHDN-001 if an app is attached
- Access to run SQL verification queries and HTTP smoke tests (HTTP smoke mandatory on shared env)

## 2. Restore steps (outline)

1. Declare incident; stop application writers (prevent writes to inconsistent DB) — OPS-SHDN-001.
2. Provision or verify target PostgreSQL 16 instance.
3. Restore latest logical dump (`pg_restore` / `psql`).
4. If WAL archiving is active: replay to the recovery target timestamp.
5. Run `alembic current` — schema revision must match the application version to start.
6. **Verify `audit_log`** before opening traffic (see §3).
7. Start application.
8. Verify probes and smoke (see §4).
9. Open service; record any data gap for reconciliation.

## 3. `audit_log` verification (mandatory)

| Check | Pass criteria |
|---|---|
| Row count vs last backup note | Explain any delta; do not silently drop newer rows |
| `max(occurred_at)` | ≥ last known backup watermark (or documented gap) |
| Append-only integrity | No UPDATE/DELETE tooling run against `audit_log` during restore |

If a newer `audit_log` fragment can be salvaged (WAL/replica), **reconcile/attach** — do not discard (OPS-DR-001 §5).

## 4. Application verification checklist

| # | Check | Pass |
|---|---|---|
| 1 | `GET /health` → 200 `{status: ok}` | Liveness |
| 2 | `GET /health/ready` → 200 `{checks.database: ok}` | DB connectivity |
| 3 | Authenticated `POST /v1/cases` + `GET /v1/cases/{id}` | Create/get smoke |
| 4 | Optional: assign/status/list/timeline/notes | Lifecycle smoke |
| 5 | Logs are JSON; include request/correlation ids; no PII | Observability — OPS-LOG-001 |

## 5. Pre-activation drill checklist (shared env)

- [ ] Backup artifact identified and checksum recorded
- [ ] Restore into non-production scratch DB completed
- [ ] §3 audit checks signed off by Security Officer (or delegate)
- [ ] §4 probes and smoke signed off by Operations
- [ ] RTO wall-clock measured and compared to 4h target (DEC-005)
- [ ] Gaps / lessons filed; OPS-DR-001 status reviewed for graduation from Draft

## 6. Sprint-09 DEV scratch drill result (2026-07-22)

| Field | Value |
|---|---|
| Evidence pack | `./evidence/restore-drill-20260722/README.md` |
| Dump SHA-256 | `0BAFAD6D0D7380252E000054F7CC1E71F2F49E78D29C900ABC50450C7BF56AD5` |
| Result | **PASS** — SRC/DST `cases=1`, `audit_log=1`, identical `max(occurred_at)`, Alembic `0003` |
| HTTP smoke | Skipped (no app bound to scratch DBs); required on shared-env drill |
| Security Officer sign-off | Deferred to shared-env drill (synthetic data) |
| Follow-up | Re-run checklist §5 on ADR-010 shared Postgres before UAT entry |

Checklist status after Sprint-09:

- [x] Backup artifact identified and checksum recorded (DEV scratch)
- [x] Restore into non-production scratch DB completed (DEV scratch)
- [x] §3 audit checks verified for synthetic rows (Security Officer formal sign-off deferred)
- [ ] §4 probes and smoke signed off by Operations (shared env)
- [x] Wall-clock recorded (local ≈ 6s — not an RTO claim against DEC-005 4h)
- [x] Lessons: host `:5432` may be occupied; use alternate ports or docker-only networking for scratch drills

## Related

- `./ECMP_Backup_Strategy_v0.1.md`
- `./ECMP_DR_BCP_Plan_v0.1.md`
- `./ECMP_Shutdown_Procedure_v0.1.md` (OPS-SHDN-001)
- `./ECMP_Log_Inspection_Procedure_v0.1.md` (OPS-LOG-001)
- `./evidence/restore-drill-20260722/README.md`
- `../14 Deployment Standards/ECMP_Production_Deployment_Checklist_v0.1.md`
