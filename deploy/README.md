# ECMP edge deploy — `pengaduan.layanankami.tech` (+ apex landing opsional)

Lab Mode A (IP + ports 3000/8000) can keep running until DNS is ready.
This folder adds **Caddy TLS reverse proxy** only — **no SSO**.

## Hosts (Opsi A / DEC-023)

| Host | Peran |
|------|--------|
| `pengaduan.layanankami.tech` (`ECMP_DOMAIN`) | Modul pengaduan (login Mode A) |
| `layanankami.tech` (`ECMP_APEX_DOMAIN`) | Landing statis → link ke modul |

Cutover apex: [`APEX_LANDING_CUTOVER_CHECKLIST.md`](APEX_LANDING_CUTOVER_CHECKLIST.md).

## Auth (DEC-020)

| Phase | Mechanism |
|-------|-----------|
| Now (lab / first shared URL) | Local JWT users (`admin` / password in DB) |
| Later | SSO/OIDC as **target** login (not temporary stopgap) |

## Cutover checklist (modul)

1. **DNS** — create A record `pengaduan` → VPS IPv4 (`187.124.137.64`).
2. **Wait** until `dig +short pengaduan.layanankami.tech A` returns that IP.
3. **Env** — `cp .env.prod.example .env.prod` and set strong `POSTGRES_PASSWORD`, `JWT_SECRET_KEY`, `CADDY_ACME_EMAIL`; set `ECMP_APEX_DOMAIN` only when siap cutover apex.
4. **Bring up overlay**:
   ```bash
   cd /opt/ECMP
   docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod up -d --build
   ```
5. **Verify** — `https://pengaduan.layanankami.tech/login` and `https://pengaduan.layanankami.tech/health`.
6. Optional: firewall allow only 22/80/443; keep 3000/8000/5433 on localhost (prod overlay already binds them to `127.0.0.1`).

## Rollback to lab-only

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod stop caddy
docker compose --env-file .env up -d
```

## Backup

```bash
/opt/ECMP/deploy/backup-postgres.sh
```

Dumps land in `backups/ecmp_*.sql.gz` (git-ignored). Cron example (02:15 UTC daily) is installed on the lab VPS; retain `ECMP_BACKUP_KEEP_DAYS` (default 14).

## Lab master data seed

Without seed data, complaint create fails (empty customers/branches + no active SLA).

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod \
  exec -T postgres psql -U ecmp -d ecmp < deploy/seed-lab-master-data.sql
```

Then create `agent1` / `supervisor1` via `POST /api/v1/users`, insert matching `user_roles` rows, and restart backend so permission cache refreshes. Assign requires role `SUPERVISOR` + `complaints:assign`.

## Host credentials

On the VPS only (not in git): `/root/.ecmp-credentials` (mode 600) — admin + DB passwords after hardening.

## Firewall

UFW: allow `22`, `80`, `443` only. App ports stay on `127.0.0.1`.
