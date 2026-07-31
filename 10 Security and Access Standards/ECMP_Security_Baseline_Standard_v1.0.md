# ECMP Security Baseline Standard
Version: 1.0  
ID: SEC-BASE-001  
Date: 2026-07-31  
Role: ECMP Security Architect  
Status: **Proposed Baseline** — integrates governance 2026-07-31; does **not** authorize execution  

| Field | Value |
|---|---|
| Supersedes / extends | `ECMP_Security_Standards_v0.1.md` (SEC-STD-001) for host/domain/release portability |
| Governance | CLOSED (Phase 0–4.5); RAB = NO-GO |
| Phase 5 | PRE-APPROVED runbook only — not executable |
| Related | Lab Security Posture · Host/Domain Migration Checklist · WP-04/WP-05 · ADR-007/012/014/015 · DEC-020 |

---

# Executive Summary

This standard defines **defensive, portable security** for the Complaint Management Module so that changing **domain**, **VPS**, or **cloud host**, and performing **DR / release**, remains controlled and auditable.

It is **not** a penetration test, vulnerability scan, or implementation guide.

**Ownership boundary (North Star):**

| Belongs to ECMP (this module) | Belongs to Enterprise Platform (not invented here) |
|---|---|
| App RBAC, complaint audit, module secrets in env, edge config for this deploy, release evidence | Corporate IdP/SSO, global MFA policy, org directory, enterprise SIEM, multi-region HA platform |

**Current maturity target for live lab:** **Level 1 — Lab** (with explicit reopen-on-migration).  
**Minimum before calling a host “production for this module”:** **Level 3 — Production** controls in §15.  
**Level 4–5:** Future Work / Platform — out of Complaint Module completion unless Board assigns.

---

# Security Architecture Overview

```text
                    ┌─────────────────────────────────────┐
                    │     Enterprise Platform (future)     │
                    │  IdP · MFA · Directory · SIEM · HA   │
                    └─────────────────┬───────────────────┘
                                      │ Mode B JWT (contract TBD)
┌─────────────────────────────────────▼───────────────────────────────────┐
│ ECMP Module boundary                                                     │
│  Edge (Caddy + ECMP_DOMAIN) → Frontend / Backend → Postgres              │
│  Secrets: host env only · AuthZ: module RBAC · Audit: append-only        │
│  Release: RAB → signed gates → Runbook evidence (no silent Git promote)│
└─────────────────────────────────────────────────────────────────────────┘
         ▲ portable via env + backup/restore + DNS — not via redesign
```

Portability rule: **identity of the service = configuration + data backup**, not hostname baked into code.

---

# SECTION 1 — Security Principles

| Principle | ECMP interpretation |
|---|---|
| Least Privilege | Accounts, DB roles, container caps, and admin UI scoped to need; no shared root for daily ops |
| Zero Trust | Do not trust network location; every functional API requires AuthN (except `/health`); edge ≠ identity |
| Defense in Depth | Host firewall + TLS edge + app AuthZ + DB privileges + backups |
| Secure by Default | Docs/OpenAPI closed on non-lab; HTTPS only; no secrets in git; dev endpoints gated |
| Separation of Duties | Author ≠ sole approver for release security gate; RAB ≠ implementer alone |
| Immutable Infrastructure | Prefer replaceable hosts/images over long-lived snowflake VPS; config in repo templates, secrets out of band |
| Configuration as Code | Caddy/compose/templates versioned; runtime secrets and FQDN via env |
| Auditability | Auth, deploy, release, and significant writes leave evidence |
| Recoverability | Backup + tested restore + documented rollback before promote |

---

# SECTION 2 — Identity & Access Management

