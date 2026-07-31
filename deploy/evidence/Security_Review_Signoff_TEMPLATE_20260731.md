# Security Review Sign-off Template (S-01…S-09 / R4)

| Field | Value |
|---|---|
| Date | 2026-07-31 |
| Status | **UNSIGNED — checklist for reviewer** |
| Scope | VPS-only promotion candidates per Split Plans |
| Starting baseline | `Lab_Security_Posture_Temporary_Host_20260731.md` (dispositions Open / Mitigated / Accepted lab-only) |

| ID | Item | Result (PASS/FAIL/N/A) | Notes |
|---|---|---|---|
| S-01 | `.env.prod.example`: no real secrets; safe placeholders | | Baseline: Mitigated (partial) |
| S-02 | JWT / DB password handling — templates only in git | | Baseline: Mitigated (partial); rotate on new host |
| S-03 | `ENVIRONMENT=production` vs Mode A / DEC-020 lab auth risk | | Baseline: Open — Blocked for promote |
| S-04 | Caddy exposure `/docs*`, `/redoc*`, `/openapi.json` | | Baseline: Accepted lab-only — reopen on final FQDN |
| S-05 | Login rate-limit + trust `X-Forwarded-For` behind Caddy | | Baseline: Open — Blocked for promote |
| S-06 | IAM users repository/service + cache invalidation | | Baseline: Open |
| S-07 | Users admin UI create/list privilege surface | | Baseline: Accepted lab-only |
| S-08 | `/root/.ecmp-credentials` references — no secret content in git | | Baseline: Mitigated (partial); not portable SoT |
| S-09 | Written Security Review sign-off | | Baseline: Open |

## Sign-off

| Role | Name | Date | Decision |
|---|---|---|---|
| Security Reviewer | _pending_ | | PASS / FAIL |
