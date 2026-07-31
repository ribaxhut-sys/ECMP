# Residual Risk Acceptance Template (R9 / A-04)

| Field | Value |
|---|---|
| Date | 2026-07-31 |
| Status | **UNSIGNED** |
| Rule | RAB will not accept residual risk without written acceptance |

| ID | Risk | Severity | Accept? (Yes/No) | Conditions / mitigation | Approver |
|---|---|---|---|---|---|
| RR-1 | Base SHA not locked | High | | Lock via `Base_SHA_Lock_*` | Tech Lead + RM |
| RR-2 | 14 remote commits outside forensics | High | | Keep no bulk merge/rebase; cherry-pick only | Governance Board |
| RR-3 | VPS↔Batch-1 content overlap on 13 paths | High | | Content review before each EXISTS pick | Tech Lead |
| RR-4 | Security/Deploy review incomplete | High | | Complete S-* / D-* sign-off | Sec + Deploy |
| RR-5 | Mixed commits without approved split | Medium–High | | Approve `Split_Plans_*` | Tech Lead |
| RR-6 | Release-level rollback not approved | Medium | | Approve `Rollback_Pack_*` | Deploy + RM |
| RR-7 | Evidence pack incomplete | Medium | | Complete unsigned sheets + A-08 | Release Manager |

## Board acceptance block (RR-2 minimum for G6)

| Role | Name | Date | Accept RR-2? | Notes |
|---|---|---|---|---|
| Governance Board | _pending_ | | Yes / No | |

## Product Owner (R10 / A-09)

| Statement | Name | Date | Decision |
|---|---|---|---|
| Scope remains Complaint Module / lab sync; no platform sprawl | _pending_ | | Approve / Reject |
