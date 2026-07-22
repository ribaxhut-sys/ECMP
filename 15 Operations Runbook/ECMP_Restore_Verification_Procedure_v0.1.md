# ECMP Restore Verification Procedure

| Field | Value |
|---|---|
| ID | OPS-RST-001 |
| Version | 0.1 |
| Owner | Operations Lead |
| Reviewer | DevOps Lead / Security Officer |
| Approver | Operations Lead |
| Status | 🟡 Draft / Planned (drill executes at SIT/UAT activation) |
| Last Review | 2026-07-22 |
| Related | OPS-DR-001, OPS-BAK-001, DEP-CHK-001 |

Documentation only. First live restore drill is **required at least once before UAT**
(OPS-DR-001 §7) after ADR-010 baseline activation — not during Sprint-08.

## 1. Prerequisites

- Shared PostgreSQL with a known-good `pg_dump` (and WAL archive if PITR is in scope)
- Application build/commit pinned and compatible with restored Alembic head
- Incident window / maintenance flag declared
- Access to run SQL verification queries and HTTP smoke tests

## 2. Restore steps (outline)

1. Declare incident; stop application writers (prevent writes to inconsistent DB).
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
| 5 | Logs are JSON; include request/correlation ids; no PII | Observability |

## 5. Pre-activation drill checklist (ready to run when SIT exists)

- [ ] Backup artifact identified and checksum recorded
- [ ] Restore into non-production scratch DB completed
- [ ] §3 audit checks signed off by Security Officer (or delegate)
- [ ] §4 probes and smoke signed off by Operations
- [ ] RTO wall-clock measured and compared to 4h target (DEC-005)
- [ ] Gaps / lessons filed; OPS-DR-001 status reviewed for graduation from Draft

## Related

- `./ECMP_Backup_Strategy_v0.1.md`
- `./ECMP_DR_BCP_Plan_v0.1.md`
- `../14 Deployment Standards/ECMP_Production_Deployment_Checklist_v0.1.md`
