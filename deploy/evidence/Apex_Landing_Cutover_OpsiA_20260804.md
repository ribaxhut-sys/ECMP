# Evidence — Apex landing cutover (Opsi A)

| Field | Value |
|---|---|
| Date | 2026-08-04 |
| Verdict | **PASS** |
| Scope | DNS apex/www → VPS; Caddy static landing; module unchanged |
| Mode B | **CLOSED** (untouched) |

## DNS

| Host | A record |
|---|---|
| `layanankami.tech` | `187.124.137.64` |
| `www.layanankami.tech` | `187.124.137.64` |
| `pengaduan.layanankami.tech` | `187.124.137.64` (unchanged) |

## Edge

- Landing: `deploy/apex-landing/index.html` via Caddy `ECMP_APEX_DOMAIN`
- CTA → `https://pengaduan.layanankami.tech/login`
- TLS: Let’s Encrypt for apex + www obtained 2026-08-04
- Module `/login` + `/health` remain 200

## Explicit non-goals

- No SSO / Identity Adapter / enterprise `securitySchemes`
- Module not moved to apex
- Hostinger Website Builder no longer serves apex (DNS moved)

## Related

- DEC-023, `deploy/APEX_LANDING_CUTOVER_CHECKLIST.md`
