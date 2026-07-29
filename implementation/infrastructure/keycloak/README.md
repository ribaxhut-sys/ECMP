# ECMP Keycloak IdP baseline (SEC-MIG-001 Phase 1)

| Field | Value |
|---|---|
| Task | TASK-PLATFORM-SECMIG-P1-001 |
| Realm | `ecmp` |
| Image | `quay.io/keycloak/keycloak:26.2.5` (pinned) |
| Compose profile | `auth` |
| Host URL (DEV) | http://localhost:8180 |

## Purpose

Repository-managed Keycloak baseline for local/DEV. **Does not** wire ECMP application authentication (Phase 2).

## Layout

```text
keycloak/
├── README.md                 ← this file
├── import/
│   └── ecmp-realm.json       ← realm-as-code (imported on start)
└── scripts/
    └── validate-idp.ps1      ← smoke: discovery, JWKS, realm, clients/roles hints
```

## Start

From repository root (or any cwd — use `-f`):

```powershell
docker compose -f implementation/infrastructure/docker-compose.yml --profile auth up -d
```

Wait until `ecmp-keycloak` is healthy (or ~60–90s).

Admin console: http://localhost:8180/admin  
Default (local only): `admin` / `admin_local_only` — override via `implementation/infrastructure/.env` from `.env.example`.

## Default compose (no auth profile)

```powershell
docker compose -f implementation/infrastructure/docker-compose.yml up -d
```

Starts **PostgreSQL only**. Keycloak is not created. Existing DEV DB behaviour is unchanged.

## OIDC surfaces (after import)

| Endpoint | URL |
|---|---|
| Issuer | http://localhost:8180/realms/ecmp |
| Discovery | http://localhost:8180/realms/ecmp/.well-known/openid-configuration |
| JWKS | http://localhost:8180/realms/ecmp/protocol/openid-connect/certs |

## Clients (SEC-AUTH-001 §2.2)

| Client ID | Type | Notes |
|---|---|---|
| `ecmp-web` | Public + PKCE | Authorization Code; UI deferred (ADR-011) |
| `ecmp-api-docs` | Public + PKCE | Docs / Swagger login path |
| `ecmp-ci` | Confidential | client_credentials; secret in realm JSON (**local only**) |
| `ecmp-svc-core` | Confidential | Baseline `ecmp-svc-*` pattern |
| `ecmp-api` | Resource | Audience target `ecmp-api` (mapper) |

## Roles (realm)

`cs_agent`, `viewer` (SEC-RAM-001 slice) · `supervisor`, `handler` (Planned)

Access-token claim `roles[]` via client scope `ecmp-roles`. Audience `ecmp-api` via `ecmp-audience`.

## Reproducibility

Realm SoT is `import/ecmp-realm.json`. Compose does **not** persist a Keycloak data volume so a recreate re-imports from the repo.

```powershell
docker compose -f implementation/infrastructure/docker-compose.yml --profile auth down
docker compose -f implementation/infrastructure/docker-compose.yml --profile auth up -d
```

Postgres volume `ecmp_pgdata` is independent — auth down/up does not drop the app database when you do not pass `-v`. Avoid `down -v` unless you intend to wipe Postgres too.

## Validate

```powershell
powershell -File implementation/infrastructure/keycloak/scripts/validate-idp.ps1
```

## Out of scope (this baseline)

- ECMP `ECMP_AUTH_MODE` / JWT validation / JWKS consumption in app
- OpenAPI / CI JWT suites / SIT activation
- Wiring backend to Keycloak

See `15 Operations Runbook/ECMP_IdP_Administrator_Runbook_v1.0.md`.
