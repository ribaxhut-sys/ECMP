# ECMP_ADR_012_Target_Authentication_Architecture_v1.0

| Field | Value |
|---|---|
| ID | ADR-012 |
| Version | 1.0 |
| Owner | Security Architect |
| Reviewer | Tech Lead / Solution Architect / Security Officer |
| Approver | Architecture Board |
| Status | 🟡 Proposed |
| Last Review | 2026-07-21 |
| Next Review | 2026-10-21 |

- ADR Status: Proposed
- Date: 2026-07-21
- Decision Owners: Security Architect, Tech Lead
- Related Domains: Core Platform (all domains consume)

## Context

ADR-007 split authentication into a **slice phase** (static env bearer tokens, DEV/CI only) and a **target phase** (JWT signed by an OIDC IdP), but deliberately left the target phase undesigned ("IdP/SSO selection = follow-up decision"). The repository assessment now flags Authentication as the **only Critical issue**: the slice mechanism has no expiry, no user store, no individual identity (limitations L-1, L-2 in `10 Security and Access Standards/ECMP_AuthN_Limitations_Register_v0.1.md`), and it blocks every shared environment (DEP-001 §1, ADR-010 §3 — SIT/UAT may only be activated after the ADR-007 target phase is active).

This ADR elaborates the ADR-007 target phase into a concrete architecture. It is a **design decision only** — no implementation is authorized by this ADR; implementation follows the migration plan (`10 Security and Access Standards/ECMP_AuthN_Migration_Rollout_Plan_v1.0.md`) and its own sprint gating.

## Decision Drivers

- Close Critical finding: replace static tokens with expiring, individually attributable, cryptographically verifiable credentials before any shared environment (hard gate in DEP-001 §1 / ADR-010 §3).
- AuthN/AuthZ must stay centralized in Core Platform (SA §8, BR-CP-01/02); Role-Permission SoT = Core Platform (ADR-008) — the token design must not create a second SoT.
- Deployment baseline for SIT/UAT is Docker Compose on one managed VM (ADR-010) — the IdP must be runnable there without a cloud dependency.
- Frontend is deferred (ADR-011) — the login flow must be designed now but its first consumer may be non-interactive (CI, API clients).
- Blueprint lists full SSO as Future Enhancement — the design must allow later federation to a corporate IdP without re-architecting.
- Keep dev experience: local development must keep working offline with the current dev-token mechanism.

## Options Considered

### Option A — Self-hosted OIDC IdP (Keycloak) — chosen
- Pros: runs in the ADR-010 compose baseline (no cloud dependency); full OIDC/OAuth2 (Authorization Code + PKCE, client_credentials, refresh rotation, RP-initiated logout, back-channel logout); built-in identity brokering → future SSO to corporate IdP without app change; free/OSS; user store included.
- Cons: one more container to operate (upgrades, backups, HA later); team must learn realm/client administration.

### Option B — Managed IdP (Microsoft Entra ID / Auth0 / Okta)
- Pros: no ops burden, mature MFA/conditional access, likely the eventual corporate SSO endpoint.
- Cons: procurement/budget decision not made (same trigger pattern as ADR-010 §4 PROD deferral); requires internet-reachable environments (SIT/UAT baseline is one VM); tenant governance outside team control; per-user licensing.

### Option C — Build own JWT issuer inside Core Platform
- Pros: no new component; full control.
- Cons: rebuilding an IdP (user store, password policy, token endpoints, key rotation, revocation) is high-risk security engineering with no differentiating value; contradicts "security by default" (AI-RULES §9); rejected.

## Decision

