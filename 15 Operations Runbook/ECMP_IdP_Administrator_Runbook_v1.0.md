# ECMP IdP Administrator Runbook v1.0

| Field | Value |
|---|---|
| ID | OPS-IDP-001 |
| Version | 1.0 |
| Owner | DevOps Lead / Security Architect |
| Reviewer | Tech Lead / SRE |
| Approver | Architecture Board |
| Status | 🟢 Active (local DEV baseline — SEC-MIG Phase 1) |
| Last Review | 2026-07-30 |
| Next Review | 2026-10-21 |
| Task | TASK-PLATFORM-SECMIG-P1-001 |

## 1. Purpose

Operational runbook for the **local/DEV Keycloak IdP baseline** introduced by SEC-MIG-001 Phase 1.

**Pack path note (Historical for production recovery):** Compose/realm assets live under `implementation/infrastructure/` (optional auth profile / local DEV IdP). This is **not** the foundation app tree and is **not** part of production ECMP disaster recovery. Production API ops use root `backend/` + security/backup runbooks (OPS-SEC-*, OPS-BAK-001, OPS-DR-001). Keycloak's own `/health/ready` on port 9000 is IdP-only — do not confuse with ECMP `/live` / `/ready`.

This runbook does **not** authorize shared SIT/UAT/PROD IdP operation (Phase 3+) or replace foundation jwt-mode production procedures (P6-001).

## 2. Inventory

| Component | Detail |
|---|---|
| Image (pinned) | `quay.io/keycloak/keycloak:26.2.5` |
| Compose file | `implementation/infrastructure/docker-compose.yml` |
| Profile | `auth` (optional) |
| Container | `ecmp-keycloak` |
| HTTP (host) | http://localhost:8180 |
| Management/health | http://localhost:9000/health/ready |
| Realm SoT | `implementation/infrastructure/keycloak/import/ecmp-realm.json` |
| Admin console | http://localhost:8180/admin |

Default bootstrap admin (local only): username `admin`, password `admin_local_only` (override via `implementation/infrastructure/.env`).

## 3. Start / stop

### 3.1 Start IdP (optional profile)

```powershell
docker compose -f implementation/infrastructure/docker-compose.yml --profile auth up -d
docker compose -f implementation/infrastructure/docker-compose.yml --profile auth ps
```

Expected: `ecmp-postgres` (always when compose starts postgres) and `ecmp-keycloak` (profile `auth`) healthy.

### 3.2 Start Postgres only (default)

```powershell
docker compose -f implementation/infrastructure/docker-compose.yml up -d
```

Keycloak must **not** start. Confirm:

```powershell
docker ps --filter name=ecmp-keycloak
```

(empty / no running container)

### 3.3 Stop IdP (keep Postgres)

```powershell
docker compose -f implementation/infrastructure/docker-compose.yml --profile auth stop keycloak
# or remove Keycloak container while leaving Postgres:
docker compose -f implementation/infrastructure/docker-compose.yml --profile auth rm -sf keycloak
```

### 3.4 Full profile down (preserve Postgres volume)

```powershell
docker compose -f implementation/infrastructure/docker-compose.yml --profile auth down
```

Do **not** use `down -v` unless you intentionally wipe `ecmp_pgdata`.

## 4. Realm import (repository-managed)

1. Edit `implementation/infrastructure/keycloak/import/ecmp-realm.json` in git.
2. Recreate Keycloak so `--import-realm` runs on a clean container filesystem:

```powershell
docker compose -f implementation/infrastructure/docker-compose.yml --profile auth up -d --force-recreate keycloak
```

3. Validate discovery/JWKS:

```powershell
powershell -File implementation/infrastructure/keycloak/scripts/validate-idp.ps1
```

**Note:** `--import-realm` typically skips re-import if the realm already exists in the container’s data. This baseline intentionally omits a Keycloak data volume so recreate → re-import from repo.

## 5. Realm export (promote console changes back to git)

If a change was made in the Admin UI for experiments, **export** and replace the repo file:

1. Admin Console → Realm `ecmp` → Realm settings → **Partial export** (or full export) including clients and roles.
2. Save as `implementation/infrastructure/keycloak/import/ecmp-realm.json`.
3. Diff carefully: strip environment-specific secrets before commit when moving beyond local DEV; keep LOCAL-ONLY placeholders for Phase 1 secrets.
4. PR review required — realm JSON is SoT.

