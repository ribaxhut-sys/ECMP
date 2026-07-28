# ECMP Deployment Checklist — v1.0.0 (Production)

| Field | Value |
|---|---|
| ID | DEP-CHK-V1 |
| Version | 1.0.0 |
| Applies to | Foundation stack (`backend/`, `frontend/`, Compose) |
| Last Update | 2026-07-23 |
| Task | PHASE-13 / TASK-016 |

## Pre-deployment

- [ ] Latest code from `main` (or release commit for `v1.0.0`)
- [ ] Release tag `v1.0.0` created
- [ ] Confirm target environment is **production** (`ENVIRONMENT=production`)
- [ ] Generate / rotate strong `JWT_SECRET_KEY` (≥32 random characters); store in vault
- [ ] Set `ALLOWED_ORIGINS` to exact frontend origin(s) (no `*`; https in production)
- [ ] Set `PASSWORD_RESET_FRONTEND_BASE_URL` to the same public frontend origin
- [ ] Set `EMAIL_PROVIDER=noop` (SMTP out of scope until later release)
- [ ] Run `python scripts/validate-production-config.py --env-file .env --require-production`
- [ ] Set `ALLOWED_HOSTS` to backend public hostnames
- [ ] Confirm Postgres credentials and **backup completed**
- [ ] Review `CHANGELOG.md` + `docs/releases/v1.0.0.md`
- [ ] Confirm image tags / Compose build context match `v1.0.0`
- [ ] Docker images built
- [ ] Images scanned (if scanner available)
- [ ] Rollback package prepared (`docs/releases/ROLLBACK_v1.0.0.md`)
- [ ] SSL certificate valid (Caddy ACME or Nginx PEMs — see `docs/deployment/TLS_REVERSE_PROXY.md`)
- [ ] Domain configured (`ECMP_DOMAIN` DNS A/AAAA + reverse proxy)
- [ ] Production compose is `docker-compose.prod.yml` (proxy-only published ports)
- [ ] Confirm no `.env` with secrets is committed to git

## Database

- [ ] `alembic upgrade head` (runs automatically on backend container start)
- [ ] Migration success (no pending revisions)
- [ ] No schema conflict

## Deployment

- [ ] Pull / checkout `v1.0.0` tag or release commit
- [ ] Inject production env from vault (or `.env` not committed)
- [ ] `docker compose -f docker-compose.prod.yml config`
- [ ] `docker compose -f docker-compose.prod.yml build`
- [ ] `docker compose -f docker-compose.prod.yml up -d`
- [ ] Wait for Postgres + backend healthy; Caddy serving 80/443
- [ ] Restart services gracefully if needed (`docker compose -f docker-compose.prod.yml up -d --force-recreate`)
- [ ] Reverse proxy / TLS terminating layer verified (HTTP→HTTPS, HSTS)

## Post-deployment

- [ ] `GET https://<ECMP_DOMAIN>/live` → HTTP 200
- [ ] `GET https://<ECMP_DOMAIN>/ready` → HTTP 200, `checks.startup=ok`, `checks.database=ok`
- [ ] Backend/frontend/Postgres **not** reachable on host :8000/:3000/:5432
- [ ] Confirm `/docs` returns 404 in production
- [ ] Login via UI `/login`
- [ ] Dashboard loads
- [ ] Complaint create/list
- [ ] Reports
- [ ] User management (authorized role)
- [ ] Authentication refresh
- [ ] Logout

## Smoke test

- [ ] Create complaint
- [ ] Assign
- [ ] Escalate
- [ ] Resolve
- [ ] Close
- [ ] Dashboard update
- [ ] Reports update

## Monitoring

- [ ] CPU / Memory within baseline
- [ ] Container health = healthy
- [ ] Database connections stable
- [ ] API error rate acceptable
- [ ] P95 / P99 observed (or baseline noted if no APM yet)

## Logging

- [ ] No unexpected stack traces
- [ ] No JWT leakage
- [ ] No password leakage
- [ ] No refresh token leakage
- [ ] No sensitive headers in logs

## Rollback

See [`docs/releases/ROLLBACK_v1.0.0.md`](./releases/ROLLBACK_v1.0.0.md).

## Abort criteria (do not proceed / NO-GO)

- Secret guard fails at startup (weak JWT secret)
- Migrations fail
- `/ready` returns HTTP 503 after start window
- Login or refresh broken
- Critical security regression (tokens in logs, docs exposed in production)
- Unexpected HTTP 500 rate during smoke test