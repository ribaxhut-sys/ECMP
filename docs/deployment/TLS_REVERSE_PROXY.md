# ECMP TLS & Reverse Proxy Deployment (B3)

| Field | Value |
|---|---|
| ID | DEP-TLS-001 |
| Version | 1.0.0 |
| Date | 2026-07-28 |
| Release | ECMP v1.0.0 |
| Blocker | B3 — reverse proxy + TLS |
| Recommended proxy | **Caddy 2** (`docker-compose.prod.yml`) |
| Alternative | Nginx (`docker-compose.prod.nginx.yml`) |

## Root cause (B3)

Foundation Compose (`docker-compose.yml`) published frontend (`:3000`), backend (`:8000`), and optionally Postgres to the host with **no official TLS termination or reverse proxy**. Public production requires HTTPS, a single edge entrypoint, trusted forwarded headers, and hardened defaults.

## Architecture (recommended)

```text
Internet
   │
   │  TCP 80 / 443  (only published ports)
   ▼
┌─────────────┐
│   Caddy     │  HTTP→HTTPS redirect, ACME certs, gzip/zstd,
│  (edge)     │  HSTS, WebSocket Upgrade forwarding
└──────┬──────┘
       │  Docker network "internal" (no host ports)
       ├──────────────► frontend:3000
       └──────────────► backend:8000 ──► postgres:5432
```

**Single public hostname** (recommended for refresh-cookie same-origin):

| Path | Upstream |
|---|---|
| `/api/*`, `/live`, `/ready`, `/health`, `/version` | `backend:8000` |
| everything else | `frontend:3000` |

Split API hostname is possible but not the default reference (set a second Caddy site block and rebuild frontend with that API origin).

## DNS requirements

1. Create an **A** (or **AAAA**) record for `ECMP_DOMAIN` → public IP of the Docker host.
2. Propagate before first ACME attempt (Caddy HTTP-01 / TLS-ALPN).
3. Optional: `www` CNAME → apex only if you add a matching site block (not in the default Caddyfile).

## Firewall ports

| Port | Proto | Direction | Purpose |
|---|---|---|---|
| 80 | TCP | inbound | HTTP→HTTPS + ACME HTTP-01 |
| 443 | TCP | inbound | HTTPS |
| 443 | UDP | inbound | HTTP/3 (QUIC) — optional; published by default |
| 22 | TCP | inbound | SSH admin (host) |
| 3000 / 8000 / 5432 | — | **closed** on host | App tiers stay internal |

Do not publish backend, frontend, or Postgres host ports on the production compose file.

## TLS certificates

### Caddy (recommended)

- Automatic issuance and renewal via Let's Encrypt / ZeroSSL.
- Set `ACME_EMAIL` (registration contact) and `ECMP_DOMAIN`.
- Certificate material persists in volume `ecmp_prod_caddy_data` (`/data`).
- Renewal is automatic inside Caddy (no cron job).

### Nginx (alternative)

- Operator supplies PEMs at `deploy/proxy/certs/fullchain.pem` and `privkey.pem`.
- Renew with certbot (or corporate PKI) and reload Nginx (`docker compose ... exec nginx nginx -s reload`).
- ACME webroot path: `/.well-known/acme-challenge/` → `/var/www/certbot`.

### Lab / offline verification

```powershell
docker compose -f docker-compose.prod.yml `
  -f deploy/proxy/docker-compose.lab-override.yml config
```

Uses `Caddyfile.lab` (`tls internal`). Browser/curl must trust the local CA or use `curl -k`.

## Environment variables

Copy `.env.production.example` (repo root) → `.env` (never commit).

| Variable | Required | Notes |
|---|---|---|
| `ECMP_DOMAIN` | Yes | Public hostname (DNS) |
| `ACME_EMAIL` | Yes (Caddy) | ACME account email |
| `ENVIRONMENT` | Yes | `production` |
| `ALLOWED_ORIGINS` | Yes | `https://<ECMP_DOMAIN>` |
| `ALLOWED_HOSTS` | Yes | `<ECMP_DOMAIN>,backend` |
| `NEXT_PUBLIC_API_BASE_URL` | Yes (build) | `https://<ECMP_DOMAIN>` |
| `PASSWORD_RESET_FRONTEND_BASE_URL` | Yes | Same as origin |
| `FORWARDED_ALLOW_IPS` | Prod compose default `*` | Trust proxy headers; safe because backend has **no** host port |
| `JWT_SECRET_KEY` / `POSTGRES_PASSWORD` | Yes | Strong secrets |
| `EMAIL_PROVIDER` | Yes | `noop` until SMTP |

Validate:

