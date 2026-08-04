# B2-24 — CAP-006 Stay Deferred Confirmation & Blocker Freeze

| Field | Value |
|---|---|
| Document ID | GOV-B2-24-GOV-001 |
| Sprint | B2-24 |
| Date | 2026-08-04 |
| Authority | Architecture Review Board / PMO / Repository Governance |
| Scope | Confirm CAP-006 engine **Stay Deferred**; freeze official blocker; revoke stale “next eng = CAP-007” PMO language; state FR-030 engineering **NOT authorized** |
| Non-goals | No Backend / Frontend / DB / OpenAPI / Event Catalog / FRD body / BR; **do not invent or design** Time Source fulfillment pattern, scheduler, polling, queue, retry, worker, timer, SQL, framework |
| Prerequisite | B2-14 CAP-007 **COMPLETE**; B2-22 **ADDITIONAL ARCHITECTURE REQUIRED**; B2-23 **FULFILLMENT PATTERN NOT SPECIFIED**; FRD-005 LOCKED; ADR-CAP006-001 Hybrid Accepted; ARC-CAP006-001/002 Accepted |
| Verdict | **STAY DEFERRED · BLOCKER FROZEN · NO ENG AUTHORIZATION** |

## 1. Purpose

Close false pressure to start CAP-006 / FR-030 engineering while the Time Source **fulfillment pattern** remains unspecified, and correct obsolete roadmap text that still pointed engineering at CAP-007 (already Implemented in B2-14).

## 2. Current state (verified)

### Completed engineering

| Item | Status | Evidence |
|---|---|---|
| CAP-001…003 | Implemented (keep-green) | Capability Register / TRC-L-001…004 |
| Batch-1 Aggregate intake | Implemented / CLOSED slice | FRD-CM-001; Mode A M3 |
| CAP-007 / API-040 / FR-040 | **Implemented** | B2-14; TRC-L-008 Approved |
| CAP-008 Mode A Case | **Program CLOSED** | GOV-CAP008-CLOSE-* |
| Batch 1 Localization (catalog) | Merged `main` | PR #7 / `f9c2b72` |

### Deferred engineering (not authorized now)

| Item | Status | Official blocker |
|---|---|---|
| CAP-006 / FR-030 / EVT-004 **engine** | **Stay Deferred** | Time Source fulfillment pattern **NOT SPECIFIED** (B2-23); frozen by this B2-24 |
| CAP-004 / FR-010 | Stay Deferred | ACR-002 + API-010 draft |
| CAP-005 production notification engine | Stay Deferred | Catalog/engine gate (stub remains) |

### Pending Board / bilateral decisions (not eng tickets)

| Item | Status |
|---|---|
| DEC-F4 / FRD-CM-002 Aggregate escalate | Draft / awaiting Board countersign — **NOT APPROVED FOR CODE** |
| Mode B unlock | CLOSED (C-7 / C-B6-1) |
| Production promote blocked on external IdP | External / Release gate |

## 3. Official blocker (frozen)

**Blocker ID:** CAP006-BLK-001  
**Statement:** Time Source **fulfillment pattern** is **NOT SPECIFIED** (B2-23 / GOV-B2-23-ARB-001).  
**Freeze:** CAP-006 engine delivery remains **Planned / Stay Deferred** until a **future** architecture artifact **Accepts** a fulfillment pattern from **non-invent** repository evidence, **or** Board explicitly invent-authorizes (outside default constitution).  
**Consequence:** **FR-030 implementation is NOT authorized.** No scheduler design. No EVT-004 producer engineering under CAP-006 SoT.

## 4. Governance decisions (B2-24)

1. CAP-006 engine status confirmed **Stay Deferred**.
2. CAP006-BLK-001 is the **official frozen blocker**.
3. FR-030 / CAP-006 engine coding is **not authorized** by B2-14, B2-20…B2-23, or this B2-24.
4. Stale PMO language “next eng: implement CAP-007 …” is **obsolete** and must be replaced (CAP-007 already COMPLETE).
5. Ranked **open engineering** must not treat CAP-006 as an active eng ticket; it is **architecture-gated**.
6. CWX redesign / Batch 2 i18n wiring / Mode B / Identity remain **out of scope** for this freeze.

## 5. Repository impact

| Artifact | Action |
|---|---|
| This evidence | **Created** |
| `ai/sprint/CAP008_ROADMAP_RESET_v1.0.md` | PMO queue corrected |
| Capability Register | CAP-006 disposition + notes synced |
| Traceability TRC-L-007 | Status note synced (Planned; blocker frozen) |
| ADR-CAP006-001 | Cross-ref note only |
| Architecture Governance README | Pointer only |
| OpenAPI / Event Catalog / FRD body / BR / application code / DB | **Unchanged** |

## 6. Acceptance Criteria (this sprint)

- [x] CAP-006 explicitly **Stay Deferred**.
- [x] Blocker CAP006-BLK-001 formally documented and **frozen**.
- [x] FR-030 marked **unauthorized** until fulfillment pattern Accepted.
- [x] Obsolete “next eng = CAP-007” roadmap language corrected.
- [x] No engineering scope expanded; zero production code changes.

## 7. Rollback

Revert the documentation commit(s) that introduce this evidence and metadata sync. No runtime rollback.

## 8. Risk

**LOW** — documentation consistency only.

## 9. Recommended next (after B2-24)

- **Not** CAP-006 / FR-030 coding.
- Keep-green Mode A (M1/M5/M6 regression) if capacity.
- CAP-004 / CAP-005 only when their own DoR / gates open.
- Wait for future ARB Accept of Time Source fulfillment pattern (non-invent) before any CAP-006 eng gate.

## 10. Final Verdict

**STAY DEFERRED · BLOCKER FROZEN · NO ENG AUTHORIZATION**

---

*End of GOV-B2-24-GOV-001.*
