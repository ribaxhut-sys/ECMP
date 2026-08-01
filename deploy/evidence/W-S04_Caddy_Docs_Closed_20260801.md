# W-S04 Closure — Caddy docs routes removed

| Field | Value |
|---|---|
| Date | 2026-08-01 |
| Change | Removed public reverse_proxy for `/docs*`, `/redoc*`, `/openapi.json` from `deploy/Caddyfile` |
| Kept | `/api/*`, `/health*`, frontend default |
| Waiver | W-S04 marked **closed** for edge exposure (lab/prod edge template) |

App-level OpenAPI remains controlled by `docs_enabled` / environment in backend.