| Topic | Baseline |
|---|---|
| Administrator accounts | Named humans only; no shared “admin” for production; lab may use seed users **labeled lab** |
| Service accounts | Compose service identity ≠ human admin; no human SSH as app UID for routine deploys if avoidable |
| SSH access | Key-based; root login disabled for routine use; rate-limit / fail2ban-equivalent; jump path documented |
| MFA | **Platform-owned** for corporate SSO (Mode B). Lab Mode A: password JWT — Accepted lab-only until IdP contract |
| RBAC | Module authorization per ADR-008 / Role Access Matrix; ECMP is not User Directory SoR |
| Emergency access | Break-glass procedure: dual control, time-bound, logged, rotated after use |
| Account lifecycle | Join/move/leave: provision, revoke, archive; lab seed data not reused as prod identities |
| Credential rotation | On hire/leave, on incident, on **every host migration**, on suspicion of leak |

Align AuthN phases with ADR-007 / ADR-012 / DEC-020. **Do not invent production IdP issuer** without platform contract.

---

# SECTION 3 — Secrets Management

## Classification

| Class | Examples | Storage |
|---|---|---|
| C1 Critical | `JWT_SECRET_KEY`, DB password, OAuth client secret, encryption keys | Host secret store / env — never git |
| C2 Sensitive | SMTP creds, API keys to external systems | Same as C1 |
| C3 Operational | Non-secret config (`ECMP_DOMAIN`, feature flags) | Env / config templates OK in git as examples |

## Rules

1. `.env` gitignored; examples contain **placeholders only**.  
2. **Rotate** JWT, DB, SMTP, OAuth, API keys on: new VPS, new cloud, domain cutover to “final”, incident, staff leave with access.  
3. **Revoke** old secrets before or immediately after cutover; do not leave dual-valid JWT secrets across hosts.  
4. PROD vault/secret manager = platform deployment decision (`14 Deployment Standards`) — until then, hardened host env + restricted permissions.  
5. Path references like `/root/.ecmp-credentials` are **not** portable SoT.

---

# SECTION 4 — Infrastructure Security

| Control | Baseline |
|---|---|
| VPS hardening | Minimal packages; automatic security updates policy; non-shared multi-tenant abuse awareness |
| Linux hardening | Unneeded services off; correct file perms on `.env` (e.g. 600); dedicated app user |
| Firewall | Allow 80/443; SSH rate-limited; deny by default otherwise |
| SSH | Keys only; disable password auth in production-bound hosts; no world-exposed agent forwards |
| Fail2Ban / equivalent | SSH and optionally edge auth abuse — host-level (out of git; re-apply on migration — D-06) |
| Time sync | NTP/chrony required (JWT skew, logs, TLS) |
| Container isolation | User-defined bridge; no host network mode for app |
| Docker network | Backend DB not published publicly; only edge publishes 80/443 |
| File permissions | Secrets readable only by deploy user / compose |
| Host backup | Config inventory + secret recovery path (not secrets in git backup) |

---

# SECTION 5 — Container Security

| Control | Baseline |
|---|---|
| Non-root containers | Prefer non-root USER in images where stack allows |
| Minimal images | Slim/runtime images; no compilers in prod images |
| Version pinning | Pin base image tags/digests for release builds |
| Image provenance | Build from repo CI/context; no mystery local tarballs as SoT |
| Image scanning | Required from **Level 3**; advisory at Level 1–2 |
| Resource limits | Memory/CPU limits in compose for prod-bound |
| Read-only FS | Where app supports; writable only needed volumes |
| Health checks | `/health` (and compose healthcheck) for restart policy |

---

# SECTION 6 — Application Security

