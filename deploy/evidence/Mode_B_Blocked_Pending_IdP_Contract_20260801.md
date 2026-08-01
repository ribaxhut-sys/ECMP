# Mode B Enablement — BLOCKED pending real IdP contract

| Field | Value |
|---|---|
| Date | 2026-08-01 |
| Status | **BLOCKED** (Board C-7 — Mode B / Batch-2 / Enterprise customer CLOSED) |
| Priority item | Post-P5 #6 |
| SoT ADR | ADR-014 v1.4 + ADR-015 v1.3 (Accepted with Conditions; Implementation Deferred) |

## Evidence

- Config gates for `ECMP_AUTH_MODE=jwt` + `OIDC_*` **exist** in `backend/app/core/config.py`.  
- ADR-015 is Accepted architecture but **Implementation Deferred**; bilateral platform artefacts (issuer of record, JWKS, entitlement mapping signed by platform owner) are **not** present as verified production SoT in this lab.  
- Lab/self-provisioned realm references must not be treated as Enterprise Platform contract.

## Allowed now

- Continue lab Mode A / documented waivers.  
- Prepare checklists for Mode B cutover.

## Forbidden now

- Inventing production `OIDC_ISSUER` / realm as if platform-approved.  
- Setting `ENVIRONMENT=production` with fabricated OIDC to “pass” gates.  
- Claiming Enterprise SSO / Mode B complete.

## Unblock criteria

1. Board lifts C-7 / Mode B Closed for the intended environment.  
2. Written bilateral IdP contract evidence aligned to ADR-015.  
3. Security sign-off for Mode B lab→staging.  
4. Configure OIDC_* and run `scripts/validate-production-config.py --require-production`.
