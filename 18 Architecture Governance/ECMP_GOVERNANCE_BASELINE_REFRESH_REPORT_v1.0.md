# ECMP Governance Baseline Refresh Report v1.0

| Field | Value |
|---|---|
| Document ID | GOV-REFRESH-001 |
| Program | PROGRAM-GOVERNANCE-001 |
| Version | 1.0 |
| Date | 2026-07-30 |
| Prepared by | ECMP Documentation Administrator |
| Audience | Architecture Board / Solution Architect / PMO |
| Status | 🔴 Recorded — **FAIL** |
| Scope | Repository hygiene only — no architecture redesign, no implementation |

---

## 1. Executive Summary

PROGRAM-GOVERNANCE-001 executed **partial** governance baseline refresh against recorded Board Resolutions.

| Input | Repository presence | Used |
|---|---|---|
| PROGRAM-BOARD-004 | **Present** (`ECMP_PROGRAM_BOARD_004_Architecture_Board_Resolution_v1.0.md`) | Yes — ADR-014/015 Accept With Conditions hygiene |
| PROGRAM-BOARD-005 | **MISSING** | No — registration blocked |
| PROGRAM-BOARD-006 | **MISSING** | No — ADR-016/017/018 Accept flip blocked |

**Verdict: FAIL**

Reason: mandatory inputs PROGRAM-BOARD-005 and PROGRAM-BOARD-006 are absent. Documentation Administrator must not invent Board Review conditions (C-1′…C-11′) or Accept dispositions for ADR-016/017/018.

Partial BOARD-004 C-1 / F-2 hygiene **was** executed (authorized and overdue). Mode B / Batch-2 / Enterprise customer / OpenAPI / AuthN–AuthZ coding remain **CLOSED / not granted**.

---

## 2. Updated Files

| Path | Change type | Notes |
|---|---|---|
| `05 Architecture Decision Records/ECMP_ADR_014_ECMP_Enterprise_Business_Module_v1.4.md` | Metadata only | Lifecycle → **Accepted with Conditions** (BR-009); badge Approved; Mode B Closed noted |
| `05 Architecture Decision Records/ECMP_ADR_015_Enterprise_Identity_Contract_v1.3.md` | Metadata only | Lifecycle → **Accepted with Conditions** (BR-010); Bilateral Contract (C-3); Mode B Closed |
| `05 Architecture Decision Records/README.md` | Index hygiene | ADR-014/015 Accepted with Conditions; ADR-016/017/018 remain Proposed |
| `05 Architecture Decision Records/ADR_INDEX.generated.md` | Regenerated | Via `python tools/ear_repo_check.py --write-adr-index` |
| `docs/architecture/adr-index.md` | Portal mirror sync | v0.6; reflects BOARD-004; notes missing BOARD-006 |
| `18 Architecture Governance/README.md` | Registration attempt | BOARD-004 linked; BOARD-005/006 marked **MISSING** |
| `18 Architecture Governance/ECMP_PROGRAM_ADR_002_Board_Resolutions_v1.0.md` | Traceability hygiene | BR-005/BR-006 + PROGRAM-ADR-004 pending disposition marked **historical**; active = BR-009/BR-010 |
| `18 Architecture Governance/ECMP_GOVERNANCE_BASELINE_REFRESH_REPORT_v1.0.md` | Created | This report |

### Explicitly not modified (by design)

| Item | Reason |
|---|---|
| ADR-014 / ADR-015 normative decision bodies | No architecture rewrite |
| ADR-016 / ADR-017 / ADR-018 metadata Accept flip | PROGRAM-BOARD-006 missing — inventing Accept forbidden |
| OpenAPI / implementation / Mode B artifacts | Out of scope; C-7 CLOSED |

---

## 3. Archived Files

| Archived path | Prior role | Canonical head |
|---|---|---|
| `05 Architecture Decision Records/archive/ECMP_ADR_014_ECMP_Enterprise_Business_Module_v1.3.md` | Historical revision | `…_v1.4.md` |
| `05 Architecture Decision Records/archive/ECMP_ADR_015_Enterprise_Identity_Contract_v1.2.md` | Historical revision | `…_v1.3.md` |

Historical banners prepended. Folder `archive/` is skipped by `ear_repo_check` collectors.

### Archive gaps (recorded)

| Expected per PROGRAM-BOARD-004 C-1 supersession table | Result |
|---|---|
| `ECMP_ADR_014_…_v1.0.md` | **Not found** in ADR folder at refresh time (already absent) |
| `ECMP_ADR_015_…_v1.0.md` | **Not found** in ADR folder at refresh time (already absent) |

No delete of canonical v1.4 / v1.3 heads.

---

## 4. Registration Status — Board Programs

| Program | Expected artifact | Status |
|---|---|---|
| PROGRAM-BOARD-004 | `ECMP_PROGRAM_BOARD_004_Architecture_Board_Resolution_v1.0.md` | **Registered** (linked from Governance README) |
| PROGRAM-BOARD-005 | Architecture Board Review (ADR-016/017/018) | **RECORDED** — Ready for Resolution; resolved by BOARD-006 |
| PROGRAM-BOARD-006 | Architecture Board Resolution (Accept With Conditions ADR-016/017/018) | **RECORDED** — BR-011 / BR-012 / BR-013; C-B6-1…C-B6-7; Mode B CLOSED |