```powershell
python scripts/validate-production-config.py --env-file .env --require-production
```

### Trusted forwarded headers (backend)

| Header | Set by proxy | Consumed by |
|---|---|---|
| `X-Forwarded-For` | Caddy / Nginx | Uvicorn (`--proxy-headers` + `FORWARDED_ALLOW_IPS`) → `request.client` |
| `X-Forwarded-Proto` | Caddy / Nginx | Uvicorn URL scheme (`https`) |
| `X-Forwarded-Host` | Caddy / Nginx | Host reconstruction behind proxy |
| `Host` | Passed through | `TrustedHostMiddleware` (`ALLOWED_HOSTS`) |

Application settings:

- `FORWARDED_ALLOW_IPS=*` in production compose (entrypoint passes `--forwarded-allow-ips`).
- `TRUST_FORWARDED_CLIENT_IP` defaults to `false` (SECMIG-P5-005). Login lockout and audit IP helpers use the ASGI peer (`request.client.host`), which Uvicorn rewrites only for trusted hops. Set `TRUST_FORWARDED_CLIENT_IP=true` only when the process cannot rely on Uvicorn proxy-header trust and still needs application-level `X-Forwarded-For` parsing.
- `ALLOWED_HOSTS` must include the public hostname **and** `backend` (healthchecks / internal DNS).
- Refresh cookies use `Secure=true` when `ENVIRONMENT` is not development/test — requires HTTPS at the browser.

## Security headers

| Header | Source | Value / notes |
|---|---|---|
| `Strict-Transport-Security` | **Proxy** | `max-age=31536000; includeSubDomains; preload` |
| `X-Content-Type-Options` | Application | `nosniff` |
| `X-Frame-Options` | Application | `DENY` |
| `Referrer-Policy` | Application | `no-referrer` |
| `Permissions-Policy` | Application | camera/mic/geo disabled |
| `Content-Security-Policy` | Application | `default-src 'none'; frame-ancestors 'none'; ...` |

Proxy does **not** duplicate application headers.

## Persistent volumes

| Volume | Purpose |
|---|---|
| `ecmp_prod_pgdata` | PostgreSQL data |
| `ecmp_prod_caddy_data` | ACME certs + Caddy state |
| `ecmp_prod_caddy_config` | Caddy config autosave |

Backup Postgres before upgrades (`docs/deployment/UPGRADE_PROCEDURE.md`). Back up `caddy_data` if you need to preserve ACME account/certs across host rebuilds.

## Deploy (Caddy)

```powershell
copy .env.production.example .env
# edit secrets + ECMP_DOMAIN + ACME_EMAIL

python scripts\validate-production-config.py --env-file .env --require-production
docker compose -f docker-compose.prod.yml config
docker compose -f docker-compose.prod.yml up -d --build
```

## Upgrade procedure (with proxy)

1. Backup Postgres (+ optionally `caddy_data`).
2. Pull/checkout release tag; refresh `.env` if new vars appear.
3. Validate config.
4. `docker compose -f docker-compose.prod.yml build backend frontend`
5. `docker compose -f docker-compose.prod.yml up -d`
6. Smoke via **HTTPS** (not host `:8000`):

```powershell
curl.exe -fsS https://$env:ECMP_DOMAIN/live
curl.exe -fsS https://$env:ECMP_DOMAIN/ready
curl.exe -sI http://$env:ECMP_DOMAIN/live   # expect 308/301 → https
```

Caddy renews certificates automatically; Nginx operators renew PEMs and reload.

## Validation checklist

- [ ] `docker compose -f docker-compose.prod.yml config` succeeds
- [ ] HTTPS `GET /live` and `GET /ready` return 200
- [ ] HTTP redirects to HTTPS
- [ ] Host ports 3000/8000/5432 **not** published (`docker compose ... ps` / `docker port`)
- [ ] Response includes HSTS (proxy) + app security headers
- [ ] Login / refresh cookie `Secure` over HTTPS
- [ ] Existing API behavior unchanged (no feature regression)

## WebSockets

v1.0.0 has **no** product WebSocket APIs. Proxy configs still forward `Upgrade` / `Connection` for Next.js and future use.

## Related

- [`PRODUCTION_DEPLOYMENT_GUIDE.md`](./PRODUCTION_DEPLOYMENT_GUIDE.md)
- [`ENVIRONMENT_VARIABLE_REFERENCE.md`](./ENVIRONMENT_VARIABLE_REFERENCE.md)
- [`UPGRADE_PROCEDURE.md`](./UPGRADE_PROCEDURE.md)
- [`../deployment-checklist.md`](../deployment-checklist.md)
- `deploy/proxy/README.md` (repo root)