| Control | Baseline |
|---|---|
| HTTPS only | Public access via TLS edge; no intentional cleartext public API |
| Secure cookies | Secure/HttpOnly/SameSite as applicable to session model |
| JWT handling | Validate alg/exp/aud as mode requires; short TTL preferred; secret rotation invalidates old |
| CSRF | Required for cookie-session patterns; Bearer API follows established anti-CSRF model for SPA |
| CORS | `ALLOWED_ORIGINS` exact FQDN; update on domain migration |
| CSP | Define and tighten by maturity level; lab may be looser if documented |
| HSTS | Enable on final public FQDN after HTTPS stable |
| X-Frame-Options / frame-ancestors | Deny/sameorigin default |
| X-Content-Type-Options | `nosniff` (already directed at edge headers in lab Caddy) |
| Referrer-Policy | Strict-origin-when-cross-origin or tighter |
| Rate limiting | Login and sensitive endpoints; **trusted proxy** must be correct (S-05) |
| Request validation | Schema/OpenAPI-aligned validation |
| File upload | Type/size/malware policy when feature exists |
| Error handling | No stack traces or secrets to clients; no PII in app logs (SEC-STD-001) |
| OpenAPI/docs | **Closed** on Level 3+ public edge; lab-only acceptance must reopen on migration |

---

# SECTION 7 — Database Security

| Control | Baseline |
|---|---|
| Least privilege | App role ≠ superuser; migrations via controlled role |
| Backup encryption | At-rest encryption for backup media from Level 3; lab: access-controlled storage minimum |
| Restore validation | Restore drill evidence required (existing restore-drill practice) |
| Audit logging | Business write audit append-only (BR-008); DB admin actions logged at host where possible |
| Connection security | DB not exposed on public NIC; compose internal network |
| Credential rotation | With host migration and on schedule (§12) |

---

# SECTION 8 — Logging & Audit

| Log class | Minimum content |
|---|---|
| Audit events | Actor, action, entity, outcome, UTC time (app audit_log) |
| Authentication | Login success/failure, rate-limit hits (no passwords) |
| Deployment | Who, host, image/tag, compose project, time |
| Release | RAB decision, base SHA, pick SHAs, PR/merge evidence |
| Security | Firewall changes, secret rotation events, break-glass |

| Topic | Baseline |
|---|---|
| Retention | Lab: ≥30 days operable logs; Production-bound: per Compliance (`17`) — default ≥90 days security/auth until Compliance overrides |
| Integrity | Prefer append-only app audit; protect log files from world write; ship to platform SIEM when available (Platform) |

---

# SECTION 9 — Backup & Disaster Recovery

| Topic | Baseline |
|---|---|
| Backup strategy | Automated Postgres dump + retain N; config templates in git; secrets recovery procedure separate |
| Restore strategy | Documented restore to new host; no dual-write |
| Recovery validation | Periodic restore drill (evidence under `deploy/evidence/`) |
| Backup encryption | Required Level 3+ |
| RPO / RTO (module lab→prod) | **Lab:** best-effort. **Level 3 target (module):** RPO ≤ 24h, RTO ≤ 8h unless Board sets stricter |
| DR testing | At least quarterly restore drill before claiming Level 3 |

Disaster ≠ redesign domain. DR = new/clean host + env + restore + DNS.

---

# SECTION 10 — Migration Security

Applies to domain, subdomain, VPS, and cloud move. Extends `Host_Domain_Migration_Checklist_20260731.md`.

| Phase | Controls |
|---|---|
| Pre-migration security review | Reopen lab acceptances (S-03/S-04/S-07); confirm docs closed if leaving lab; WP-04 posture current |
| Secret rotation | New JWT/DB/SMTP/OAuth on target **before** public cutover; revoke old after soak |
| DNS validation | `dig` proves A/AAAA; TTL plan; no cutover on wrong IP |
| Certificate validation | ACME success on new FQDN; no expired/mismatch cert |
| Rollback security | DNS rollback plan; do not leave two hosts accepting writes; old secrets revoked on abort path too |
| Post-migration verification | Smoke health/login/API; CORS/hosts; rate-limit IP; admin access; backup job on new host |

**Cloud migration:** same as VPS migration + provider IAM least privilege + network SG equivalent to firewall §4. No ECMP-specific cloud SDK required.

---

# SECTION 11 — Release Security Gate

