# B2-22 — CAP-006 Concrete Runtime Non-Invent Gate

| Field | Value |
|---|---|
| Document ID | GOV-B2-22-ARB-001 |
| Sprint | B2-22 |
| Date | 2026-08-01 |
| Authority | Architecture Review Board / Solution Architect / Repository Governance |
| Scope | Determine whether **current repository patterns** suffice to enter **Technical Runtime Design** for ARC-CAP006-002 **without inventing** new platform architecture |
| Non-goals | No Backend / Frontend / DB / OpenAPI / Event Catalog / FRD / BR; **do not design** scheduler, polling, retry, queue, thread, SQL, worker, timer, algorithm, framework |
| Prerequisite | ARC-CAP006-001 Accepted; ARC-CAP006-002 Accepted (B2-21); ADR-CAP006-001 Accepted Hybrid (B2-20); FRD-005 LOCKED; DEC-CAP006-BQ-001 |
| Verdict | **ADDITIONAL ARCHITECTURE REQUIRED** |

## 1. Repository files audited

| Artifact | Role in gate |
|---|---|
| `ARC-CAP006-001_Time_Source.md` | Time Source = Accepted **concept**; not a fulfillment pattern |
| `ARC-CAP006-002_Runtime_Architecture.md` | Conceptual stages RS-01…RS-08; RS-04/05/06 require Time Source |
| `ADR-CAP006-001_Evaluation_Mechanism.md` | Hybrid class Accepted; concrete Deferred; DEC-012/013/014 ≠ CAP-006 |
| FRD-005 LOCKED | Time AC + lifecycle event flow |
| DEC-CAP006-BQ-001 | Ownership; mechanism = eng/ADR |
| ADR-001 | Inter-domain event-driven; near-real-time breach goal |
| ADR-009 + ADR-009-ADD-G2 | Outbox official; Mode A in-process drain; FR-030/KPI consumer flagged as broker re-eval trigger |
| Data Dictionary | Clock ECMF; Config Admin; evaluation/Breach KPI |
| Event Catalog | EVT-001/003/005/006/007 → KPI; EVT-004 ← KPI |
| `implementation/backend` outbox + drain + Notification stub | Existing emit/consume pattern (Mode A) |
| `backend` EventDispatcher + KPI/Dashboard/Notification consumers | Existing in-process consumption pattern |
| DEC-013 / `backend/.../sla/service.py` on-read re-evaluate | Adjacent **complaint-stage** pattern — **explicitly OOS** for CAP-006 fulfillment |
| ARCH-EXEC-RT-001 Execution Runtime | Prepare-only; **not** adopted as CAP-006 SoT (ARC-CAP006-002) |
| ARCH-KPI-PROJECTION-001 | Event-only projection; **not** Time Source / EVT-004 engine |

## 2. Review findings (nine topics)

| # | Topic | Finding |
|---|---|---|
| 1 | Time Source | **Concept Accepted; fulfillment pattern ABSENT** in repository architecture SoT |
| 2 | Hybrid mechanism | Class Accepted; lifecycle half has patterns; time half does **not** |
| 3 | Runtime ownership | **Sufficient** — FRD §2a / DEC-CAP006-BQ-001 / Data Dictionary / ARC-CAP006-002 |
| 4 | Event ownership | **Sufficient** — Event Catalog producers/consumers; no time-tick invent needed for ownership |
| 5 | Configuration ownership | **Sufficient** — Administration SoT; EVT-006 Planned consumer role for KPI |
| 6 | Existing repository patterns | Outbox, in-process drain consumer, EventDispatcher handlers, KPI projection (event-only) |
| 7 | Existing infrastructure patterns | Mode A in-process transport (ADR-009-ADD-G2); broker still deferred |
| 8 | Existing outbox pattern | **Sufficient for EVT-004 emit path** (ADR-009) once breach decision exists |
| 9 | Existing event consumption pattern | **Sufficient for RS-01/02/03/07/08** (lifecycle + config) via dispatcher/outbox-drain analogues |

## 3. Existing Runtime Patterns (usable without invent)

