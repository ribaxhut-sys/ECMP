# Enterprise Platform Handover Package — ECMP v1.2.0

| Field | Value |
|---|---|
| ID | EP-HANDOVER-v1.2.0-20260801 |
| Date | 2026-08-01 |
| From | ECMP Platform Integration Coordinator |
| To | Enterprise Platform Owner / IdP / IAM / Org Directory |
| Candidate | `v1.2.0-rc.1` @ `6890f50` |
| ECMP status | Application COMPLETE · RC READY · Production **BLOCKED** |
| Cause | Missing Enterprise Platform artifacts |
| Verdict | **WAITING FOR ENTERPRISE PLATFORM** |

> ECMP does **not** invent production OIDC values.  
> This package lists **external** deliverables only.  
> No CAP-008 / FRD / OpenAPI / Business Rules / ECMP code changes in this pack.

## SoT anchors (ECMP side — already present)

| Artifact | Status |
|---|---|
| ADR-014 / ADR-015 | Accepted with Conditions; Mode B **Implementation Deferred** |
| SEC-BIND-OIDC-001 | Draft — provisional; needs EP confirm |
| SEC-ENT-REP-001 | Draft — provisional; needs EP confirm |
| SEC-ORG-SYNC-001 | Draft — org-gap prerequisite (C-B6-3) |
| Mode B | CLOSED (C-7 / C-B6-1) |
| Config gates | `OIDC_ISSUER` / `OIDC_AUDIENCE` / `OIDC_JWKS_URL` required for production |
| Evidence | `Mode_B_Blocked_Pending_IdP_Contract_20260801.md`, `PLATFORM_READINESS_REVIEW_v1.2.0_PE_20260801.md` |

---

## 1. Required contracts (bilateral, signed)

| ID | Deliverable | EP must provide |
|---|---|---|
| EP-C-01 | Identity Contract of Record | Signed confirmation of ADR-015 claim set as production SoT (or delta with Board Resolution) |
| EP-C-02 | IdP / OIDC Binding Contract | Production `iss`, `aud`, JWKS (or discovery), token type (JWT access vs opaque+introspection) — **real values, not examples** |
| EP-C-03 | Claim Catalog | Wire claim names → ADR-015 mapping confirmed (closes Binding Profile BP-O-01 / ADR-016 D-02) |
| EP-C-04 | Entitlement Signal Contract | Chosen representation: `module_entitlements` contains `ecmp.complaint` **or** boolean `ecmp_complaint_entitled` (SEC-ENT-REP-001) |
| EP-C-05 | Organization Reference Contract | Semantics & id opacity for `organization_id` / `branch_id` / `department_id`; resolvability SLA |
| EP-C-06 | Org Sync Integration Contract | Transport (pull/push/hybrid), cadence, payload shape ownership (Event Catalog entries if push — EP-authored) |
| EP-C-07 | Client Registration Record | ECMP API resource client + (if applicable) interactive RP client IDs; redirect/logout URIs for production domain |
| EP-C-08 | Board unlock | Written lift of C-7 / C-B6-1 for intended environment **after** contracts above |

---

## 2. Required configuration (values EP owns; ECMP consumes)

| Env / setting | Owner | Notes |
|---|---|---|
| `OIDC_ISSUER` | EP | Exact production issuer URL |
| `OIDC_AUDIENCE` | EP | ECMP-isolated audience (ADR-016 §10.4) |
| `OIDC_JWKS_URL` | EP | JWKS endpoint matching issuer |
| `OIDC_JWKS_CACHE_TTL_SECONDS` | Joint | EP may recommend; ECMP may set ops default |
| Discovery document URL | EP | If used instead of static JWKS |
| Token endpoint / end-session / revocation | EP | For RP-initiated flows if EP requires browser SSO |
| MFA policy | EP | Platform-owned; ECMP does not implement MFA product |
| Vault / secret delivery path for client secrets | EP / Ops | If confidential clients used |

**Forbidden:** ECMP inventing any row above to “pass” validators.

---

## 3. Required production evidence (from EP / joint with EP IdP)

| ID | Evidence |
|---|---|
| EP-E-01 | Sample production-shaped JWT (redacted) showing required ADR-015 claims + entitlement signal |
| EP-E-02 | JWKS fetchable from production network path ECMP will use |
| EP-E-03 | Negative cases documented: expired, wrong `aud`, missing entitlement, unresolvable org refs → expect deny |
| EP-E-04 | Test identities for smoke (named users + non-entitled control user) |
| EP-E-05 | Joint AuthN smoke result: login / token validation / refresh (or re-auth) against real IdP |

---

## 4. Required security artifacts

| ID | Artifact |
|---|---|
| EP-S-01 | Signed IdP trust statement (issuer of record, key rotation policy, contact) |
| EP-S-02 | Bilateral review / acceptance of SEC-BIND-OIDC-001, SEC-ENT-REP-001 (Draft → Accepted) |
| EP-S-03 | Security Officer / Architect sign-off for Mode B lab→staging→production path |
| EP-S-04 | Confirmation: AuthN ≠ entitlement; no default-allow |
| EP-S-05 | Incident / revoke / key-compromise runbook contact on EP side |

---

## 5. Required deployment artifacts

| ID | Artifact |
|---|---|
| EP-D-01 | Production DNS / network path: ECMP host → IdP issuer + JWKS (egress allowlist if required) |
| EP-D-02 | Registered redirect / post-logout URIs for `https://<ECMP_DOMAIN>/…` (EP RP console) |
| EP-D-03 | Audience / resource registration for ECMP API |
| EP-D-04 | Org directory sync endpoint or event feed reachable from ECMP runtime (per EP-C-06) |
| EP-D-05 | Environment promotion rules: which IdP realm/tenant is PROD vs non-PROD |

*(ECMP already owns compose overlay, Caddy, images `*:1.2.0-rc.1`, backup evidence — not EP scope.)*

---

## 6. Acceptance criteria — Platform Ready

All must be true:

- [ ] EP-C-01…EP-C-08 received and filed under `deploy/evidence/` (or Board-linked pointer)
- [ ] Real `OIDC_ISSUER` / `OIDC_AUDIENCE` / `OIDC_JWKS_URL` supplied (no placeholders)
- [ ] `python scripts/validate-production-config.py --env-file .env.prod --require-production` → **PASS**
- [ ] `docker compose -f docker-compose.prod.yml --env-file .env.prod config` → **PASS**
- [ ] EP-E-02…EP-E-05 completed (AuthN path against real IdP)
- [ ] Org refs resolvable per EP-C-05/06 **or** Board-waived with written residual risk (C-B6-3)
- [ ] Platform Readiness Review re-run → **PLATFORM READY**

---

## 7. Acceptance criteria — Ready for Release

All of §6 plus:

- [ ] REL-SEC-001 overall **GO** (Configuration + Authentication gates PASS)
- [ ] Production AuthN login/refresh smoke PASS; jwt recovery smoke unblocked
- [ ] REL-APR-001 required roles mark **Go** (Tech Lead, Security, Ops, Release Manager)
- [ ] Final Release Review → **READY FOR RELEASE**; tag `v1.2.0` authorized
- [ ] No invented OIDC; no CAP-008/FRD/OpenAPI/BR drift for this cutover

---

## Explicit non-asks (out of EP handover)

- Changes to Complaint domain, CAP-008, FRD, OpenAPI, Business Rules  
- ECMP becoming Customer / Org / Identity SoR  
- MFA / password / SSO product owned by ECMP  
- Fabricated Keycloak `localhost` realm as production contract  

## Decision

```text
WAITING FOR ENTERPRISE PLATFORM
```
