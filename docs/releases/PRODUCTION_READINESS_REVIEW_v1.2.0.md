# ECMP Production Readiness Review — v1.2.0 (re-run)

| Field | Value |
|---|---|
| ID | PRR-v1.2.0-RERUN |
| Date | 2026-08-01 |
| Candidate | `v1.2.0-rc.1` @ `6890f50` |
| Controlling gate | REL-SEC-001 |
| Status | **ISSUED (re-run)** |
| Cutover decision | **NO-GO** |

> No features / FRD / OpenAPI / CAP-008 / Business Rules changes.  
> OIDC values were **not** fabricated.

## Closure attempt summary

| Blocker (prior) | This pass |
|---|---|
| `.env.prod` validation (8 issues) | Reduced to **5** AuthN/OIDC-only; non-AuthN hygiene **closed** |
| Compose ACME_EMAIL | **Closed** (fallback + host keys) |
| Compose OIDC required vars | **Open** (needs real contract) |
| Backup evidence | **Closed** (`-Fc` + SHA-256) |
| Recovery evidence | **Documented**; prod jwt smoke **open** |
| REL-APR ops evidence | **Pack complete**; marks remain **No-Go** |

## REL-SEC-001 re-score

| Gate | Result |
|---|---|
| Configuration | **FAIL** |
| Authentication | **FAIL** |
| Authorization | **PASS** |
| Audit | **PASS (lab ack)** |
| Backup | **PASS** |
| Recovery | **FAIL for prod cut** |
| Smoke | **PASS lab only** |
| **Overall** | **NO-GO** |

## Decision

```text
PRODUCTION CUTOVER: NO-GO
FINAL TAG v1.2.0:    NOT AUTHORIZED
CANDIDATE REMAINS:   v1.2.0-rc.1
HARD BLOCKER:        Bilateral IdP contract (OIDC) — do not invent
```

## Related

- `deploy/evidence/PROD_CFG_CLOSURE_v1.2.0_20260801.md`
- `deploy/evidence/REL_SEC_001_v1.2.0_Assessment_20260801.md`
- `deploy/evidence/FINAL_RELEASE_REVIEW_v1.2.0_20260801.md`
- `deploy/evidence/Mode_B_Blocked_Pending_IdP_Contract_20260801.md`