| Pattern | Repo evidence | Maps to ARC-CAP006-002 |
|---|---|---|
| Transactional outbox | ADR-009; `implementation/backend` outbox table + write-in-txn | RS-06 durable emit EVT-004 |
| In-process outbox drain + consumer | ADR-009-ADD-G2; Notification stub on drain | Mode A analogue for delivering lifecycle events to consumers |
| In-process EventDispatcher consumers | TASK-046…051; KPI/Notification/Dashboard handlers | Lifecycle **state** consumption pattern (Hybrid event half) |
| Ownership / config / event contracts | FRD-005; DEC-CAP006-BQ-001; Data Dictionary; Event Catalog | RS responsibilities & boundaries (non-tech) |

## 4. Pattern Gaps (blocking)

| Gap | Why blocking | Why not fill from adjacent code |
|---|---|---|
| **Time Source fulfillment pattern** for silent-period evaluation (RS-04/05/06) | Hybrid **requires** time stimulus; ARC-CAP006-001 is concept-only; B2-17E rejected Accepting “job” without design | DEC-013 on-read re-evaluate is **≠ CAP-006** (FRD-005 §9; ADR-CAP006-001 §C.4; ARC-CAP006-002 OOS); also does not alone guarantee near-real-time silent periods (ADR-001 goal) |
| No Accepted Time Source pattern class in ADR/ARC beyond the stimulus **requirement** | Technical Runtime Design would have to invent scheduler/poll/worker/timer **or** invent a new platform binding | ARCH-EXEC-RT-001 does not schedule/execute; not CAP-006 SoT |
| KPI Projection (TASK-051) | Event-driven counters only | Not breach detection / EVT-004 / Time Source |

**Non-blocking residual (post-architecture):** broker vs Mode A process boundary when KPI/SLA consumer becomes separate process (ADR-009-ADD-G2 note) — orthogonal to Time Source pattern gap; does not by itself supply RS-04.

## 5. Non-Invent Assessment

| Question | Answer |
|---|---|
| Can Hybrid **lifecycle** stages be designed from existing patterns? | **Yes** (outbox + dispatcher/drain consumer patterns) |
| Can EVT-004 **emit** be designed from existing patterns? | **Yes** (transactional outbox) |
| Can **Time Source** stages RS-04/05/06 be designed without new architecture? | **No** |
| Can CAP-006 enter **Technical Runtime Design** without inventing additional architecture? | **No** |

Composing only existing Accepted patterns yields at best **event-half + emit path** — which ADR-CAP006-001 already rejected as sole class (**event-only**). Therefore Technical Runtime Design is **not** unlocked.

## 6. Architecture Board Decision

**ADDITIONAL ARCHITECTURE REQUIRED**

- CAP-006 engine status remains **Planned / Stay Deferred**.
- ARC-CAP006-001 / ARC-CAP006-002 / ADR-CAP006-001 **unchanged** in Accepted content (gate records gap only).
- This sprint does **not** invent or Accept scheduler/job/poll/worker/timer.
- This sprint does **not** authorize FR-030 engineering.
- This sprint does **not** reopen DEC-012/013/014 as CAP-006 fulfillment.

## 7. Remaining Technical Decisions (deferred — not designed here)

- Time Source **fulfillment pattern class** (architecture decision still required)
- Any later concrete: scheduler / poll / worker / timer / SQL / retry / queue (still forbidden to invent in this gate)
- Broker re-evaluation trigger when KPI/SLA consumer leaves in-process Mode A (ADR-009-ADD-G2)
- Fulfillment predicate / multi-clock / `slaId` allocation detail

## 8. Recommended next sprint

**B2-23 — CAP-006 Time Source Fulfillment Pattern Decision (governance-only)**  
Close whether a **fulfillment pattern class** for ARC-CAP006-001 can be Accepted from repository evidence **without invent**; if not, **confirm Stay Deferred** until a non-invent pattern basis exists. Do **not** design scheduler/poll/worker. Do **not** implement FR-030.

## 9. Final Verdict

**ADDITIONAL ARCHITECTURE REQUIRED**

---

*End of GOV-B2-22-ARB-001.*
