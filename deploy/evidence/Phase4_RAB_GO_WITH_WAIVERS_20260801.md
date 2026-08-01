# Phase 4 — Release Authorization Board (Re-session)
## Decision: GO WITH WAIVERS

| Field | Value |
|---|---|
| Date | 2026-08-01 |
| Session | Re-RAB after WP-01…WP-08 |
| Prior decision | NO-GO (2026-07-31) — superseded for execution scope below |
| Decision | **GO WITH WAIVERS** |
| Motion source | `RAB_Readiness_Memo_20260801.md` §2 option recommended |
| Decided by | Lab Operator acting as RAB chair (W-SOD-1) — chat mandate 2026-08-01 |

---

## Authorization Matrix (re-session)

| Req | Status | Notes |
|---|---|---|
| R1 DoR | **PASS WITH WAIVERS** | A-01…A-09 complete; A-10 = this GO |
| R2 Approval Matrix | **PASS (W-SOD-1)** | Single-operator SoD disclosed |
| R3 Evidence Pack | **PASS** | Pack 2026-08-01 |
| R4 Security | **WAIVED / CONDITIONAL** | Lab CONDITIONAL PASS; W-S03, W-S04, W-S05, W-S07 |
| R5 Deployment | **PASS (lab)** | Deploy sign-off 2026-08-01 |
| R6 Rollback | **PASS** | Rollback APPROVED |
| R7 Base SHA | **PASS** | `2bf779d` locked |
| R8 Split plans | **PASS** | Approved + DEFER constraint |
| R9 Residual risks | **PASS** | Accepted with conditions |
| R10 Product Owner | **PASS (W-SOD-1)** | Module scope only |

No item **NOT APPLICABLE**. Full unrestricted **GO** is **rejected**.

---

## Waiver Register (binding)

| ID | Description | Expiration | Mitigation |
|---|---|---|---|
| W-SOD-1 | Single lab operator holds multiple RACI roles | Until second named reviewer | Disclosed in all 20260801 sign-offs |
| W-S03 | `ENVIRONMENT=production` + local JWT (no Mode B) | 2026-09-30 or Mode B contract | Lab only; no Enterprise SSO claim |
| W-S04 | Caddy public `/docs*`,`/redoc*`,`/openapi.json` | 2026-09-30 or edge closed | Prefer non-dev app docs off; plan Caddy remove |
| W-S05 | XFF trust for rate-limit | Until multi-instance | Single VPS lab |
| W-S07 | Users admin UI privilege surface | Until SoT re-review | **DEFER** pick (WP-03) |
| W-D07 | `behind 14` remote commits unforensicked | Until forensics or explicit Board revisit | **No** bulk merge/rebase |
| W-EXEC-1 | Phase 5 limited to non-DEFER units only | Until WP-03 DEFER cleared by new compat review | See Authorized Scope |

---

## Authorized for Phase 5 (NOW)

**Authorized:** Release Execution **within** Phase 5 Runbook **and** this scope only.

1. Create release branch from base **`2bf779d`** (`origin/feature/cm-batch1-s2-persistence`).  
   Suggested name: `release/cm-batch1-vps-sync` (or agreed equivalent).  
2. Selective cherry-pick / port **only**:
   - Paths **ABSENT** on SoT (infra/evidence/new files) per Compat Review;  
   - Split Unit boundaries honored;  
   - **KEEP** `ad4a373` evidence OK;  
   - New files e.g. `rate_limit.py` / tests OK **if** they do not require overwriting **DEFER** files — if patch needs DEFER file, **stop** and escalate.  
3. Resolve conflicts without taking VPS version of **DEFER** paths.  
4. Smoke minimal for picked surfaces; record SHAs; open PR to SoT.  
5. Follow Rollback Pack on failure.

## Forbidden (still)

- Merge or rebase VPS `main` into SoT/`main`  
- Blind overwrite of WP-03 **DEFER** paths (users/*, auth/router bulk, api clients, `docker-compose.prod.yml` full replace, etc.)  
- Full Mixed five-commit promote as one bulk  
- Production Aggregate cutover / Enterprise Platform scope  
- Claiming Security **Production PASS** or Mode B complete  
- Force-push to SoT / `main`

## A-10

| Item | Result |
|---|---|
| Go for release branch + **limited** cherry-pick | **YES — GO WITH WAIVERS** |
| Go for full Mixed / DEFER overwrites | **NO** |

---

## Formal record

| Role | Name | Date | Signature |
|---|---|---|---|
| RAB Chair | Lab Operator (ribaxhut-sys) | 2026-08-01 | **GO WITH WAIVERS** |
| Release Manager | Lab Operator | 2026-08-01 | A-10 recorded |

Next action: execute Phase 5 Runbook **under Authorized Scope** (separate execution request).

—*End of Re-RAB decision*
