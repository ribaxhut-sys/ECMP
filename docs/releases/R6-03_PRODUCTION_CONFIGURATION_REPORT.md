# R6-03 — Production Configuration & Environment Hardening Report

| Field | Value |
|---|---|
| ID | R6-03-RPT |
| Date | 2026-07-28 |
| Branch | `release/v1.0.0` |
| Baseline | `v1.0.0-rc4` |
| Scope | Configuration / environment / startup validation / Compose readiness |
| Explicitly unchanged | Identity, RBAC, Password Management, Queue, Complaint workflows |

---

## 1. Executive Summary

R6-03 hardens the foundation stack for production deployment without adding business features.

| Gate | Result |
|---|---|
| Environment variable inventory | **PASS** — classified matrix published |
| Startup fail-fast validation | **PASS** — structured Variable / Problem / Suggested fix |
| Config separation (dev/test/staging/prod) | **PASS** — `ENVIRONMENT=test` added; prod rejects localhost/HTTP/debug/logging email |
| Secret audit | **PASS** — no production secrets in tree; weak defaults blocked outside development |
| CORS & cookie hardening | **PASS** — documented + Secure/SameSite from settings |
| Docker production review | **PASS** — healthchecks, restart, dependency order reviewed |
| Deployment documentation | **PASS** — guide, env reference, startup checklist, upgrade, rollback |
| Smoke / unit validation | See §8–§9 |
| Application features modified | **None** (config/docs/compose comments only) |

**Redis:** Not part of the foundation stack (login lockout is in-memory). Documented as N/A — no fake Redis dependency invented.  
**Storage:** Configured via System Settings (`storage.provider`, `storage.root.path`), not process env — documented.

---

## 2. Environment Variable Matrix

Canonical table: [`../deployment/ENVIRONMENT_VARIABLE_REFERENCE.md`](../deployment/ENVIRONMENT_VARIABLE_REFERENCE.md) and root [`.env.example`](../../.env.example).

### Detection summary

| Category | Count / notes |
|---|---|
| Required (core) | `ENVIRONMENT`, Postgres set, `JWT_*`, `ALLOWED_ORIGINS`, `NEXT_PUBLIC_API_BASE_URL` (build), password-reset base URL |
| Optional | Ports, log level, login lockout tunables, `IMAGE_TAG`, provenance |
| Development Only | Weak JWT/DB defaults, localhost origins, `EMAIL_PROVIDER=logging`, `DEBUG=true` |
| Production Only | Strong secrets, https origins, `EMAIL_PROVIDER=noop`, `DEBUG=false` |
| Deprecated / unused | `REDIS_*`, legacy `ECMP_*` (implementation pack) |
| Duplicates | Root `ALLOWED_ORIGINS` vs legacy `ECMP_ALLOWED_ORIGINS` — production uses root |
| Conflicts | Reset URL must ∈ `ALLOWED_ORIGINS`; compose localhost defaults + `ENVIRONMENT=production` → refuse start |

---

## 3. Startup Validation Report

**Implementation:** `backend/app/core/config.py`

- `ConfigIssue` / `ConfigValidationError` — multi-issue fail-fast with Variable / Problem / Suggested fix
- `collect_runtime_config_issues()` — inventory helper
- Invoked from `backend/app/main.py` lifespan (unchanged call site)
- CLI: `python scripts/validate-production-config.py`

| Check | Dev/Test | Staging | Production |
|---|---|---|---|
| DB host/user/db/password present | structural | structural + strong password | structural + strong password |
| Redis config | N/A | N/A | N/A |
| JWT secret / algorithm / TTL | algorithm always | strong secret + HS256 | strong secret + HS256 |
| Storage env | N/A (System Settings) | N/A | N/A |
| Frontend origin (`ALLOWED_ORIGINS`) | localhost OK | no localhost / no `*` | https only, no localhost / no `*` |
| Production localhost | allowed | rejected | rejected |
| Required secrets | weak OK | rejected if weak | rejected if weak |
| `EMAIL_PROVIDER=logging` | allowed | rejected | rejected |
| Reset URL ↔ CORS alignment | not enforced | enforced | enforced |

---

## 4. Production Configuration Matrix

| Concern | Development | Test | Staging | Production |
|---|---|---|---|---|
| `ENVIRONMENT` | `development` | `test` | `staging` | `production` |
| Docs `/docs` | on | on | off | off |
| Refresh cookie `Secure` | false | false | true | true |
| SameSite | Lax | Lax | Lax | Lax |
| CORS localhost | allowed | allowed | forbidden | forbidden |
| CORS http:// | allowed | allowed | allowed (internal) | **https only** |
| JWT placeholder | allowed | allowed | forbidden | forbidden |
| Email | `logging` | `logging`/`noop` | `noop` | `noop` |
| TrustedHost middleware | off | off | on | on |

No development defaults are accepted when `ENVIRONMENT` is `staging` or `production`.

