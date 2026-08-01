# REL-SEC-001 Assessment — ECMP v1.2.0 (re-run after blocker closure attempt)

| Field | Value |
|---|---|
| Template | `16 Release Management/ECMP_Release_Security_Gate_v1.0.md` |
| Candidate | `v1.2.0-rc.1` @ `6890f50d8243ba30589a3d88f0c0efcef791ce01` |
| Re-run date | 2026-08-01 |
| Assessor | Production Readiness Team |
| Prior score | NO-GO (first PRR) |
| Overall | **NO-GO** |

> Conditional Go forbidden. OIDC not invented (Mode_B_Blocked / W-S03).

## Gate scorecard (re-run)

| # | Gate | Result | Delta vs prior | Evidence |
|---|---|---|---|---|
| 1 | Configuration Validation | **FAIL** | Improved 8→5 issues; remaining all AuthN | `PROD_CFG_CLOSURE_v1.2.0_20260801.md` |
| 2 | Authentication Validation | **FAIL** | Unchanged hard block | No bilateral IdP; `ECMP_AUTH_MODE=dev` on host `.env.prod` |
| 3 | Authorization Validation | **PASS** | Unchanged | 169 security tests |
| 4 | Audit Validation | **PASS (lab ack)** | Unchanged | Platform audit tables; CAP-008 side effects |
| 5 | Backup Validation | **PASS** | **Closed** | `OPS_BAK_EVID_v1.2.0_20260801.md` (`-Fc` + SHA-256) |
| 6 | Recovery Validation | **FAIL for prod cut** | Evidence completed; jwt smoke still blocked | `OPS_RCV_EVID_v1.2.0_20260801.md` |
| 7 | Smoke Validation | **PASS (lab Mode A only)** | Unchanged | `/live` `/ready`; CAP-008 lab lifecycle |

**Overall:** **NO-GO**

## Closed this pass

- ACME email compose/env hygiene  
- Email provider + password-reset URL alignment  
- Version pins on host `.env.prod`  
- Full `.env.prod.example` production template  
- Candidate-bound `-Fc` backup + checksum  
- Recovery evidence pack + REL-APR ops evidence  

## Still blocking GO

1. Real IdP contract → `jwt` + `OIDC_*` + local-credential off  
2. `docker compose … prod config` until OIDC vars present  
3. Production AuthN login/refresh + recovery smoke under jwt  
4. REL-APR-001 Go marks (blocked by above)
