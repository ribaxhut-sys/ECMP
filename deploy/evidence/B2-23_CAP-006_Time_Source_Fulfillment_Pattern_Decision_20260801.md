# B2-23 — CAP-006 Time Source Fulfillment Pattern Decision

| Field | Value |
|---|---|
| Document ID | GOV-B2-23-ARB-001 |
| Sprint | B2-23 |
| Date | 2026-08-01 |
| Authority | Architecture Review Board / Solution Architect / Repository Governance |
| Scope | Determine whether repository **already defines** a **conceptual** Time Source **fulfillment pattern** (not concrete tech) |
| Non-goals | No Backend / Frontend / DB / OpenAPI / Event Catalog / FRD / BR; **do not invent or design** scheduler, polling, queue, retry, worker, timer, SQL, framework, thread, background task |
| Prerequisite | B2-22 Non-Invent Gate (**ADDITIONAL ARCHITECTURE REQUIRED**); ARC-CAP006-001/002 Accepted; ADR-CAP006-001 Hybrid Accepted; FRD-005 LOCKED |
| Verdict | **FULFILLMENT PATTERN NOT SPECIFIED** |

## 1. Repository files audited

| Artifact | Finding relevant to fulfillment pattern |
|---|---|
| ARC-CAP006-001 | Defines Time Source as **required stimulus concept**; explicitly **not** scheduler/poll/worker; **no** fulfillment pattern named |
| ARC-CAP006-002 | Stages RS-04/05/06 **consume** Time Source; does not define how stimulus is supplied |
| ADR-CAP006-001 | Hybrid class Accepted; concrete + fulfillment details Deferred; DEC-012/013/014 ≠ CAP-006 |
| FRD-005 LOCKED | AC time vs `dueAt`; mechanism left to eng/ADR; no fulfillment pattern |
| DEC-CAP006-BQ-001 | Detection outcome in scope; scheduler/mechanism = ADR — not invented as business pattern |
| ADR-001 | Near-real-time goal; event-driven inter-domain — not a Time Source fulfillment pattern |
| ADR-009 | Outbox for durable **emit** — orthogonal to time stimulus supply |
| Data Dictionary | Ownership of clock/config/breach — not fulfillment pattern |
| Event Catalog | No time-tick / DueReached event; EVT-004 is outcome, not stimulus |
| B2-22 evidence | Explicit: Time Source fulfillment pattern **ABSENT** |

## 2. Existing Fulfillment Concepts (what IS defined)

| Concept | Status | Is it a Time Source **fulfillment** pattern? |
|---|---|---|
| Time Source (ARC-CAP006-001) | Accepted | **No** — states **requirement** for time-based stimulus |
| Hybrid mechanism class (ADR-CAP006-001) | Accepted | **No** — states Time Source is **mandatory alongside** lifecycle events |
| Runtime stages RS-04/05/06 (ARC-CAP006-002) | Accepted | **No** — stages **depend on** Time Source; do not fulfill it |
| Lifecycle event consumption | Catalogued + runtime analogues | **No** — rejected as sole stimulus (event-only) |
| Transactional outbox | Accepted (ADR-009) | **No** — emit path after breach decision |
| DEC-013 on-read re-evaluate | Exists (complaint-stage) | **No** — explicitly **≠ CAP-006 fulfillment** |

**Conclusion of inventory:** Repository defines **need** and **placement** of Time Source, not a **conceptual pattern that fulfills** it.

## 3. Gap Analysis

| Question | Answer |
|---|---|
| Does any Accepted ADR/ARC name a Time Source fulfillment pattern class? | **No** |
| Can Hybrid / Runtime Architecture be re-read as that pattern? | **No** — they **require** the stimulus; they do not **supply** a pattern for supplying it |
| Can Event Catalog supply it without invent? | **No** — no time-threshold enterprise event; inventing one is forbidden |
| Can DEC-013 be elevated without invent/OOS breach? | **No** — FRD-005 §9 / ADR-CAP006-001 / ARC-CAP006-002 forbid as CAP-006 fulfillment |
| Would Accepting any pattern in this sprint require invent? | **Yes** — no repository-supported candidate remains |

## 4. Architecture Board Decision

**FULFILLMENT PATTERN NOT SPECIFIED**

1. Repository does **not** already define a conceptual Time Source fulfillment pattern.
2. ARB does **not** Accept a fulfillment pattern in B2-23 (would invent).
3. ARC-CAP006-001 remains Accepted as **stimulus requirement concept** only.
4. CAP-006 engine remains **Planned / Stay Deferred**.
5. Technical Runtime Design remains **blocked** (consistent with B2-22).
6. No FR-030 engineering authorization.

## 5. Repository Impact

| Artifact | Action |
|---|---|
| This evidence | **Created** |
| ARC-CAP006-001 / ADR-CAP006-001 / ARC-CAP006-002 | Cross-ref note only — body concepts unchanged |
| Capability Register / Traceability / CHANGELOG / Governance README / ADR index | Metadata sync |
| OpenAPI / Event Catalog / FRD / BR / code / DB | **Unchanged** |

## 6. Remaining Gaps

- Conceptual Time Source **fulfillment pattern** (still NOT SPECIFIED)
- Concrete runtime tech (still Deferred; out of this sprint)
- Technical Runtime Design unlock (still blocked)
- FR-030 / EVT-004 engine (still unimplemented)

## 7. Recommended next sprint

**B2-24 — CAP-006 Stay Deferred Confirmation & Blocker Freeze (governance-only)**  
Record official blocker: Time Source fulfillment pattern NOT SPECIFIED; freeze CAP-006 delivery posture until a **future** architecture artifact can Accept a fulfillment pattern **from non-invent evidence** (or explicit Board invent-authorize — out of current constitution default). No scheduler design. No FR-030 engineering.

## 8. Final Verdict

**FULFILLMENT PATTERN NOT SPECIFIED**

### Success question (answered)

> Does the repository already define a conceptual Time Source fulfillment pattern?

**No.**

---

*End of GOV-B2-23-ARB-001.*