Do not rely on unreproduced console-only state.

## 6. Baseline clients / roles (checklist)

### Clients

| Client | Expectation |
|---|---|
| `ecmp-web` | Public, PKCE (S256), Authorization Code |
| `ecmp-api-docs` | Public, PKCE (S256), Authorization Code |
| `ecmp-ci` | Confidential, service accounts, client_credentials |
| `ecmp-svc-core` | Confidential, service accounts — **`ecmp-svc-*` baseline** |
| `ecmp-api` | Audience resource (`aud=ecmp-api`) |

Additional `ecmp-svc-<domain>` clients are added only via realm-as-code revisions (not ad-hoc in shared envs).

### Realm roles

| Role | Source |
|---|---|
| `cs_agent` | SEC-RAM-001 / SEC-AUTH-001 |
| `viewer` | SEC-RAM-001 / SEC-AUTH-001 |
| `supervisor` | Planned (matrix) / SEC-AUTH-001 |
| `handler` | Planned (matrix) / SEC-AUTH-001 |

Permissions are **not** defined in Keycloak (ADR-008 — Core Platform SoT).

## 7. Health / diagnosis

| Check | Command / URL |
|---|---|
| Container health | `docker inspect --format "{{.State.Health.Status}}" ecmp-keycloak` |
| Ready | http://localhost:9000/health/ready |
| Discovery | http://localhost:8180/realms/ecmp/.well-known/openid-configuration |
| JWKS | http://localhost:8180/realms/ecmp/protocol/openid-connect/certs |

Common failures:

| Symptom | Likely cause | Mitigation |
|---|---|---|
| Port 8180 in use | Local process conflict | Stop conflicting process or change host port mapping in compose (document deviation) |
| Realm missing after start | Import path / JSON invalid | Check logs `docker logs ecmp-keycloak`; validate JSON; recreate container |
| Health never ready | Slow first start | Wait `start_period` (~90s); check logs |
| Admin login fails | Env override drift | Align with `.env.example` / recreate |

## 8. Security notes (DEV)

- Bootstrap admin and client secrets in realm JSON are **local-only placeholders**.
- Do not expose port 8180 on untrusted networks.
- Do not enable `auth` profile on shared SIT/UAT until Phase 3 gates and secret store are met (ADR-010 / SEC-MIG).
- Application must **not** be configured to trust this IdP until Phase 2 Board approval.

## 8.1 Application org-scope service bypass (SEC-MIG Phase 4)

When the API runs with `ECMP_AUTH_MODE=jwt`, `OrgUnitGuard` denies callers that lack a usable `orgUnitId` claim unless **both** of the following are configured and match:

| Variable | Purpose |
|---|---|
| `ECMP_ORG_SCOPE_SERVICE_SUBJECTS` | Comma-separated service-account subject UUIDs (`sub`). Machine identity allowlist. |
| `ECMP_ORG_SCOPE_SERVICE_ALLOWLIST` | Comma-separated internal role codes permitted to bypass the org claim (in addition to subject match). |

Rules of operation:

- Empty either variable → **default deny** for missing `orgUnitId` (role alone is insufficient).
- Do **not** place human user subjects in `ECMP_ORG_SCOPE_SERVICE_SUBJECTS`.
- Dev/lab (`ECMP_AUTH_MODE=dev`) leaves org-scope enforcement inactive; these vars have no effect there.
- See `.env.example` / `.env.production.example`.

## 9. Explicit non-goals

- Phase 2: `ECMP_AUTH_MODE`, JWKS validation in ECMP, OpenAPI/CI dual-mode
- Phase 3: shared environment activation
- Frontend OIDC login UI (ADR-011)
- Changing `backend/app` authentication

## Related

- `../implementation/infrastructure/keycloak/README.md`
- `../10 Security and Access Standards/ECMP_AuthN_Migration_Rollout_Plan_v1.0.md` (SEC-MIG-001)
- `../10 Security and Access Standards/ECMP_Target_Authentication_Architecture_v1.0.md` (SEC-AUTH-001)
- `../05 Architecture Decision Records/ECMP_ADR_012_Target_Authentication_Architecture_v1.0.md`
- `../18 Architecture Governance/BACKEND_MASTER_ROADMAP.md`
