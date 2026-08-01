# ADR-CAP006-001 — Evaluation Mechanism (CAP-006 / FR-030)

| Field | Value |
|---|---|
| Document ID | ADR-CAP006-001 |
| Title | Evaluation Mechanism |
| Version | 2.0 |
| Owner | Solution Architect / Performance Owner |
| Reviewer | Architecture Review Board |
| Approver | Architecture Board |
| Status | 🟢 **Accepted** — **mechanism class = Hybrid** (B2-20); conceptual runtime **ARC-CAP006-002** Accepted (B2-21); concrete runtime (scheduler/job/poll/worker) **Deferred** |
| Last Review | 2026-08-01 |
| Next Review | 2026-10-01 |
| Capability | CAP-006 (SLA Measurement & Breach Detection) |
| FR | FR-030 |
| Trace | TRC-L-007 |

- ADR Status: **Accepted** (Architecture Board, 2026-08-01 — B2-20 Mechanism Class Decision Closure)
- Scope of Accept: **mechanism class only** — not scheduler, cron, polling, worker, retry, queue, SQL, persistence, or timer implementation
- Decision Owners: Solution Architect, Architecture Board
- Related Domains: KPI & Performance, ECMF, Administration, Notification, Core Platform (outbox)
- Persistence: B2-17D — `../deploy/evidence/B2-17D_CAP-006_ADR-CAP006-001_Repository_Persist_20260801.md`
- Prior closure (concrete runtime): B2-17E — **DEFERRED** invent gap for job — still valid for implementation detail
- Workshop: B2-18 — hybrid + Time Source draft
- Concept: B2-19 — `./ARC-CAP006-001_Time_Source.md` (**Accepted**)
- Class closure: B2-20 — `../deploy/evidence/B2-20_CAP-006_ADR-CAP006-001_Mechanism_Class_Decision_Closure_20260801.md`
- Conceptual runtime: B2-21 — `./ARC-CAP006-002_Runtime_Architecture.md` (**Accepted** concept; concrete still Deferred)
- Non-Invent Gate: B2-22 — `../deploy/evidence/B2-22_CAP-006_Concrete_Runtime_Non_Invent_Gate_20260801.md` (**ADDITIONAL ARCHITECTURE REQUIRED**)
- Fulfillment pattern: B2-23 — `../deploy/evidence/B2-23_CAP-006_Time_Source_Fulfillment_Pattern_Decision_20260801.md` (**FULFILLMENT PATTERN NOT SPECIFIED**)

## Context

CAP-006 / FR-030 require automatic SLA measurement and breach detection with emission of **EVT-004 SLABreached**. FRD-005 is **LOCKED** (B2-16). Business questions are **CLOSED / DEFERRED** under **DEC-CAP006-BQ-001** (B2-15).

FRD-005 §8 leaves evaluation mechanism to engineering/ADR. B2-17E deferred Accept of event-only or job. B2-18/B2-19 established Time Source as required architecture concept and rejected event-only as sole stimulus. B2-20 closes **only** the architectural **mechanism class**.

## Problem Statement

Which **architectural mechanism class** shall CAP-006 use to evaluate SLA clocks against `dueAt`, consistent with FRD-005, ARC-CAP006-001, ADR-001, and ADR-009, without selecting any concrete runtime technology?

## Repository Evidence

| Artifact | Constraint on mechanism class |
|---|---|
| FRD-005 LOCKED | Event flow: consume EVT-001/003/005/007 → detect overdue → emit EVT-004; AC: *waktu berjalan melewati dueAt* |
| DEC-CAP006-BQ-001 | Clock start EVT-001; stop EVT-005; reopen EVT-007; detection outcome in scope; mechanism = eng/ADR |
| ARC-CAP006-001 | Time Source **Accepted** — time-based evaluation stimulus **required**; not a domain; no new events/APIs |
| B2-17E | Event-only fails time AC; job Accept would invent |
| B2-18 / B2-19 | Event-only rejected as sole mechanism; hybrid direction recorded |
| ADR-001 | Inter-domain = event-driven; SLA breach near real-time goal |
| ADR-009 | Outbox official; broker deferred; no generic retry/DLQ pre-broker |
| Event Catalog | EVT-004 Planned; no time-tick enterprise event |
| Data Dictionary | SLA Clock attributes → ECMF; evaluation/Breach → KPI |

## Decision

### A. Board determinations (B2-20)

