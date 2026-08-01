# ECMP AuthN Migration & Rollout Plan v1.0

| Field | Value |
|---|---|
| ID | SEC-MIG-001 |
| Version | 1.0 |
| Owner | Security Architect |
| Reviewer | Tech Lead / DevOps Lead / Security Officer |
| Approver | Architecture Board |
| Status | 🟢 Phase 0–1 complete (Phase 2+ still approval-gated) |
| Last Review | 2026-07-29 |
| Next Review | 2026-10-21 |

## Purpose

Migration strategy, risk register, and rollout plan for moving from the ADR-007 slice authentication (static dev tokens) to the ADR-012 target architecture (SEC-AUTH-001). **This document plans work; it does not authorize implementation.** Each phase enters a sprint through normal gating (DEC-002 / DoR) and respects AI-RULES (contract-first, traceability sync).

## 1. Migration Strategy

Guiding principles:

1. **Strangler, not big-bang** — the JWT path is added *beside* the dev-token path behind one mode switch (`ECMP_AUTH_MODE`); dev mode is never modified, only fenced. Endpoint code is untouched because the principal shape `{userId, roles, permissions, orgUnitId}` is a superset of today's `{userId, permissions}` and the `need(perm)` dependency contract is stable.
2. **Fail-closed everywhere** — unknown role → empty permissions; `dev` mode in shared env → startup refusal; JWKS unavailable + uncached key → 401, never bypass.
3. **Contract-first** — OpenAPI `securitySchemes` description and the AuthN Limitations Register are updated in the same change as each phase (AI-RULES §2, §13).
4. **Dev experience preserved** — local DEV and CI keep static tokens by default; JWT locally is an opt-in compose profile.

### Phases

| Phase | Deliverable | Exit criteria | Closes |
|---|---|---|---|
| **0 — Decision** (this change) | ADR-012, SEC-AUTH-001, SEC-MIG-001 reviewed by Architecture Board | ADR-012 status = Accepted | — |
| **1 — IdP baseline** | Keycloak container in `implementation/infrastructure` compose (profile `auth`); realm-as-code export (`ecmp` realm, clients per SEC-AUTH-001 §2.2, roles per Role Access Matrix); no app change | Realm import reproducible from repo; admin runbook drafted in `15 Operations Runbook` — **DONE** (`TASK-PLATFORM-SECMIG-P1-001`, 2026-07-29) | — |
| **2 — JWT validation path** | `ECMP_AUTH_MODE` switch; JWT validator (JWKS cache, iss/aud/exp/nbf); role→permission resolver over the existing matrix; startup guard (`dev` mode forbidden when `ECMP_ENV` shared); contract tests for 401/403 in both modes | CI green with both modes exercised; OpenAPI description updated; 401/403 semantics byte-identical to slice envelope | L-1, L-2 (design-complete) |
| **3 — SIT/UAT activation** | Deploy compose baseline (ADR-010 §3) with `jwt` mode only; real named users in IdP; secrets via env secret store (DEP-001 §2); smoke tests via `ecmp-ci` client | UAT users log in via OIDC; dev tokens rejected in SIT/UAT; Limitations Register rows L-1/L-2 marked closed | **L-1, L-2** |
| **4 — Org scoping (gate G1)** | `orgUnitId` claim populated from IdP user attributes; BR-CP-02 enforcement in permission check (SEC-AUTH-001 §7.5 note) | Cross-unit access tests pass per Role Access Matrix planned section | **L-3** |
| **5 — Hardening (pre-PROD)** | Refresh rotation verification, key-rotation drill, back-channel logout decision, IdP backup/restore drill, PROD IdP choice (with ADR-010 §4 platform ADR) | Threat Model (SEC-TM) re-review; pen-test findings triaged | L-5 (vault, with DEP-001) |

Explicit non-goals of this migration: building a frontend (ADR-011 stands — Phase 2 is testable via token endpoint + API calls), choosing the PROD platform (ADR-010 §4), introducing a message broker (ADR-009).

### Compatibility & data migration

- **No user data migration**: dev principals (`cs.agent.1`, `viewer.1`, `noperm.1`) are synthetic and stay dev-only. IdP users are created fresh (SIT/UAT: named team members; PROD: per joiner process, BR-ADM-01 approval).
- **Audit continuity**: audit `actor` becomes IdP `sub`; dev-mode audit rows keep the fixed principal ids. No retroactive rewrite (append-only, BR-008).
- **Role names**: token roles use snake_case (`cs_agent`) mapped 1:1 to Role Access Matrix rows; the matrix document gains a "token role name" column in Phase 2 (matrix revision, not a new SoT).
- **Rollback**: SIT/UAT before go-live can temporarily fall back only by redeploying with the dev-token build tag *and* taking the environment private again (dev mode in shared env stays forbidden — rollback = environment de-activation, not a mode flip).

