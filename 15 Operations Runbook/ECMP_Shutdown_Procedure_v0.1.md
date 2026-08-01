# ECMP Shutdown Procedure

| Field | Value |
|---|---|
| ID | OPS-SHDN-001 |
| Version | 0.2 |
| Owner | Operations Lead |
| Reviewer | DevOps / Tech Lead Backend |
| Approver | Operations Lead |
| Status | 🟡 Draft |
| Last Review | 2026-07-30 |
| Next Review | 2027-01-21 |
| Related | OPS-RB-001, OPS-RST-001, DEP-001 |

Documented stop sequence for ECMP. **Canonical stack:** root Compose (`backend`, `frontend`, `postgres`). Shared SIT/UAT drain steps remain **Planned** where noted (ADR-010).

## 1. When to use

| Situation | Use this procedure |
|---|---|
| End of local development session | Yes — orderly stop |
| Before DB restore / schema recreate | Yes — stop writers first (OPS-RST-001) |
| Incident mitigation | Yes — stop app before infra surgery |
| Planned maintenance (shared/prod) | Yes — declare window; stop proxy traffic first when possible |

## 2. Order of shutdown (mandatory)

Stop **writers first**, then UI, then data store. Never stop PostgreSQL while the API still accepts traffic.

1. **backend** (API writers)
2. **frontend** (if running)
3. **Reverse proxy** (prod: caddy/nginx) — optional if already draining
4. **postgres** — only after no app holds connections

## 3. Foundation — local Compose

```powershell
# From repo root
docker compose stop frontend backend
# Confirm API down
curl.exe http://127.0.0.1:8000/ready
# Then database when intended
docker compose stop postgres
# or: docker compose down   # keeps volumes unless -v
```

Confirm: `docker compose ps` shows services stopped as intended.

**Warning:** `docker compose down -v` deletes volumes. DEV data may be disposable — **never** use `-v` on shared/production without incident-commander approval.

## 4. Foundation — production Compose

```powershell
docker compose -f docker-compose.prod.yml stop frontend backend
# Optional: leave caddy up for maintenance page, or stop after drain
docker compose -f docker-compose.prod.yml stop caddy
docker compose -f docker-compose.prod.yml stop postgres
```

Prefer declaring a maintenance window and draining edge traffic before stopping backend (section 7).

## 5. DEV — uvicorn without Compose

1. Find PID on port `8000`; prefer `Ctrl+C` in the uvicorn terminal.
2. Confirm connection refused on `/ready`.
3. Stop postgres via root compose (section 3) if it was started that way.

## 6. Historical / optional packs

| Pack | Path | Note |
|---|---|---|
| Slice case-service | `implementation/backend` | **Historical** — not production SEC-MIG path |
| IdP Keycloak | `implementation/infrastructure` `--profile auth` | Optional DEV IdP (OPS-IDP-001) |
| Developer Portal | `implementation/portal` `:8030` | Internal tooling (ADR-011) |

Stop these only if you started them; do not confuse with root `backend/`.

## 7. Planned — shared drain (ADR-010)

1. Declare maintenance / incident window; notify per OPS-RB-001 / OPS-SEC-RB-001.
2. Block new traffic at reverse proxy before stopping app processes.
3. Stop app replica(s), then database (or failover per OPS-DR-001).
4. Record wall-clock and in-flight write gap for reconciliation.

## 8. Verification checklist

| # | Check | Pass |
|---|---|---|
| 1 | API not accepting traffic | `/ready` connection refused or proxy maintenance |
| 2 | Frontend stopped if intended | Compose `ps` |
| 3 | Postgres stopped when intended | Compose `ps` |
| 4 | No orphan uvicorn on :8000 | Port clear |

## Related

- `./ECMP_Runbook_Slice_v0.1.md` (OPS-RB-001)
- `./ECMP_Security_Operations_Runbook_v1.0.md` (OPS-SEC-RB-001)
- `./ECMP_Restore_Verification_Procedure_v0.1.md` (OPS-RST-001)
- `../docs/deployment/PRODUCTION_DEPLOYMENT_GUIDE.md`