Mandatory before Phase 5 execution (after RAB GO) and before merge promote:

| Gate | Owner | Evidence |
|---|---|---|
| Security Review (S-01…S-09) | Security Reviewer | Signed Security Sign-off |
| Dependency Review | Tech Lead | CI / advisory notes for release scope |
| Container Review | Deploy Lead | Image pin + limits + no public DB port |
| Secrets Review | Security + Deploy | No secrets in git; rotation if new host |
| Configuration Review | Deploy Lead | Domain/CORS/hosts/TLS coherent |
| Rollback Validation | Deploy + RM | Signed Rollback Pack |
| Evidence Verification | Release Manager | Pack complete (WP-07) |

Unsigned gate = **no promote**. Aligns R4 and Phase 5 Runbook CP-1/CP-5.

---

# SECTION 12 — Operational Security

| Cadence | Activities |
|---|---|
| Monthly | Access review (lab/prod accounts); firewall rule review; cert expiry check; backup success review |
| Quarterly | Restore drill; dependency update window; revisit lab acceptances; threat model delta |
| Continuous / event | Certificate renewal (ACME); secret rotation on event; OS patch; Docker image update; DR exercise after major host change |

---

# SECTION 13 — Security Checklists

## 13.1 Server Provisioning
- [ ] OS updates policy on  
- [ ] App user + Docker  
- [ ] Firewall 80/443 + SSH hardening  
- [ ] Time sync  
- [ ] `.env` mode 600; placeholders never committed  
- [ ] Fail2ban/equivalent for SSH  
- [ ] Backup target defined  

## 13.2 Production-bound Deployment
- [ ] §11 gates signed  
- [ ] `ECMP_AUTH_MODE` matches environment policy  
- [ ] Docs/OpenAPI not public (or waiver)  
- [ ] HTTPS + HSTS plan  
- [ ] DB not public  
- [ ] Health check green  
- [ ] Release evidence archived  

## 13.3 Domain Migration
- [ ] Pre-migration security review  
- [ ] Env FQDN/CORS/hosts/API URL updated  
- [ ] Frontend rebuilt  
- [ ] Secrets rotated if leaving lab trust boundary  
- [ ] DNS + cert validated  
- [ ] Smoke + rate-limit check  
- [ ] Evidence A-09  

## 13.4 Server Migration
- [ ] Backup taken & verified  
- [ ] New host provisioned (13.1)  
- [ ] New secrets  
- [ ] Restore + migrate  
- [ ] Private smoke then DNS  
- [ ] Old host writes stopped  
- [ ] Evidence B-11  

## 13.5 Emergency Rollback
- [ ] DNS and/or release-branch revert per Rollback Pack  
- [ ] No force-push to SoT  
- [ ] Secrets consistency checked  
- [ ] Incident note filed  

## 13.6 Disaster Recovery
- [ ] Declare DR  
- [ ] Provision clean host  
- [ ] Restore latest good backup  
- [ ] New secrets  
- [ ] DNS to DR host  
- [ ] Validate + schedule restore-drill follow-up  

---

# SECTION 14 — Security KPIs

| KPI | Lab (L1) target | Production-bound (L3) target |
|---|---|---|
| Critical vulns open | Track | 0 beyond SLA (e.g. 7 days) |
| High vulns open | Track | SLA (e.g. 30 days) |
| Patch compliance | Best effort | ≥95% hosts in window |
| Backup success rate | ≥95% | ≥99% |
| Restore success (last drill) | Pass/Fail recorded | Pass within RTO |
| Certificate days-to-expiry | >14 | >30 |
| Secret rotation compliance | On migration/incident | Schedule + migration |
| Security review completion | Before re-RAB | 100% releases |
| Deployment approval completion | N/A while NO-GO | 100% promotes |

---

# SECTION 15 — Security Maturity Roadmap

