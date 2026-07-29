# Architecture Board Countersign Pack — ADR-012

| Field | Value |
|---|---|
| Document ID | GOV-CS-ADR-012 |
| Subject | Accept ADR-012 Target Authentication Architecture (Keycloak / OIDC) |
| Version | 1.0 |
| Date | 2026-07-29 |
| Prepared by | Lead Software Engineer / Security track |
| Audience | Architecture Board / Security Architect / Tech Lead |
| Status | 🟢 Countersigned — ADR-012 **Accepted** (TASK-PLATFORM-ADR012-ACCEPT-001 complete) |
| ADR | `05 Architecture Decision Records/ECMP_ADR_012_Target_Authentication_Architecture_v1.0.md` (Accepted) |
| Epic / Task | EPIC-PLATFORM / **TASK-PLATFORM-ADR012-ACCEPT-001** |
| BMR | `18 Architecture Governance/BACKEND_MASTER_ROADMAP.md` |

---

## One-page decision

**Ask:** Countersign **Accept ADR-012**. This unlocks Phase 0 of SEC-MIG-001 (decision complete). It does **not** authorize Keycloak coding, compose IdP deployment, or OpenAPI securityScheme changes — those remain gated to SEC-MIG-001 phases under normal DoR.

**Outcome (2026-07-29):** ADR-012 Status = **Accepted**. SEC-MIG-001 Phase 0 = **completed**. SEC-MIG Phase 1 is **dependency-unlocked** but **still requires separate Architecture approval** before any implementation.

### Locked decisions requested (from ADR-012)

| # | Decision |
|---|---|
| 1 | Protocol = **OIDC** (Auth Code + PKCE) for users; **OAuth2 client_credentials** for services |
| 2 | Baseline IdP = **Keycloak** (Option A) on ADR-010 Compose SIT/UAT baseline; managed IdP later = swap/broker, not app redesign |
| 3 | Access token = **RS256 JWT**, 15 min; refresh rotating 8h idle / 12h max; ID token not sent to APIs |
| 4 | JWT carries identity + **roles[]** + org scope; **permissions resolved in Core Platform** (ADR-008 SoT), not embedded |
| 5 | Local **`ECMP_AUTH_MODE=dev`** retained for DEV/CI only; **refuse start** with `dev` in shared env |
| 6 | Envelope semantics unchanged: invalid → **401**; no permission → **403** |
| 7 | SEC-AUTH-001 becomes normative **when this ADR is Accepted** |

### Explicit non-authorizations (TASK-PLATFORM-ADR012-ACCEPT-001)

This task is **governance only**. Completion **does not** authorize:

- Keycloak
- OIDC
- JWT changes
- `backend/app` code
- migrations
- OpenAPI changes
- CI changes
- Docker changes

Also remain blocked until separate phase approval:

- SEC-MIG-001 Phase 1+ (Keycloak container, JWT validator, SIT/UAT activation)
- ADR-010 SIT/UAT shared env go-live (still requires ADR-007 target active = Phase 3)
- EPIC-CM-F4, outbox publisher, Enterprise Master Customer HTTP, real AV
- Changing EX-20260729-01 Batch 1 lab exception scope

### Current implementation note (fact, not a scope change)

Production tree `backend/` already has **local password JWT login** (`/api/v1/auth/login`) for lab — distinct from ADR-007 historic “static env bearer” slice. ADR-012 remains the **target OIDC/IdP** decision for shared environments; accepting it does not remove or redesign lab login in this pack.

---

## Artifact set for Board

| Artifact | Role |
|---|---|
| ADR-012 v1.0 | Decision SoT (**Accepted**) |
| SEC-AUTH-001 | Target architecture (normative after Accept) |
| SEC-MIG-001 | Migration plan (Phase 0 complete; Phase 1+ still gated) |
| ADR-007 | Slice + target split — remains valid for slice/DEV |
| ADR-010 | SIT/UAT activation hard-gated on target auth |
| AuthN Limitations Register | Closure path points at ADR-012 artifacts |

---

## Open gates after Accept (checklist)

| Gate | Owner | Next action |
|---|---|---|
| Flip ADR-012 Status → 🟢 Accepted | Architecture Board Chair | ✅ Done — TASK-PLATFORM-ADR012-ACCEPT-001 (2026-07-29) |
| Flip SEC-MIG-001 / SEC-AUTH-001 readiness for Phase 1 DoR | Security Architect / Tech Lead | Separate sprint gate — **not this pack** |
| Solution Architecture §8 reference ADR-012 | Solution Architect | Follow-up editorial (ADR-012 follow-up list) |
| Phase 1 Keycloak baseline code | — | **Requires separate Architecture approval to start** (dependency-unlocked only) |

---

## Sign-off

| Role | Name | Date | Decision |
|---|---|---|---|
| Architecture Board Chair | | | ☐ Accept ADR-012 / ☐ Reject / ☐ Accept with conditions |
| Security Architect | | | ☐ |
| Solution Architect | | | ☐ |
| Tech Lead | | | ☐ |
| Business Owner (inform) | | | ☐ Noted |

**Conditions (if any):** _________________________________

**On Accept:** update ADR-012 Status to Accepted; do **not** start SEC-MIG Phase 1 until a dedicated implementation task is Board-approved.

**Governance status note:** Document Status above records **Countersigned — ADR-012 Accepted** for TASK-PLATFORM-ADR012-ACCEPT-001. Signature-row checkboxes are left unchanged per task execution mode (status-only metadata). Named wet-ink / named digital countersigns may be recorded later without changing the Accept outcome.

---

## Related paths

- `05 Architecture Decision Records/ECMP_ADR_012_Target_Authentication_Architecture_v1.0.md`
- `10 Security and Access Standards/ECMP_Target_Authentication_Architecture_v1.0.md`
- `10 Security and Access Standards/ECMP_AuthN_Migration_Rollout_Plan_v1.0.md`
- `18 Architecture Governance/BACKEND_MASTER_ROADMAP.md`

---

*End of GOV-CS-ADR-012. Completed under TASK-PLATFORM-ADR012-ACCEPT-001 — docs/governance only; no application code; no Keycloak / OIDC / JWT / migrations / OpenAPI / CI / Docker authorization.*
