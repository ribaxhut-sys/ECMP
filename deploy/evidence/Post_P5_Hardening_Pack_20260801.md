# Post-P5 Hardening Pack — 2026-08-01

| Field | Value |
|---|---|
| Branch | `chore/post-p5-hardening` |
| Base | `feature/cm-batch1-s2-persistence` @ `6bae8aa` (post PR #2) |
| Status | Ready for review |

## Priority order executed

| # | Item | Result |
|---|---|---|
| 1 | Review/merge PR #2 | **DONE** (already merged) |
| 2 | Close W-S04 Caddy docs | **DONE** — `deploy/Caddyfile` no longer proxies `/docs*` `/redoc*` `/openapi.json`; evidence `W-S04_Caddy_Docs_Closed_20260801.md` |
| 3 | Truth-repair CLAUDE + ADR refs | **DONE** — root `CLAUDE.md`; no competing ADR stubs (SoT ADR-014 v1.4 / ADR-015 v1.3 already Accepted w/ Conditions) |
| 4 | Frontend CI | **DONE** — `root-frontend-ci.yml` already present; trigger widened for `chore/**` + PR into `feature/**` |
| 5 | Rate-limit wire | **DEFER dual-wire** — annotate `rate_limit.py`; SoT uses `login_protection` on auth router |
| 6 | Mode B | **BLOCKED documented** — C-7; no invented IdP |
| 7 | Observability min + smoke | **DONE** — `deploy/smoke-lab.sh` + evidence; live edge smoke 2026-08-01: health 200, login 200, docs 404 |

## Live smoke (edge)

```
smoke_base=https://pengaduan.layanankami.tech
health_http=200
login_page_http=200
docs_http=404
smoke_ok
```

## Explicitly NOT done

- Mode B enablement / production IdP invent  
- DEFER overwrite of SoT paths from Mixed VPS  
- Full APM stack  
- Claiming Production/Enterprise Ready
