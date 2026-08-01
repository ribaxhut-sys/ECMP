# Deployment Package Verification — ECMP v1.2.0 candidate (re-run)

| Field | Value |
|---|---|
| ID | DEP-PKG-VER-v1.2.0-RERUN |
| Date | 2026-08-01 |
| Candidate | `v1.2.0-rc.1` |
| Verdict | **NOT PRODUCTION-DEPLOYABLE** (AuthN/OIDC incomplete) |

## Inventory delta

| Component | Result |
|---|---|
| `docker-compose.prod.yml` | Updated: `ACME_EMAIL` accepts `CADDY_ACME_EMAIL` fallback |
| `.env.prod.example` | Expanded to full production AuthN/OIDC template (placeholders; do-not-invent) |
| Host `.env.prod` | Hygiene updated (git-ignored); OIDC intentionally absent |
| Compose `config` | **FAIL** on missing `OIDC_JWKS_URL` (expected) |
| Validator `--require-production` | **FAIL** (5 AuthN issues) |
| Images `*:1.2.0-rc.1` | Present (lab) |

## Conclusion

Deployment package hygiene improved. Production deploy still blocked on real IdP configuration.