1. **Protocol standard, not vendor lock**: ECMP authenticates users via **OIDC (Authorization Code + PKCE)** and services via **OAuth2 client_credentials**. All ECMP-side validation uses only standard OIDC/OAuth2 surfaces (discovery document, JWKS, token/revocation/logout endpoints) so the IdP is swappable.
2. **Baseline IdP = Keycloak (Option A)**, deployed as a container in the ADR-010 compose baseline for SIT/UAT. Moving to a corporate/managed IdP (Option B) later is an IdP swap or brokering decision, not an application change (see §Future SSO in the architecture doc).
3. **Token model**: RS256-signed JWT access tokens validated by ECMP on every request (signature via cached JWKS, `iss`, `aud`, `exp`, `nbf`); access token lifetime **15 minutes**; refresh tokens **rotating, 8h idle / 12h max session, reuse detection**; ID token only for login-session establishment, never sent to ECMP APIs.
4. **RBAC integration**: JWT carries **identity + roles + org scope** (`sub`, `preferred_username`, `roles[]`, `orgUnitId`, `sid`). **Permissions are NOT embedded in the token** — Core Platform resolves `roles[] → permissions{}` at request time from the Role-Permission matrix (SoT per ADR-008, cached with short TTL). This keeps tokens small, keeps permission changes effective within cache-TTL instead of token-TTL, and preserves the single SoT.
5. **Dev-token mechanism is retained for local DEV/CI only**, behind an explicit mode switch (`ECMP_AUTH_MODE=dev|jwt`); the application **must refuse to start** with `dev` mode in any shared environment. Limitations L-1/L-2 stay registered until Phase 3 of the migration plan closes them.
6. **Semantics unchanged**: missing/invalid/expired token → **401 UNAUTHENTICATED**; valid token without permission → **403 FORBIDDEN** (ADR-007 §4, error envelope unchanged).
7. Full architecture (flows, claims schema, sequences, service-to-service, logout) is specified in `10 Security and Access Standards/ECMP_Target_Authentication_Architecture_v1.0.md` (SEC-AUTH-001), which is normative once this ADR is Accepted.

## Consequences

### Positive
- Unblocks SIT/UAT activation gate (ADR-010 §3 / DEP-001 §1).
- Individual identity (`sub`) enables real audit attribution (BR-008) and later read-audit decisions (OQ-007).
- `orgUnitId` claim provides the enforcement hook for BR-CP-02 org-unit scoping (closes limitation L-3 path, gate G1).
- OIDC-standard-only coupling keeps future SSO (Blueprint Future Enhancement) an infrastructure change, not an application change.

### Negative / Trade-offs
- New operational component (IdP) in SIT/UAT: backups, upgrades, availability become part of the runbook (`15 Operations Runbook`).
- Permission resolution per request adds a lookup (mitigated by short-TTL cache; measured in NFR terms before UAT).
- Access tokens remain valid up to 15 min after logout/role change (accepted; revocation denylist explicitly NOT built in baseline — documented trade-off in SEC-AUTH-001 §Logout).
- Two auth modes exist during migration; guarded by fail-fast environment checks (risk R-1 in migration plan).

### Follow-up Actions
- [ ] Architecture Board review → move Status to Accepted
- [ ] Update Solution Architecture §8 (Security Architecture) to reference ADR-012 / SEC-AUTH-001
- [ ] Execute migration plan phases (SEC-MIG-001) — implementation NOT authorized by this ADR alone
- [ ] Update `ECMP_AuthN_Limitations_Register` closure column (done in this change: closure now points to ADR-012 artifacts)
- [ ] OpenAPI `securitySchemes` description update when Phase 2 implementation starts (contract change goes through `07 API Catalog` per AI-RULES §2)

## Related
- ADR-007 (slice + target split — this ADR elaborates the target phase; ADR-007 remains valid for the slice phase)
- ADR-008 (RBAC SoT = Core Platform), ADR-010 (deployment baseline), ADR-011 (frontend deferral)
- `10 Security and Access Standards/ECMP_Target_Authentication_Architecture_v1.0.md` (SEC-AUTH-001)
- `10 Security and Access Standards/ECMP_AuthN_Migration_Rollout_Plan_v1.0.md` (SEC-MIG-001)
- `10 Security and Access Standards/ECMP_AuthN_Limitations_Register_v0.1.md`, `ECMP_Role_Access_Matrix_v0.1.md`