| # | Question | Decision |
|---|---|---|
| 1 | Is Time Source mandatory? | **Yes** — ARC-CAP006-001 |
| 2 | Is lifecycle event consumption still required? | **Yes** — FRD-005 §6; DEC-CAP006-BQ-001 (start/stop/reopen/status) |
| 3 | Does CAP-006 require BOTH? | **Yes** |
| 4 | Architectural classification | **Hybrid** |

### B. Accepted mechanism class: Hybrid

**Hybrid** means:

1. **Lifecycle events** (EVT-001 / EVT-003 / EVT-005 / EVT-007) are **required** to supply and update SLA clock **state** (start, status, stop/finalize, reopen restart) per FRD-005 and DEC-CAP006-BQ-001.
2. **Time Source** (ARC-CAP006-001) is **mandatory** to supply **time-based evaluation stimulus** so `dueAt` can be evaluated when wall-clock passes the threshold, including **silent periods** with no lifecycle event.
3. **Both** are required. Neither alone is the Accepted class.

#### Why Hybrid (repository evidence)

| Rejected / not chosen | Why |
|---|---|
| **Event-only** | FRD AC triggers on *waktu berjalan melewati dueAt*; lifecycle events do not fire at `dueAt`; B2-17E/B2-18/B2-19 reject sole event-only |
| **Time-only** | FRD-005 §6 and DEC-CAP006-BQ-001 require EVT-001 start, EVT-003 status, EVT-005 stop, EVT-007 reopen; Data Dictionary places clock attributes on ECMF fed by operational events; ADR-001 inter-domain remains event-driven consumption |
| **Hybrid** | Satisfies time AC (Time Source) **and** clock-state SoT via lifecycle events without inventing new enterprise events or OpenAPI |

#### Boundary of this Accept

**In scope of Accept:** mechanism **class** = Hybrid (events for state + Time Source for time stimulus).

**Out of scope of Accept (remain Deferred):** scheduler, cron, polling interval, worker, retry, queue, SQL, persistence schema, timer implementation, catch-up/recovery runbook, observability of engine, concrete fulfillment predicate details beyond FRD.

#### Compatibility

- **ADR-001:** Unchanged. Inter-domain integration remains event-driven. Time Source is intra-KPI runtime concern, not a replacement for ECMF→KPI events.
- **ADR-009:** Unchanged. EVT-004 emit path remains transactional outbox until broker selection. Hybrid class does not authorize publisher retry/DLQ frameworks.
- **Business Rules / OpenAPI / Event Catalog:** Unchanged by this Accept.

### C. Prior decisions retained

1. Detection outcome MUST emit EVT-004 once per `caseId`+`slaId` per breach cycle; re-breach after reopen allowed.
2. ECMF owns SLA clock **attributes**; KPI owns **runtime evaluation** and EVT-004 emission.
3. Warning 80% via Notification — not a new enterprise event.
4. DEC-012/013/014 ≠ CAP-006 fulfillment.
5. ARC-CAP006-001 Time Source remains Accepted concept (infrastructure/runtime concern of KPI).

### D. B2-17E note (concrete runtime)

B2-17E **DEFERRED** Accept of concrete **job** design remains correct for **implementation detail**. B2-20 does **not** Accept job/scheduler. It Accepts only the **class**.

### E. Conceptual runtime (B2-21)

**ARC-CAP006-002 Runtime Architecture** is the **ONE** official **conceptual** runtime SoT (stages, responsibilities, boundaries, ownership). It does **not** Accept concrete scheduler/job/poll/worker/retry/queue/SQL/persistence/timer. Engine delivery remains Planned / Stay Deferred.

### F. Non-Invent Gate (B2-22)

B2-22 audited whether existing repository patterns suffice for Technical Runtime Design without invent. Verdict: **ADDITIONAL ARCHITECTURE REQUIRED** — Time Source **fulfillment pattern** absent (concept-only). Lifecycle event consumption + transactional outbox patterns are **not** sufficient alone (would collapse to rejected event-only). Evidence: `../deploy/evidence/B2-22_CAP-006_Concrete_Runtime_Non_Invent_Gate_20260801.md`. Does **not** invent scheduler/job. Does **not** authorize FR-030 engineering.

### G. Time Source fulfillment pattern (B2-23)

B2-23 asked whether the repository **already defines** a **conceptual** Time Source fulfillment pattern. Verdict: **FULFILLMENT PATTERN NOT SPECIFIED**. ARC-CAP006-001 remains the stimulus **requirement** concept only; Accepting a fulfillment pattern in B2-23 would invent. Evidence: `../deploy/evidence/B2-23_CAP-006_Time_Source_Fulfillment_Pattern_Decision_20260801.md`.

