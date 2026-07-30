# ECMP Startup Checklist (R6-03)

| Field | Value |
|---|---|
| ID | START-CHK-001 |
| Version | 1.2.0 |
| Date | 2026-07-30 |
| Status | 🟢 Active |
| Task note | SECMIG-P6-005 — third step in foundation cutover precedence |

## Precedence

Foundation shared/prod cutover order: **REL-SEC-001 → DEP-CHK-V1 → START-CHK-001**.

- Gate: [`../../16 Release Management/ECMP_Release_Security_Gate_v1.0.md`](../../16%20Release%20Management/ECMP_Release_Security_Gate_v1.0.md)
- Deploy checklist: [`../deployment-checklist.md`](../deployment-checklist.md)
- Hub: [`./README.md`](./README.md)

## Before `docker compose up`

- [ ] `.env` present and **not** committed
- [ ] `python scripts/validate-production-config.py --env-file .env` → PASS
- [ ] For production: `--require-production` → PASS
- [ ] `ENVIRONMENT=staging` or `production` ⇒ `ECMP_AUTH_MODE=jwt` (SECMIG-P6-001)
- [ ] `ECMP_ENV=shared` for shared/staging/production deployments
- [ ] `OIDC_ISSUER` / `OIDC_AUDIENCE` / `OIDC_JWKS_URL` set and reachable from backend network
- [ ] `JWT_SECRET_KEY` rotated / vault-injected (≥32 chars; retained for dual-mode tooling)
- [ ] `POSTGRES_PASSWORD` strong
- [ ] `ALLOWED_ORIGINS` matches real frontend origin(s)
- [ ] `PASSWORD_RESET_FRONTEND_BASE_URL` equals one allowed origin
- [ ] `EMAIL_PROVIDER=noop` (staging/production) until SMTP exists
- [ ] `NEXT_PUBLIC_API_BASE_URL` set for image build (`https://ECMP_DOMAIN` in prod)
- [ ] `ECMP_DOMAIN` / `ACME_EMAIL` set for production TLS compose
- [ ] `ALLOWED_HOSTS` includes public hostname and `backend`
- [ ] `FORWARDED_ALLOW_IPS` set for proxy trust (`*` in prod compose)
- [ ] `TRUST_FORWARDED_CLIENT_IP` left `false` unless app-level XFF is required (P5-005)
- [ ] `IMAGE_TAG` pinned (not floating `latest`) for production
- [ ] Pre-deploy DB backup completed (upgrades)
- [ ] `docker compose -f docker-compose.prod.yml config` → valid (production)

## After start

- [ ] `docker compose -f docker-compose.prod.yml ps` — caddy / postgres / backend / frontend running
- [ ] Host ports **80/443 only** (no published 3000/8000/5432 on prod compose)
- [ ] `GET https://<ECMP_DOMAIN>/live` → 200
- [ ] `GET https://<ECMP_DOMAIN>/ready` → 200 (`checks.startup=ok`, `checks.database=ok`)
- [ ] HTTP → HTTPS redirect verified
- [ ] `Strict-Transport-Security` present on HTTPS responses
- [ ] App security headers present (`X-Content-Type-Options`, CSP, etc.)
- [ ] Backend logs show `application started` with expected `ENVIRONMENT` and `auth_mode=jwt`
- [ ] No `Configuration validation failed` in backend logs
- [ ] Frontend HTTPS 200 on `/`
- [ ] `/docs` returns 404 when `ENVIRONMENT` is staging/production
- [ ] Login sets refresh cookie (`HttpOnly`; `Secure` outside development)
- [ ] Refresh + logout succeed

## Fail-fast triage

| Symptom | Likely variable | Fix |
|---|---|---|
| Container exit; AuthN mode message | `ECMP_AUTH_MODE` | Set `ECMP_AUTH_MODE=jwt` for staging/production |
| Container exit; OIDC message | `OIDC_ISSUER` / `AUDIENCE` / `JWKS_URL` | Fill IdP endpoints in `.env` |
| Compose refuses AuthN vars | missing `${:?}` values | Copy from `.env.production.example` |
| Container exit on start; JWT message | `JWT_SECRET_KEY` | Strong ≥32 char secret |
| Postgres password rejected | `POSTGRES_PASSWORD` | Non-default strong password |
| Localhost origin rejected | `ALLOWED_ORIGINS` | Public https origin |
| Reset URL rejected | `PASSWORD_RESET_FRONTEND_BASE_URL` | Align with CORS origin |
| Email provider rejected | `EMAIL_PROVIDER` | Use `noop` outside development |
| Frontend build fails | `NEXT_PUBLIC_API_BASE_URL` | Set build-arg / `.env` |
| Compose refuses to start | `POSTGRES_PASSWORD` / `JWT_SECRET_KEY` unset | Fill `.env` (`${VAR:?}` guards) |
| ACME / TLS fails | `ECMP_DOMAIN` / DNS / ports 80+443 | Point DNS at host; open firewall; check Caddy logs |
| TrustedHost 400 | `ALLOWED_HOSTS` | Include public `ECMP_DOMAIN` and `backend` |
| Wrong client IP / scheme | `FORWARDED_ALLOW_IPS` | Use `*` in prod compose (backend not published) |

## Security operations companions (P6-002)

- [Security Operations Runbook](../../15%20Operations%20Runbook/ECMP_Security_Operations_Runbook_v1.0.md) — auth / lockout / secret / config / deploy
- [Secret Operations Guide](../../15%20Operations%20Runbook/ECMP_Secret_Operations_Guide_v1.0.md) — rotate / emergency replace
- [Audit Investigation Guide](../../15%20Operations%20Runbook/ECMP_Audit_Investigation_Guide_v1.0.md) — `security.*` + requestId
- [Operational Security](./OPERATIONAL_SECURITY.md) — P5-005 defaults / audit flood policy

## Backup & recovery companions (P6-003)

- [Backup Operations Guide](../../15%20Operations%20Runbook/ECMP_Backup_Operations_Guide_v1.0.md) — manual dump / config / secret policy
- [Restore Verification Procedure](../../15%20Operations%20Runbook/ECMP_Restore_Verification_Procedure_v0.1.md) — restore + rollback
- [DR/BCP Plan](../../15%20Operations%20Runbook/ECMP_DR_BCP_Plan_v0.1.md) — recovery priorities
- [Recovery Validation Checklist](../../15%20Operations%20Runbook/ECMP_Recovery_Validation_Checklist_v1.0.md) — `/live` `/ready`, RPO/RTO evidence
