# Decision Record — Lab auth: local JWT now, SSO later as target

| Field | Value |
|---|---|
| ID | DEC-020 |
| Version | 1.0 |
| Owner | Product / Ops |
| Reviewer | Solution Architect |
| Approver | Business Owner |
| Status | 🟢 Accepted (ops working agreement) |
| Last Review | 2026-07-31 |
| Next Review | 2026-10-31 |

- Type: Project Decision (non-ADR)
- Status: Accepted
- Date: 2026-07-31
- Context host: VPS lab → planned URL `https://pengaduan.layanankami.tech`

## Context

ECMP foundation lab runs on Docker Compose with **local JWT** users (no IdP).
Stakeholders want a public subdomain later and mentioned SSO “as temporary login”.
That phrasing conflicts with ADR-007 / ADR-012 (SSO/OIDC is the **target** auth path, not a stopgap).

## Options

- **A.** Build SSO/OIDC now alongside subdomain cutover.
- **B.** Keep local JWT for lab and first HTTPS cutover; plan SSO/OIDC as a **later target** phase (not “temporary”).
- **C.** Use SSO only as a short-lived temporary login, then replace again.

## Decision

**Opsi B.**

1. **Now:** local username/password + JWT (seed/lab users in Postgres). Suitable for Mode A lab and initial `pengaduan.layanankami.tech` behind Caddy.
2. **Later:** introduce SSO/OIDC per ADR-007 target / ADR-012 (e.g. Keycloak or corporate IdP) as the **intended** shared-environment login — not a temporary bridge.
3. **Out of scope for current VPS cutover:** Mode B enterprise SSO coding, IdP procurement, and MFA product features.

## Rationale

- Unblocks subdomain + TLS without expanding auth scope.
- Aligns with existing ADRs (SSO = Future Enhancement / target phase).
- Avoids building and discarding an IdP “temporary” stack.

## Impact

- Deploy edge: `deploy/Caddyfile` + `docker-compose.prod.yml` (no SSO services).
- Lab credentials remain operational until an SSO migration runbook is accepted.
- Any SSO work requires a separate decision/ADR activation — do not mix into Mode A compose without sign-off.

## Related

- ADR-007 Authentication Model
- ADR-012 Target Authentication Architecture
- `deploy/README.md` (subdomain cutover)