## Repository Constraints

- Do not invent APIs, events, payloads, SLA algorithms, or schedulers beyond catalogs.
- Do not build generic publisher retry/DLQ abstractions before broker (ADR-009).
- Do not invent enterprise time-tick events or a Time Source domain.
- TRC-L-007 remains `api: []` until a contract-first HTTP surface is separately approved.
- CAP-006 **engine** status remains Planned / Stay Deferred until a future **concrete** runtime design is approved **without invent** **and** engineering gate allows implementation.
- Conceptual runtime (ARC-CAP006-002, B2-21) is Accepted as architecture concept only — **does not** authorize FR-030 engineering start.
- This ADR Accept of **class** does **not** by itself authorize FR-030 engineering start.
- EVT-007 remains **Proposed** in Event Catalog (reopen path contract not final).

## Deferred Items

- Scheduler / cron / worker detail
- Polling interval / strategy
- Retry of evaluation/emit (distinct from BR-NOTIF-04)
- Queue technology for evaluation
- SQL / physical persistence of SLA Clock / emission ledger
- Timer implementation
- Recovery / catch-up procedures for CAP-006
- Observability / metrics for the engine
- Fulfillment predicate, multi-clock model, `slaId` allocation (separate runtime topics)
- Concrete fulfillment of ARC-CAP006-002 stages (non-invent gate — recommended B2-22)

## Consequences

### Positive

- Repository officially records CAP-006 mechanism class = **Hybrid**.
- Event-only and Time-only are closed as non-chosen classes.
- Time Source mandatory + lifecycle consumption mandatory — both binding.
- Engineering has a stable class constraint without an invented scheduler.

### Negative / residual

- FR-030 engine still unimplemented; concrete runtime still Deferred.
- Near-real-time breach goal has class-level support only.

## Repository Impact

- **v2.0 (B2-20):** Status → **Accepted** (mechanism class Hybrid); evidence pack; metadata sync.
- **Unchanged:** CAP-006 engine delivery status, FRD-005 body, Event Catalog, OpenAPI, Business Rules, application code, database.

## Related Documents

- `./ARC-CAP006-001_Time_Source.md`
- `./ARC-CAP006-002_Runtime_Architecture.md`
- `../deploy/evidence/B2-21_CAP-006_Runtime_Architecture_Specification_20260801.md`
- `../03 Functional Requirements/ECMP_FRD_KPI_SLA_v0.1.md` (FRD-005)
- `../deploy/evidence/B2-15_CAP-006_Business_Decision_Closure_20260801.md` (DEC-CAP006-BQ-001)
- `../deploy/evidence/B2-17E_CAP-006_ADR-CAP006-001_Decision_Closure_20260801.md`
- `../deploy/evidence/B2-19_CAP-006_Time_Source_Concept_Formalization_20260801.md`
- `../deploy/evidence/B2-20_CAP-006_ADR-CAP006-001_Mechanism_Class_Decision_Closure_20260801.md`
- `./ECMP_ADR_001_Event_Driven_Domain_Integration_v1.0.md`
- `./ECMP_ADR_009_Message_Broker_Deferral_v1.0.md`
- `../08 Event Catalog/events/events.yaml` (EVT-004)
- `../06 Data Dictionary/ECMP_Data_Dictionary_v1.0.md`
- `../01 Business Blueprint/ECMP_Capability_Register_v0.1.md`
- `../26 Traceability/traceability.yaml` (TRC-L-007)

## Document History

| Ver | Date | Change |
|---|---|---|
| 1.0 | 2026-08-01 | B2-17D persist; B2-17E DEFERRED mechanism Accept |
| 1.1 | 2026-08-01 | B2-19 — ARC-CAP006-001 linkage; event-only rejected; Time Source required |
| 2.0 | 2026-08-01 | B2-20 — **Accepted** mechanism class = **Hybrid**; concrete runtime remains Deferred |
| 2.0a | 2026-08-01 | B2-21 — cross-ref ARC-CAP006-002 conceptual Runtime Architecture Accepted; class/engine posture unchanged |
| 2.0b | 2026-08-01 | B2-22 — Non-Invent Gate: ADDITIONAL ARCHITECTURE REQUIRED (Time Source fulfillment); Technical Runtime Design not unlocked |
| 2.0c | 2026-08-01 | B2-23 — Time Source fulfillment pattern **NOT SPECIFIED**; no invent Accept |
