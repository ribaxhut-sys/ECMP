# Platform Readiness Review — ECMP v1.2.0 Production

| Field | Value |
|---|---|
| ID | PLAT-RDY-v1.2.0-PE-20260801 |
| Date | 2026-08-01 |
| Team | ECMP Platform Engineering |
| Candidate | `v1.2.0-rc.1` @ `6890f50` |
| Scope | Platform blockers only (no CAP-008 / BR / FRD / OpenAPI / product features) |
| Verdict | **PLATFORM NOT READY** |

## Mission scorecard

| # | Mission item | Result |
|---|---|---|
| 1 | Establish bilateral Identity Provider contract | **FAIL** — absent; Binding Profile SEC-BIND-OIDC-001 remains Draft; Mode B CLOSED (C-7) |
| 2 | Complete production OIDC configuration | **FAIL** — host `.env.prod` has no real `OIDC_*`; inventing forbidden |
| 3 | Validate production configuration | **FAIL** — 5 AuthN issues (`--require-production`) |
| 4 | Validate docker-compose production deployment | **FAIL** — `OIDC_AUDIENCE` / `OIDC_*` required vars missing |
| 5 | Complete production authentication smoke tests | **FAIL** — blocked without jwt + real IdP |
| 6 | Re-run production readiness review | **DONE** — this document |

## Live re-validation (2026-08-01)

### Host `.env.prod` (non-secret keys)

```text
ENVIRONMENT=production
ECMP_AUTH_MODE=dev
ECMP_ENV=local
ECMP_LOCAL_CREDENTIAL_AUTH=true
OIDC_* = absent
```

### Validator (force-load `.env.prod` into backend:1.2.0-rc.1)

```text
Configuration validation: FAIL (5 issue(s))
1. ECMP_AUTH_MODE=dev forbidden when ENVIRONMENT=production
2. ECMP_LOCAL_CREDENTIAL_AUTH forbidden in production
3. OIDC_ISSUER missing
4. OIDC_AUDIENCE missing
5. OIDC_JWKS_URL missing
```

### Compose

```text
docker compose -f docker-compose.prod.yml --env-file .env.prod config
→ FAIL: OIDC_AUDIENCE required (Set OIDC_AUDIENCE)
```

### Explicit non-actions (SoT)

- Did **not** invent bilateral IdP issuer / realm / JWKS
- Did **not** set fabricated `OIDC_*` to force PASS
- Did **not** modify CAP-008, Business Rules, FRD, OpenAPI, or product features
- Did **not** treat lab stack (`ecmp-*` Mode A) as production AuthN evidence

## Remaining platform blockers

1. Bilateral IdP contract from Enterprise Platform owner (issuer, audience, JWKS, claim catalog).  
2. Host production AuthN: `ECMP_AUTH_MODE=jwt`, `ECMP_LOCAL_CREDENTIAL_AUTH=false`, `ECMP_ENV=shared`, real `OIDC_*`.  
3. `docker compose … prod config` green under real OIDC vars.  
4. Production AuthN login/refresh (+ jwt recovery) smoke.  
5. REL-APR-001 / REL-SEC-001 Go marks after gates PASS.

## Unblock (external)

Provide verified IdP contract → configure `.env.prod` → re-run validator + compose + AuthN smoke → re-score REL-SEC-001.

## Decision

```text
PLATFORM NOT READY
```