## 2. Risks

| # | Risk | L | I | Mitigation | Residual owner |
|---|---|---|---|---|---|
| R-1 | Dual auth modes: `dev` mode accidentally enabled in shared env | M | **Critical** | Startup refusal on `ECMP_AUTH_MODE=dev` + shared `ECMP_ENV`; CI test asserts the refusal; deploy pipeline sets mode explicitly | DevOps Lead |
| R-2 | IdP becomes single point of failure for login | M | H | Offline JWT validation keeps issued tokens working (§6 SEC-AUTH-001); JWKS cached; IdP restart runbook; HA deferred to PROD ADR | Ops |
| R-3 | Keycloak operational unfamiliarity (upgrades, backup, realm drift) | H | M | Realm-as-code in repo (import on deploy); pin image version; upgrade procedure in `15 Operations Runbook`; drill in Phase 5 | Tech Lead |
| R-4 | Role→permission resolver cache serves stale permissions after revocation | M | M | TTL ≤60 s; document the window in Security Standards; admin bulk-changes trigger cache flush endpoint (design detail Phase 2) | Security Officer |
| R-5 | Residual access-token validity after logout (≤15 min) violates a future compliance need | L | M | Documented trade-off (SEC-AUTH-001 §7.4); `sid` already in claims → back-channel logout is additive (Phase 5 decision) | Security Architect |
| R-6 | Refresh-token theft | L | H | Rotation + reuse detection revokes session; tokens never in localStorage if BFF path chosen (frontend ADR follow-up) | Security Architect |
| R-7 | Claim contract drift when corporate SSO is brokered in later | M | M | Claims contract frozen in SEC-AUTH-001 §3; brokering maps corp groups → same roles; contract tests validate claims shape | Solution Architect |
| R-8 | IdP admin console exposed on shared VM | M | H | Console bound to management network/VPN only; strong admin credentials in secret store; audit realm admin actions | DevOps Lead |
| R-9 | Migration stalls and dev tokens live in UAT "temporarily" | M | **Critical** | Hard gate already exists (DEP-001 §1 / ADR-010 §3): SIT/UAT may not be activated at all until Phase 3 — there is no interim state with dev tokens on a shared env | Architecture Board |
| R-10 | Latency regression from per-request permission resolution | L | L | In-process cache; measure against NFR budget in Phase 2 CI perf smoke; matrix is tiny (≤ dozens of rows) | Tech Lead |

(L/I = likelihood / impact: L, M, H, Critical.)

## 3. Rollout Plan

Rollout follows environment order DEV(opt-in) → CI(contract tests) → SIT → UAT → PROD, mapped onto the phases:

| Step | Environment | Action | Gate to proceed |
|---|---|---|---|
| 1 | — | Architecture Board reviews ADR-012 (+ this plan) | ADR-012 Accepted |
| 2 | Local DEV | Compose profile `auth` with Keycloak + realm import; developers may opt in to `jwt` mode | Realm reproducible from repo (Phase 1 exit) |
| 3 | CI | Both-mode contract tests: dev-mode suite unchanged; jwt-mode suite (valid/expired/wrong-aud/wrong-iss/no-perm) | CI green both modes (Phase 2 exit) |
| 4 | SIT | First shared env activation per ADR-010 §3 — `jwt` only, named users, secret store | Smoke + security checklist pass (Phase 3 exit); Limitations L-1/L-2 closed |
| 5 | UAT | Business users onboarded (BR-ADM-01 approval trail); UAT scripts run under real identities | UAT sign-off; audit shows individual `sub` attribution |
| 6 | UAT | Enable org scoping (`orgUnitId`, BR-CP-02) at gate G1 | Cross-unit tests pass (Phase 4 exit); L-3 closed |
| 7 | PROD | Only after ADR-010 §4 trigger: PROD platform ADR decides hardened Keycloak vs managed IdP; Phase 5 hardening complete | Pen-test triage done; ops drills done |

Communication & sync obligations per step (AI-RULES §10, §13): update Limitations Register closure column, Role Access Matrix (token role names), OpenAPI securityScheme description, Traceability (`26`), and Ops Runbook in the same change as the phase that affects them.

**No-regression guarantee for developers:** at every step, `ECMP_AUTH_MODE=dev` on a laptop with `.env` tokens keeps working exactly as today; nothing in this rollout removes the slice mechanism from local DEV/CI.

## Related
- ADR-012, SEC-AUTH-001 (`ECMP_Target_Authentication_Architecture_v1.0.md`)
- ADR-007, ADR-010 (activation gate), DEC-002 (sprint gating)
- `ECMP_AuthN_Limitations_Register_v0.1.md` (L-1..L-5), `ECMP_Threat_Model_v0.1.md`, `14 Deployment Standards`
