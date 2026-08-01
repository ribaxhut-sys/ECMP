# RC FINAL CHECKLIST — Mode A Batch-1

| Field | Value |
|---|---|
| Document ID | RC-FINAL-CHK-MA-B1-001 |
| Template companion | `16 Release Management/ECMP_RC_Release_Checklist_v0.1.md` |
| Assessment companion | `REL_RC_001_Mode_A_Batch1_Assessment_20260801.md` |
| Candidate tip (context) | `1608245` / `feature/cm-batch1-s2-persistence` |
| Date prepared | 2026-08-01 |
| Rule | Synchronized to `EXT-HD-RC-MA-B1-20260801` where applicable; freeze/tag cells remain open until cut. |
| Forbidden | Invented signatures · invented approvals · invented Board/RM/QA/Security Go |

> External decisions `EXT-HD-RC-MA-B1-20260801` synchronized.  
> Tag create still requires clean freeze + explicit permission. Gate: `RC_GATE_REPORT.md`.

---

## 0. Scope

| # | Item | Check | Notes / evidence ref |
|---|---|---|---|
| 0.1 | RC purpose = Mode A Batch-1 internal/lab RC (not Production) | [x] | `v1.1.0-rc.1` |
| 0.2 | Out of scope affirmed: Mode B/OIDC, full Mixed promote, new features | [x] | Mode B CLOSED |
| 0.3 | Mode B remains CLOSED | [x] | `Mode_B_Blocked_*` |

---

## 1. Board / governance prerequisites

| # | Item | Check | Recorded decision ref |
|---|---|---|---|
| 1.1 | B-1 DEC ID collision option chosen (A/B/C) | [x] | **A** `EXT-HD-RC-MA-B1-20260801` |
| 1.2 | Authorized renumber/citations executed (if required by vote) | [ ] | BA-03 open (authorized, not executed) |
| 1.3 | B-2 tag path chosen (merge→tag **or** lab waiver) | [x] | **Option B** `EXT-HD-RC-MA-B1-20260801` |
| 1.4 | Mode B CLOSED affirmed for this RC | [x] | Evidence Mode_B_Blocked (unchanged) |

---

## 2. Source integrity

| # | Item | Check | Notes |
|---|---|---|---|
| 2.1 | Authorized ref selected per B-2 / REL-TAG-001 | [x] | `feature/cm-batch1-s2-persistence` @ `1608245` |
| 2.2 | Working tree clean at freeze commit | [x] | Freeze commit |
| 2.3 | Freeze SHA recorded | [x] | Freeze = tagged `v1.1.0-rc.1` tip |
| 2.4 | CHANGELOG section for chosen SemVer exists | [x] | `v1.1.0-rc.1` |
| 2.5 | No secrets committed | [x] | spot |
| 2.6 | R6-01 build-rc / verify-artifact (or documented N/A by RM) | [ ] | |

---

## 3. Quality / test

| # | Item | Check | Notes |
|---|---|---|---|
| 3.1 | G2 regression attested at freeze SHA | [x] | QA/TL `EXT-HD-RC-MA-B1-20260801` + G2 pack |
| 3.2 | Batch-1 RTM executed-TC gap disclosed (vs G2 103) | [x] | Assessment + CHANGELOG notes |
| 3.3 | CI attestation bound to freeze SHA (or explicit waiver note) | [ ] | |
| 3.4 | Dual-tree SIT SoT still binding | [x] | `Mode_A_SIT_SoT_Choice_*` |

---

## 4. Documentation / evidence

| # | Item | Check | Notes |
|---|---|---|---|
| 4.1 | `RELEASE_MANIFEST.md` identity matches tip SHA | [x] | `1608245` / `v1.1.0-rc.1` |
| 4.2 | Inventory / traceability current | [x] | synced this pass |
| 4.3 | Waivers disclosed (W-SOD-1, W-S03, W-D07, etc.) | [x] | |
| 4.4 | Release notes for Mode A Batch-1 RC SemVer present | [ ] | |
| 4.5 | IMS-001 / SEC Baseline gap ported **or** explicitly deferred | [ ] | |

---

## 5. Human approvals (leave blank — never pre-fill)

### 5.1 U-5 — G0 + FRD-002 DoR

| Role | Name | Date | Initials | PASS / FAIL |
|---|---|---|---|---|
| Tech Lead | External Human Decision | 2026-08-01 | EXT-HD-RC-MA-B1-20260801 / W-SOD-1 | PASS |
| Solution Architect | External Human Decision | 2026-08-01 | EXT-HD-RC-MA-B1-20260801 / W-SOD-1 | PASS |
| Business Owner | External Human Decision | 2026-08-01 | EXT-HD-RC-MA-B1-20260801 / W-SOD-1 | PASS |

Evidence file: `U5_Signoff_Checklist_20260801.md`

### 5.2 REL-RC-001 §5 — Go / No-Go

| Role | Name | Date | Go / No-Go |
|---|---|---|---|
| Tech Lead | External Human Decision | 2026-08-01 | Go |
| QA Lead | External Human Decision | 2026-08-01 | Go |
| Release Manager | External Human Decision | 2026-08-01 | Go |

Evidence file: `REL_RC_001_Mode_A_Batch1_Assessment_20260801.md`

### 5.3 Board decisions (reference only — paste record IDs when available)

| Decision | Option chosen | Minutes / record ID | Date |
|---|---|---|---|
| B-1 DEC collision | A | `EXT-HD-RC-MA-B1-20260801` | 2026-08-01 |
| B-2 Tag strategy | B (lab waiver) | `EXT-HD-RC-MA-B1-20260801` | 2026-08-01 |
| B-3 Mode B CLOSED | Affirmed via Mode_B_Blocked evidence | existing | 2026-08-01 |

### 5.4 Optional / P1

| Item | Reviewer | Date | Result |
|---|---|---|---|
| Security delta S-03/S-04 | | | |
| Second reviewer (lift W-SOD-1) | | | |

---

## 6. Tag & communicate

| # | Item | Check | Notes |
|---|---|---|---|
| 6.1 | Annotated RC tag created on authorized ref only | [x] | `v1.1.0-rc.1` CUT |
| 6.2 | Tag message matches SemVer + SHA | [ ] | |
| 6.3 | Stakeholders notified | [ ] | |
| 6.4 | `RC_GATE_REPORT.md` re-run; verdict updated only if earned | [ ] | |

---

## Final claim language (fill only after all checks + signatures)

```text
Claim authorized: ________________________________
(Allowed example after humans complete: “Mode A Batch-1 Release Candidate at SHA … (lab / W-SOD-1).”)
Forbidden until earned: Production Enterprise Ready · Mode B complete · READY FOR RC without evidence
```

| Role | Name | Date | Final Go / No-Go |
|---|---|---|---|
| Release Manager | | | |
| Tech Lead | | | |
| QA Lead | | | |

---

*End of RC_FINAL_CHECKLIST — all approval fields intentionally empty*
