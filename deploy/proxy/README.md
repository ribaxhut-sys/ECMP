# ECMP reverse proxy configs (Release Blocker B3)

| File | Role |
|---|---|
| `Caddyfile` | **Recommended** production proxy (automatic HTTPS) |
| `Caddyfile.lab` | Local TLS verification (`tls internal`) |
| `docker-compose.lab-override.yml` | Compose override for lab Caddyfile |
| `nginx/` | Alternative Nginx + operator-managed certs |
| `certs/` | Mount point for Nginx PEMs (git-ignored) |

Full procedure: [`docs/deployment/TLS_REVERSE_PROXY.md`](../../docs/deployment/TLS_REVERSE_PROXY.md).

```bash
# Recommended
docker compose -f docker-compose.prod.yml up -d --build

# Nginx alternative
docker compose -f docker-compose.prod.nginx.yml up -d --build
```
