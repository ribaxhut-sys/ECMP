# Production Configuration Closure Attempt — v1.2.0-rc.1

| Field | Value |
|---|---|
| ID | PROD-CFG-CLOSE-v1.2.0-20260801 |
| Date | 2026-08-01 |
| Candidate | `v1.2.0-rc.1` |
| Result | **PARTIAL** — non-AuthN hygiene closed; AuthN/OIDC **OPEN (hard block)** |

## What was closed (allowed)

| Item | Action |
|---|---|
| `ACME_EMAIL` vs `CADDY_ACME_EMAIL` | `docker-compose.prod.yml` accepts either; host `.env.prod` sets both |
| Email / reset URL | Host `.env.prod`: `EMAIL_PROVIDER=noop`; `PASSWORD_RESET_FRONTEND_BASE_URL` aligned to `https://$ECMP_DOMAIN` |
| Version pins | `APP_VERSION` / `IMAGE_TAG` → `1.2.0-rc.1` |
| Prod env template | `.env.prod.example` expanded to full production key set with **placeholder** OIDC and explicit do-not-invent rule |
| Validator issue count | Was **8** → now **5** (all remaining = AuthN/OIDC/local-credential) |

## What must NOT be closed by inventing values

| Item | SoT |
|---|---|
| `ECMP_AUTH_MODE=jwt` + real `OIDC_*` | Requires bilateral IdP contract — `Mode_B_Blocked_Pending_IdP_Contract_20260801.md` |
| Fabricated issuer to pass validator | **Forbidden** |
| W-S03 as production promote | Lab-only; **blocked for promote** |

## Current validator result (host `.env.prod`)

```text
Configuration validation: FAIL (5 issue(s))
1. ECMP_AUTH_MODE=dev forbidden when ENVIRONMENT=production
2. ECMP_LOCAL_CREDENTIAL_AUTH must be false in production
3. OIDC_ISSUER missing
4. OIDC_AUDIENCE missing
5. OIDC_JWKS_URL missing
```

## Current compose prod config

```text
docker compose -f docker-compose.prod.yml --env-file .env.prod config
→ FAIL: OIDC_JWKS_URL required (expected until real IdP values supplied)
ACME_EMAIL interpolation: resolved via CADDY_ACME_EMAIL fallback (closed)
```

## Unblock criteria (external)

1. Board / platform owner provides verified IdP contract (issuer, audience, JWKS).  
2. Set `ECMP_AUTH_MODE=jwt`, `ECMP_LOCAL_CREDENTIAL_AUTH=false`, `ECMP_ENV=shared`, real `OIDC_*`.  
3. Re-run validator + compose config + AuthN login/refresh smoke.  
4. Then re-score REL-SEC-001.
