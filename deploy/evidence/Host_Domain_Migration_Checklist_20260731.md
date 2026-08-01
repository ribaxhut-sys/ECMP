# Host / Domain Migration Checklist
Version: 1.0  
Date: 2026-07-31  
Class: Operations planning (WP-05 support)  
Status: DRAFT for Deploy Lead sign-off  

| Field | Value |
|---|---|
| Current lab host | VPS (Hostinger) — live foundation lab |
| Current lab domain | `pengaduan.layanankami.tech` |
| Assumption | Domain and/or server **will move** later |
| Not authorized here | Git promote · cherry-pick · production Aggregate cutover |
| Principle | Change **mechanism** (DNS, env, host) only — not Complaint domain behavior |

---

## Why this exists

Lab is intentionally temporary. Future move must be a **config + data + DNS** exercise, not a rewrite.

Already portable (do not regress):

| Concern | Mechanism |
|---|---|
| TLS site name | `ECMP_DOMAIN` → Caddy `{$ECMP_DOMAIN}` |
| ACME contact | `CADDY_ACME_EMAIL` |
| Browser CORS | `ALLOWED_ORIGINS` |
| Host allow-list | `ALLOWED_HOSTS` |
| Frontend API origin | `NEXT_PUBLIC_API_BASE_URL` (requires frontend **rebuild** after change) |
| App/data | Compose stack + Postgres volume/backup |

---

## Rules (immutable for this checklist)

1. **No hostname literals in new code/docs as the only source of truth** — env wins.  
2. **Secrets are per-host** — rotate JWT/DB passwords on new server; do not treat old `.env` as permanent.  
3. **Complaint Module behavior unchanged** by a move.  
4. **Batch-1 SoT / RAB / Phase 5 Git** are unrelated; this checklist does not authorize promote.  
5. **Identity/OIDC issuer** (when Mode B): update to real platform issuer — not invented on the new host without contract.

---

## A. Subdomain / domain change (same VPS)

Use when only DNS name changes (same IP).

| Step | Action | Owner | Done |
|---|---|---|---|
| A-01 | Choose new FQDN; document old → new | Deploy Lead | ☐ |
| A-02 | Create DNS **A** (and optional AAAA) → current VPS IP | DNS owner | ☐ |
| A-03 | Wait for propagation (`dig +short <NEW_DOMAIN> A`) | Deploy Lead | ☐ |
| A-04 | Update `.env`: `ECMP_DOMAIN`, `ALLOWED_ORIGINS`, `ALLOWED_HOSTS`, `NEXT_PUBLIC_API_BASE_URL`, `CADDY_ACME_EMAIL` if needed | Deploy Lead | ☐ |
| A-05 | Rebuild **frontend** image/build so `NEXT_PUBLIC_*` is baked in | Deploy Lead | ☐ |
| A-06 | Reload/restart Caddy + stack (`docker compose …`) | Deploy Lead | ☐ |
| A-07 | Smoke: `https://<NEW>/health`, `/login`, one API call | QA / Deploy | ☐ |
| A-08 | Keep old DNS temporarily (TTL-dependent) or remove after soak | DNS owner | ☐ |
| A-09 | Archive evidence: env key list (no secrets), dig output, smoke notes | Release Mgr | ☐ |

**Rollback A:** revert env to old FQDN, rebuild frontend, point DNS back, reload Caddy.

---

## B. New server (new VPS / new IP), same or new domain

| Step | Action | Owner | Done |
|---|---|---|---|
| B-01 | Provision host (Docker, ufw 80/443/SSH rate-limit, user `ecmp`) per `deploy/vps` guidance | Deploy Lead | ☐ |
| B-02 | Take **Postgres backup** on old host; verify checksum/size | Deploy Lead | ☐ |
| B-03 | Copy deploy artefacts only: compose, `deploy/Caddyfile`, scripts — **not** ad-hoc host-only hacks as SoT | Deploy Lead | ☐ |
| B-04 | Create **new** `.env` on new host (new secrets); set domain vars for target FQDN | Deploy Lead | ☐ |
| B-05 | Start stack **without** public DNS cutover first (optional: hosts-file or staging name) | Deploy Lead | ☐ |
| B-06 | Restore DB from B-02 backup; run migrate if required by that release’s runbook | Deploy Lead | ☐ |
| B-07 | Smoke on new host privately | QA / Deploy | ☐ |
| B-08 | DNS A/AAAA → **new** IP (lower TTL ahead of time if possible) | DNS owner | ☐ |
| B-09 | Public smoke on FQDN; monitor ACME/TLS | Deploy Lead | ☐ |
| B-10 | Decommission or freeze old host (do not dual-write DB) | Deploy Lead | ☐ |
| B-11 | Archive: backup id, new host id, DNS change time, smoke, rollback note | Release Mgr | ☐ |

**Rollback B:** DNS back to old IP; keep old stack read-only until soak ends. Do **not** restore old DB over new if writes already happened on new — escalate.

---

## C. Variable checklist (copy into new `.env`)

Fill target values; never commit secrets.

| Variable | Purpose | Old lab (reference) | New value |
|---|---|---|---|
| `ECMP_DOMAIN` | Public hostname | `pengaduan.layanankami.tech` | |
| `CADDY_ACME_EMAIL` | Let’s Encrypt | `admin@layanankami.tech` | |
| `ALLOWED_ORIGINS` | CORS | `https://pengaduan.layanankami.tech` | |
| `ALLOWED_HOSTS` | Host header allow | includes old FQDN | |
| `NEXT_PUBLIC_API_BASE_URL` | Browser → API | `https://pengaduan.layanankami.tech` | |
| `ENVIRONMENT` / `ECMP_AUTH_MODE` | Gate auth mode | per DEC-020 lab | per target policy |
| DB / JWT secrets | Per host | _do not copy blindly_ | **new** |

OIDC (`OIDC_ISSUER`, `OIDC_AUDIENCE`, `OIDC_JWKS_URL`) — only when Mode B / staging|production JWT gate applies; must match **real** IdP contract.

---

## D. What must stay portable (regression guard)

Before any edge/compose change in future picks, Deploy Lead confirms:

| Check | Pass? |
|---|---|
| Caddy site block still uses `{$ECMP_DOMAIN}` | ☐ |
| No new hard-coded lab FQDN required for boot | ☐ |
| Frontend public API URL comes from build-arg/env | ☐ |
| Backup/restore scripts take compose project/env as input | ☐ |
| Runbook steps say “set env” not “edit Caddy hostname by hand” | ☐ |

Fail any row → fix in deploy docs/templates **before** treating lab as migration-ready.

---

## E. Explicitly out of scope

- Rewriting Complaint Aggregate / Batch-1 domain  
- Building a multi-region platform or generic “migration SDK”  
- Silent cutover of live lab to Batch-1 without cutover DEC  
- Committing `.env` or real secrets into git  

---

## Sign-off (ties to WP-05)

| Role | Name | Date | Decision |
|---|---|---|---|
| Deploy Lead | _pending_ | | Approve checklist as lab migration baseline |
| Release Manager | _pending_ | | Acknowledge evidence path |

When signed, reference this file from Deployment Review (D-02/D-05) as **migration readiness note**.