---

## 5. Consistency Checks

### 5.1 Status consistency

| ADR | Version head | Lifecycle after refresh | Expected from available Board Resolutions | Result |
|---|---|---|---|---|
| ADR-014 | v1.4 | Accepted with Conditions | BOARD-004 BR-009 | **PASS** |
| ADR-015 | v1.3 | Accepted with Conditions | BOARD-004 BR-010 | **PASS** |
| ADR-016 | v1.0 | Accepted with Conditions | BOARD-006 BR-011 | **PASS** |
| ADR-017 | v1.0 | Accepted with Conditions | BOARD-006 BR-012 | **PASS** |
| ADR-018 | v1.0 | Accepted with Conditions | BOARD-006 BR-013 | **PASS** |

### 5.2 Version consistency

| Check | Result |
|---|---|
| Canonical ADR-014 path = v1.4 only (non-archive) | **PASS** |
| Canonical ADR-015 path = v1.3 only (non-archive) | **PASS** |
| Generated index points to v1.4 / v1.3 | **PASS** |
| Human README points to v1.4 / v1.3 | **PASS** |
| Portal mirror points to v1.4 / v1.3 | **PASS** |
| ADR-014/015 v1.0 supersession files present to archive | **WARN** — already absent |

### 5.3 Cross-reference consistency

| Check | Result |
|---|---|
| ADR-014/015 cite PROGRAM-BOARD-004 | **PASS** |
| PROGRAM-ADR-002 marks BR-005/BR-006 historical | **PASS** |
| Mode B CLOSED stated on ADR-014/015 and indexes | **PASS** |
| PROGRAM-BOARD-005 / 006 resolvable paths | **FAIL** — missing |
| Broken markdown links after report creation | Re-check after this file exists |

### 5.4 Regenerated ADR index evidence

`ADR_INDEX.generated.md` lists ADR-001…ADR-018 with:

- ADR-014 / ADR-015 → Approved (Accepted with Conditions — PROGRAM-BOARD-004)
- ADR-016 / ADR-017 / ADR-018 → Proposed

---

## 6. Remaining Issues

| ID | Severity | Issue | Required next action |
|---|---|---|---|
| RI-01 | **Blocker** | PROGRAM-BOARD-005 missing | Author/record Architecture Board Review with C-1′…C-11′ (Secretary/Board), then re-run refresh |
| RI-02 | **Blocker** | PROGRAM-BOARD-006 missing | After BOARD-005 exists, record Accept With Conditions Resolution for ADR-016/017/018 — **do not invent** |
| RI-03 | Medium | ADR-016/017/018 remain Proposed while ChatGPT/mission text may assume Accept | Do not flip metadata until BOARD-006 is in repo |
| RI-04 | Low | Historical ADR-014/015 v1.0 files named in BOARD-004 C-1 table not present to archive | Accept as pre-existing gap; optional hunt outside tree |
| RI-05 | Info | Mode B / Batch-2 / enterprise customer remain CLOSED | Preserve C-7; no implementation authorization |

---

## 7. Repository Status (post-refresh)

| Area | Status |
|---|---|
| ADR-014 / ADR-015 Board Accept hygiene (BOARD-004) | Synced |
| ADR-016 / ADR-017 / ADR-018 Accept hygiene | **Not synced** (blocked) |
| Canonical ADR index / mirrors | Synced for available truth |
| Superseded ADR archive (v1.2/v1.3) | Done |
| Mode B | **CLOSED** |
| Implementation / OpenAPI / Auth coding | **Not authorized by this program** |
| Overall PROGRAM-GOVERNANCE-001 | **FAIL** |

---

## 8. Non-Granted Authorities (reaffirmed)

This refresh does **not** grant:

1. Mode B enablement
2. Batch-2 unlock
3. Enterprise customer production
4. OpenAPI changes
5. Authentication coding
6. Authorization coding
7. Invented Accept of ADR-016 / ADR-017 / ADR-018
8. Invented PROGRAM-BOARD-005 / PROGRAM-BOARD-006 content

Governance posture retained where BOARD-004 applies:

> **Accepted Architecture — Implementation Deferred — Mode B Closed**

---

## 9. PASS / FAIL

# **FAIL**

**Stop.** Re-run PROGRAM-GOVERNANCE-001 only after PROGRAM-BOARD-005 and PROGRAM-BOARD-006 exist as recorded governance artifacts in `18 Architecture Governance/`.

---

## Related post-refresh evidence

- `ECMP_AUDIT_ADDENDUM_Independent_Program_Audit_20260730_Fase0_v1.0.md` (AUDIT-ADD-20260730-F0) — Independent Program Audit addendum: marks BOARD-004 C-1 / F-1 / F-2 / F-3 (K-1 / K-2) as **REMEDIATED** against current tree; does **not** reverse this report’s **FAIL** for missing BOARD-005/006.

---

*End of ECMP_GOVERNANCE_BASELINE_REFRESH_REPORT_v1.0 — hygiene only; no architecture redesign; no implementation.*