| Level | Name | ECMP ownership |
|---|---|---|
| L1 | Lab | **Current intended** for temporary VPS/domain |
| L2 | Internal | Trusted network / internal users |
| L3 | Production | Module production-bound on agreed host |
| L4 | High Availability | **Future Work — Platform/ops beyond single-module scope** |
| L5 | Enterprise | **Future Work — Enterprise Platform** (IdP, SIEM, org IAM) |

### Level 1 — Lab
- **Controls:** HTTPS edge; env secrets; firewall basics; Mode A allowed; docs exposure only if Accepted lab-only  
- **Reviews:** Lab Security Posture; migration checklist known  
- **Monitoring:** Health + basic auth failure awareness  
- **Automation:** Compose up; ACME  
- **Docs:** This baseline + migration checklist + posture  

### Level 2 — Internal
- **Controls:** Docs closed; stronger SSH; named accounts; backup+restore drill  
- **Reviews:** WP-04 style security sign-off  
- **Monitoring:** Auth + deploy logs retained 30d+  
- **Automation:** Scheduled backup  
- **Docs:** Signed Security + Deploy reviews  

### Level 3 — Production
- **Controls:** Mode policy enforced (`jwt` when staging/production per config gates); HSTS; rate-limit+trusted proxy verified; secrets rotation discipline; DB not public; image pin; backup encryption  
- **Reviews:** Full §11 Release Security Gate  
- **Monitoring:** KPI dashboard monthly  
- **Automation:** Backup + cert renew + CI green before merge  
- **Docs:** Complete evidence pack + RAB GO  

### Level 4 — High Availability
- **Required Controls / Reviews / Monitoring / Automation / Docs:** Multi-AZ, automated failover, duplicated secrets store — **Platform/ops program**.  
- *Future Work — Di luar ruang lingkup Complaint Management Module unless Board explicitly expands.*

### Level 5 — Enterprise
- **Required:** Corporate IdP MFA, central SIEM, org directory SoR, enterprise vault — **Enterprise Platform**. ECMP consumes contracts; does not define them here.  
- *Future Work — Di luar ruang lingkup Complaint Management Module.*

---

# Operational Procedures (summary)

1. **Day-2 lab:** operate at L1; track Open items in Lab Security Posture.  
2. **Before domain/VPS move:** §10 + migration checklist; rotate secrets; reopen lab acceptances.  
3. **Before promote:** §11 gates + RAB GO + Phase 5 runbook.  
4. **Ongoing:** §12 cadence; measure §14 KPIs from L2 upward.

---

# Approval Matrix

| Artifact | Approver | When |
|---|---|---|
| This Standard (SEC-BASE-001) | Security Architect → Architecture Board | Adoption |
| Lab Security Posture | Sec + Deploy + RM | WP-04 start |
| Security Sign-off S-01…S-09 | Security Reviewer | Before re-RAB / promote |
| Migration checklist execution | Deploy Lead | Each move |
| Release Security Gate §11 | Per gate owners | Before Phase 5 / merge |
| L4/L5 expansion | Board + Platform owners | Only if explicitly in scope |

---

# KPIs

See §14.

---

# Security Roadmap

| Horizon | Outcome |
|---|---|
| Now | Adopt SEC-BASE-001; remain L1 lab; close WP-04 using posture → sign-off |
| Next host/domain | Execute §10 securely; decide L2 vs stay L1 |
| Module production-bound | Reach L3 controls + RAB GO + evidence |
| Later | Consume Platform IdP/SIEM (L5 capabilities) without rewriting complaint domain |

---

# Formal Statement

SEC-BASE-001 is the **ECMP Security Baseline Standard** for portable, auditable operation of the Complaint Management Module.  
It does **not** authorize Git execution, penetration testing, or expansion into Enterprise Platform ownership.  
Identity contracts for Mode B remain **unverified** until obtained from platform owners.

—*End of ECMP Security Baseline Standard v1.0*
