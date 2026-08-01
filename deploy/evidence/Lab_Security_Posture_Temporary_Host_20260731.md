# Lab Security Posture — Temporary VPS / Domain
Version: 1.0  
Date: 2026-07-31  
Class: Planning / WP-04 input (not a signed Security PASS)  
Authority | Based only on approved Phase 0 flags, Phase 1 High items, DEC-020 lab stance, Host/Domain Migration Checklist  

| Field | Value |
|---|---|
| Context | Lab on temporary VPS + FQDN that **will move** |
| Current lab FQDN (reference) | `pengaduan.layanankami.tech` |
| Auth posture (lab) | Mode A local JWT now → SSO later (DEC-020 lab) |
| RAB | NO-GO — this sheet does **not** satisfy R4 |
| Re-audit | Not performed — disposition from existing evidence only |

**Status legend**

| Status | Meaning |
|---|---|
| Open | Risk known; control not verified complete |
| Mitigated (partial) | Control exists in design/evidence; residual remains |
| Accepted (lab-only) | Tolerated **only** while labeled lab; must re-open before final host/domain |
| Blocked for promote | Must be PASS/closed before Security Sign-off / Phase 5 |

---

## Executive posture

Treat the current stack as **public-facing lab**, not Enterprise production.

- Exposure and Mode A auth are **Accepted (lab-only)** with explicit reopen-on-migration.  
- Secrets handling, edge docs, and proxy trust are **Open / Blocked for promote** until WP-04 PASS.  
- Moving domain/server is safe only if secrets are **rotated** and lab acceptances are **re-validated** on the new FQDN/host.

---

## S-01…S-09 disposition (evidence-bound)

| ID | Topic | Disposition | Evidence basis | Required before final move / promote |
|---|---|---|---|---|
| S-01 | `.env.prod.example` placeholders | **Mitigated (partial)** | Phase 0 §7: keys present; values redacted in forensics — example must stay placeholder-only | Confirm no real secrets in git; template review signed |
| S-02 | JWT / DB password in git | **Mitigated (partial)** | Same as S-01; live secrets expected only in host `.env` (not evidenced here) | Rotate on every new host; never commit `.env` |
| S-03 | `ENVIRONMENT=production` vs Mode A lab | **Open** · **Blocked for promote** | Phase 0 §7 / Phase 1 High: production env + DEC-020 local JWT narrative | Align env label with real auth mode; no gate bypass |
| S-04 | Caddy `/docs*`, `/redoc*`, `/openapi.json` | **Accepted (lab-only)** · **Blocked for promote** | Phase 0 §7: exposed on same public host | Close or IP-restrict before final domain; re-check after FQDN change |
| S-05 | Rate-limit + `X-Forwarded-For` | **Open** · **Blocked for promote** | Phase 0 §6–7: limiter + Caddy; trust-proxy correctness not signed | Verify trusted proxy / IP keying with edge; smoke after move |
| S-06 | IAM users repo/service + cache | **Open** | Phase 0 §7 / Phase 1: provisioning paths flagged | Review privilege + cache invalidation in WP-04 |
| S-07 | Users admin UI create/list | **Accepted (lab-only)** | Phase 0 §7: large admin surface | Lab accounts only; re-review before final host |
| S-08 | `/root/.ecmp-credentials` path ref | **Mitigated (partial)** | Phase 0 §7: path only in docs; file not in git | Do not treat path as portable SoT; exclude from migration copy-list |
| S-09 | Written Security Sign-off | **Open** | Template unsigned | WP-04 owner signature required for R4 |

---

## Lab-only acceptances (must reopen on migration)

When domain or server changes, these automatically return to **Open**:

1. **S-04** public OpenAPI/docs exposure  
2. **S-07** admin Users UI as lab convenience  
3. **S-03** any temporary mismatch between env label and Mode A lab auth  
4. Any firewall/UFW host rules **out of git** (Phase 1 / D-06) — re-apply on new host; do not assume they travel  

Record reopen in migration evidence (Host/Domain Migration Checklist A-09 / B-11).

---

## Controls that travel with a good migration

| Control | How |
|---|---|
| Hostname not hard-coded | `ECMP_DOMAIN` + Caddy `{$ECMP_DOMAIN}` |
| CORS / hosts / public API URL | Env + frontend rebuild |
| Secrets | **New** values on new host — never clone blindly |
| DB | Backup → restore; no dual-write |
| TLS | Fresh ACME on new FQDN |
| Edge surface | Re-apply S-04 decision (close docs on final) |

---

## Promote / final-host gate (security)

Do **not** claim Security PASS until:

- [ ] S-01…S-08 reviewed with PASS/FAIL/N/A + notes on sign-off sheet  
- [ ] S-04 not left “open public docs” on final FQDN without written accept  
- [ ] S-03 env/auth mode coherent for target (`jwt` + real IdP if staging/production)  
- [ ] S-05 proxy trust verified behind Caddy  
- [ ] S-02 rotation done for target host  
- [ ] S-09 signed by Security Reviewer  

Until then: **R4 remains FAIL**; Phase 5 remains unauthorized.

---

## Handoff to WP-04

| Input for Security Reviewer | Path |
|---|---|
| This posture sheet | `Host_Domain_…` sibling: `Lab_Security_Posture_Temporary_Host_20260731.md` |
| Sign-off template | `Security_Review_Signoff_TEMPLATE_20260731.md` |
| Phase 0 §7 list | `Git_Forensics_Phase0_20260731.md` |
| Migration reopen rules | `Host_Domain_Migration_Checklist_20260731.md` |

**Reviewer task:** convert dispositions above into official PASS/FAIL on the sign-off template. This posture sheet is **not** a substitute signature.

---

## Sign-off (posture acknowledgment only)

| Role | Name | Date | Decision |
|---|---|---|---|
| Security Reviewer | _pending_ | | Acknowledge as WP-04 starting baseline |
| Deploy Lead | _pending_ | | Acknowledge lab-only acceptances + reopen-on-move |
| Release Manager | _pending_ | | File under evidence pack |

—*End of Lab Security Posture v1.0*
