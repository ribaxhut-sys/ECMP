# ECMP Shutdown Procedure

| Field | Value |
|---|---|
| ID | OPS-SHDN-001 |
| Version | 0.1 |
| Owner | Operations Lead |
| Reviewer | DevOps / Tech Lead Backend |
| Approver | Operations Lead |
| Status | 🟡 Draft |
| Last Review | 2026-07-22 |
| Next Review | 2027-01-21 |
| Related | OPS-RB-001, OPS-RST-001, DEP-001 |

Documented stop sequence for ECMP services in scope today (**DEV lokal + CI**). Shared SIT/UAT/PROD steps remain **Planned** until ADR-010 baseline activation (after ADR-007 target auth).

## 1. When to use

| Situation | Use this procedure |
|---|---|
| End of local development session | Yes — orderly stop |
| Before DB restore / schema recreate | Yes — stop writers first (OPS-RST-001 §2) |
| Incident mitigation (corrupt writes, runaway process) | Yes — stop app before infra surgery |
| Planned maintenance window (shared env) | Planned — same order once SIT/UAT exists |

## 2. Order of shutdown (mandatory)

Stop **writers first**, then dependents, then data store. Never stop PostgreSQL while the case-service still accepts traffic.

1. **ecmp-case-service** (application writers)
2. **Developer Portal** (if running — IMP-PORTAL-001)
3. **PostgreSQL** (`ecmp-postgres`) — only after no app process holds connections

## 3. DEV — case-service

1. Identify the process listening on the API port (default `8000`):

```powershell
# PowerShell — find PID on port 8000
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue |
  Select-Object -ExpandProperty OwningProcess -Unique
```

2. Prefer graceful stop: in the terminal running uvicorn, press `Ctrl+C` and wait for process exit.
3. If the process does not exit within ~15s: stop the PID (`Stop-Process -Id <pid> -Force` on Windows; `kill <pid>` on Linux/macOS).
4. Confirm: `curl http://127.0.0.1:8000/health` fails (connection refused).

**Do not** leave a second uvicorn instance bound to the same port.

## 4. DEV — Developer Portal (optional)

If portal is running on `8030`:

1. `Ctrl+C` in the portal uvicorn terminal, or stop its PID.
2. Confirm: `curl http://127.0.0.1:8030/` fails (connection refused).

Portal is internal tooling — not a customer path (ADR-011).

## 5. DEV — PostgreSQL

Only after steps §3–§4:

```powershell
docker compose -f implementation/infrastructure/docker-compose.yml stop postgres
# or full tear-down (keeps named volume unless -v):
docker compose -f implementation/infrastructure/docker-compose.yml down
```

Confirm: `docker compose -f implementation/infrastructure/docker-compose.yml ps` shows postgres not running (or absent).

**Warning:** `docker compose ... down -v` deletes volume `ecmp_pgdata`. DEV data is disposable (OPS-BAK-001 / OPS-DR-001) — do **not** use `-v` on shared environments.

## 6. CI

CI containers are ephemeral. No operator shutdown — the workflow runner tears down the job environment. Do not adapt this runbook for GitHub Actions job cleanup.

## 7. Planned — shared SIT/UAT/PROD (ADR-010)

When shared env is active, extend this procedure with:

1. Declare maintenance / incident window; notify per OPS-RB-001 escalation matrix.
2. Drain or block new traffic (load balancer / reverse proxy) before stopping app processes.
3. Stop app replica(s), then database (or failover per OPS-DR-001).
4. Record wall-clock and any in-flight write gap for reconciliation.

Until then, treat §7 as **Planned** — do not invent orchestration scripts (TS-001 §7 / ADR-010).

## 8. Verification checklist

| # | Check | Pass |
|---|---|---|
| 1 | No process listening on API port | Connection refused on `/health` |
| 2 | Portal stopped (if it was running) | Connection refused on `:8030` |
| 3 | Postgres stopped when intended | `docker compose ... ps` clean |
| 4 | No orphan uvicorn after force-kill | Task list / `Get-Process` clear |

## Related

- `./ECMP_Runbook_Slice_v0.1.md` (OPS-RB-001) — inventory & incident playbooks
- `./ECMP_Restore_Verification_Procedure_v0.1.md` (OPS-RST-001) — stop writers before restore
- `../14 Deployment Standards/ECMP_Deployment_Standards_v0.1.md` (DEP-001)
