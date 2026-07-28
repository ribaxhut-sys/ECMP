# ECMP Startup Checklist (R6-03)

| Field | Value |
|---|---|
| ID | START-CHK-001 |
| Version | 1.0.0 |
| Date | 2026-07-28 |

## Before `docker compose up`

- [ ] `.env` present and **not** committed
- [ ] `python scripts/validate-production-config.py --env-file .env` → PASS
- [ ] For production: `--require-production` → PASS
- [ ] `JWT_SECRET_KEY` rotated / vault-injected (≥32 chars)
- [ ] `POSTGRES_PASSWORD` strong
- [ ] `ALLOWED_ORIGINS` matches real frontend origin(s)
- [ ] `PASSWORD_RESET_FRONTEND_BASE_URL` equals one allowed origin
- [ ] `EMAIL_PROVIDER=noop` (staging/production) until SMTP exists
- [ ] `NEXT_PUBLIC_API_BASE_URL` set for image build
- [ ] `IMAGE_TAG` pinned (not floating `latest`) for production
- [ ] Pre-deploy DB backup completed (upgrades)

## After start

- [ ] `docker compose ps` — postgres / backend / frontend healthy or running
- [ ] `GET /health` → 200, `database=up`
- [ ] Backend logs show `application started` with expected `ENVIRONMENT`
- [ ] No `Configuration validation failed` in backend logs
- [ ] Frontend HTTP 200 on `/`
- [ ] `/docs` returns 404 when `ENVIRONMENT` is staging/production
- [ ] Login sets refresh cookie (`HttpOnly`; `Secure` outside development)
- [ ] Refresh + logout succeed

## Fail-fast triage

| Symptom | Likely variable | Fix |
|---|---|---|
| Container exit on start; JWT message | `JWT_SECRET_KEY` | Strong ≥32 char secret |
| Postgres password rejected | `POSTGRES_PASSWORD` | Non-default strong password |
| Localhost origin rejected | `ALLOWED_ORIGINS` | Public https origin |
| Reset URL rejected | `PASSWORD_RESET_FRONTEND_BASE_URL` | Align with CORS origin |
| Email provider rejected | `EMAIL_PROVIDER` | Use `noop` outside development |
| Frontend build fails | `NEXT_PUBLIC_API_BASE_URL` | Set build-arg / `.env` |
| Compose refuses to start | `POSTGRES_PASSWORD` / `JWT_SECRET_KEY` unset | Fill `.env` (`${VAR:?}` guards) |
