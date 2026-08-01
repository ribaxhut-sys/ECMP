# Security Review Sign-off — Lab Operator (WP-04)

| Field | Value |
|---|---|
| Date | 2026-08-01 |
| Scope | VPS promotion candidates + lab edge |
| Overall | **CONDITIONAL PASS — Lab only** / **FAIL for unrestricted Production promote** |
| Baseline | `Lab_Security_Posture_Temporary_Host_20260731.md` · SEC-BASE-001 |

| ID | Item | Result | Notes |
|---|---|---|---|
| S-01 | `.env.prod.example` placeholders | **PASS** | Placeholders `change-me-*`; no live secrets in example file reviewed |
| S-02 | JWT/DB only templates in git | **PASS** | `.env` / `.env.prod` gitignored; live secrets on host only |
| S-03 | `ENVIRONMENT=production` vs Mode A JWT | **FAIL (prod)** / **WAIVED (lab W-S03)** | No `ECMP_AUTH_MODE`/OIDC in `config.py`; DEC-020 local JWT; label production ≠ Mode B |
| S-04 | Caddy `/docs*`,`/redoc*`,`/openapi.json` | **FAIL (prod)** / **WAIVED (lab W-S04)** | Still proxied in `deploy/Caddyfile`; app may disable docs if env≠development — edge still routes |
| S-05 | Rate-limit + XFF behind Caddy | **CONDITIONAL PASS** | Code exists; trust-proxy accepted for **lab single-node** only (W-S05); re-verify on multi-node |
| S-06 | IAM users repo/service | **PASS (lab)** | Lab admin surface; **DEFER promote** per WP-03 |
| S-07 | Users admin UI | **WAIVED (lab W-S07)** | Accepted lab-only; DEFER promote |
| S-08 | `/root/.ecmp-credentials` path | **PASS** | Path reference only; not in git content |
| S-09 | Written sign-off | **PASS** | This document |

## Waivers (time-bound)

| ID | Risk | Expiration | Mitigation |
|---|---|---|---|
| W-S03 | Prod env + local JWT | Until Mode B contract **or** 2026-09-30 | Lab only; no claim Enterprise SSO |
| W-S04 | Public docs routes | Until Caddy removes docs handles **or** 2026-09-30 | Prefer ENVIRONMENT=development for swagger; plan edge close |
| W-S05 | XFF trust | Until multi-instance | Single VPS lab |
| W-S07 | Admin UI privilege | Until RBAC re-review on SoT | DEFER pick |
| W-SOD-1 | Single operator SoD | Until second reviewer named | Documented lab exception |

## Sign-off

| Role | Name | Date | Decision |
|---|---|---|---|
| Security Reviewer | Lab Operator (W-SOD-1) | 2026-08-01 | **CONDITIONAL PASS (lab)** — not Production PASS |

Supersedes unsigned template for WP-04 purposes.