---

## 5. Secret Audit Summary

| Finding | Severity | Status |
|---|---|---|
| `.env` gitignored (`**/.env`, `.env.*`, exception `.env.example`) | Info | OK |
| `.env.example` contains placeholders only | Info | OK |
| Hardcoded JWT default `change-me-in-production` | Medium (dev only) | Mitigated — fail-fast outside development |
| Hardcoded Postgres default `ecmp` | Medium (dev only) | Mitigated — fail-fast + Compose `${:?}` |
| Compose requires `JWT_SECRET_KEY` / `POSTGRES_PASSWORD` | — | OK |
| Repository secrets in git history for `.env` | — | Not introduced by R6-03; ops must keep `.env` local |
| `PGADMIN_DEFAULT_PASSWORD` | Low | Validated when set outside development |
| Frontend build-time API URL | — | Required build-arg (R2-04) |

**No production secrets were added to the repository.**

---

## 6. Docker Review

| Item | Assessment |
|---|---|
| `docker-compose.yml` services | postgres, backend, frontend; pgAdmin under `tools` profile |
| Healthchecks | Postgres `pg_isready`; backend `/health`; frontend image HEALTHCHECK |
| Restart policy | `unless-stopped` on all core services |
| Volumes | `ecmp_pgdata` (and pgAdmin); no secret volumes |
| Networks | Compose default bridge; service DNS `postgres` |
| Image tags | `ecmp-*:${IMAGE_TAG:-latest}` — **pin `IMAGE_TAG` in production** |
| Environment injection | `${VAR:?}` for secrets; localhost CORS default documented as dev-only |
| Startup / dependency order | postgres healthy → backend healthy → frontend |
| Redis service | Absent by design |
| Rebuild optimization | Out of scope (per epic) |

---

## 7. Deployment Documentation Summary

| Document | Path |
|---|---|
| Production Deployment Guide | `docs/deployment/PRODUCTION_DEPLOYMENT_GUIDE.md` |
| Environment Variable Reference | `docs/deployment/ENVIRONMENT_VARIABLE_REFERENCE.md` |
| Startup Checklist | `docs/deployment/STARTUP_CHECKLIST.md` |
| Upgrade Procedure | `docs/deployment/UPGRADE_PROCEDURE.md` |
| Rollback Procedure | `docs/releases/ROLLBACK_v1.0.0.md` (existing, still valid) |
| Config CLI | `scripts/validate-production-config.py` |

---

## 8. Smoke Test Result

| Check | Result |
|---|---|
| `pytest tests/test_settings_guard.py` (container) | **PASS** 21/21 |
| `pytest tests/test_settings_guard.py tests/test_auth.py` | **PASS** 29/29 |
| `python scripts/validate-production-config.py --env-file .env` | **PASS** (`ENVIRONMENT=development`) |
| Production fail-fast (compose run with weak/localhost prod env) | **PASS** — startup aborted with structured issues (JWT, Postgres, origins, email) |
| `GET /health` | **PASS** — `status=ok`, `database=up`, `environment=development` |
| Frontend `GET /` (follow redirects) | **PASS** — HTTP 200 |
| Login + `/auth/me` (`golive_admin`) | **PASS** — access token issued |
| Refresh cookie attributes (development) | **PASS** — `HttpOnly`; `SameSite=Lax`; `Secure` absent (expected in development) |
| Full backend pytest in container | 986 passed / 7 failed — failures are catalog/`docker-compose.yml` path lookups (not mounted in image); not R6-03 regressions. CI runs these with full repo checkout. |

---

## 9. GitHub Actions Result

| Workflow | Result |
|---|---|
| Backend CI (last on `release/v1.0.0`, commit `b0bc692`) | **success** (pre-R6-03 baseline) |
| Frontend CI (same) | **success** |
| EAR Docs Governance (same) | **success** |
| R6-03 commit CI | **Pending push** — local equivalents above PASS; push will re-trigger Backend/Frontend CI |

---

## 10. Remaining Risks

| Risk | Severity | Mitigation / follow-up |
|---|---|---|
| TLS not terminated in Compose | Medium | Reverse proxy required for shared production (deferred intentionally) |
| `EMAIL_PROVIDER=noop` silences reset mail | Medium | SMTP provider is out of R6-03 scope (STOP list) |
| In-memory login lockout not shared across replicas | Medium | Acceptable for single-VM baseline; Redis/K8s out of scope |
| Floating `IMAGE_TAG=latest` if unset | Low | Documented — pin tags in production |
| Local attachment storage not highly available | Low | System Settings local provider; object store later |
| Legacy `implementation/` stack confusion | Low | Docs state root stack is production path |
| CI not yet re-run on R6-03 commit | Low | Push `release/v1.0.0` to confirm Actions green |

---

## STOP

R6-03 complete. Do **not** proceed to SMTP, observability, K8s, or R6-04 in this change set.
