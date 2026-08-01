# Observability Minimum + Lab Smoke (2026-08-01)

| Field | Value |
|---|---|
| Status | **Baseline documented** — full APM stack still out of scope for this change |
| Related | `21 Technical Standards/ECMP_Observability_Standard_v0.1.md` |

## Minimum now (already in tree / this PR)

1. **Health**: `GET /health` via edge `/health*` (Caddy) and backend health.  
2. **Request correlation**: `X-Request-ID` / access logging in backend middleware.  
3. **Smoke script**: `deploy/smoke-lab.sh` (this change) — curl health + optional login page.  
4. **Config fail-fast**: `scripts/validate-production-config.py` for Mode B/prod gates when enabled.

## Still BELUM ADA (do not claim)

Prometheus, Grafana, Sentry, OTel exporters as first-class deployables.

## Operator action

```bash
./deploy/smoke-lab.sh https://pengaduan.layanankami.tech
# or
./deploy/smoke-lab.sh http://127.0.0.1:8000
```
