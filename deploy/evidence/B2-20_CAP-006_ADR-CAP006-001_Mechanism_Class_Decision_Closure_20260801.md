# B2-20 — ADR-CAP006-001 Mechanism Class Decision Closure

| Field | Value |
|---|---|
| Document ID | GOV-B2-20-ARB-001 |
| Sprint | B2-20 |
| Date | 2026-08-01 |
| Authority | Architecture Review Board / Chief Software Architect / Domain Architect / Repository Governance |
| Scope | Accept or reject **mechanism class only** for ADR-CAP006-001 |
| Non-goals | No Backend / Frontend / DB / OpenAPI / Event Catalog / FRD body / BR; no scheduler, cron, polling, worker, retry, queue, SQL, persistence, timer |
| Prerequisite | ARC-CAP006-001 Accepted (B2-19); ADR-CAP006-001 v1.1 Proposed; FRD-005 LOCKED; DEC-CAP006-BQ-001; B2-18 Workshop |
| Verdict | **ADR-CAP006-001 ACCEPTED** — mechanism class = **Hybrid** |

## 1. Repository files audited

| Artifact | Finding used |
|---|---|
| `ARC-CAP006-001_Time_Source.md` | Time Source mandatory; infrastructure/runtime KPI |
| `ADR-CAP006-001_Evaluation_Mechanism.md` (v1.1) | Event-only rejected; Time Source required; hybrid direction |
| FRD-005 LOCKED | EVT-001/003/005/007 consumption; AC time passes `dueAt` |
| DEC-CAP006-BQ-001 | Clock start/stop/reopen via lifecycle events; mechanism = ADR |
| ADR-001 | Inter-domain event-driven; near-real-time breach goal |
| ADR-009 | Outbox; broker deferred |
| Data Dictionary | SLA Clock → ECMF; evaluation/Breach → KPI |
| Event Catalog | EVT-004 Planned; no time-tick event |
| B2-18 / B2-19 | Hybrid draft; concept formalized |

## 2. Decision analysis

| # | Question | Answer | Evidence |
|---|---|---|---|
| 1 | Time Source mandatory? | **Yes** | ARC-CAP006-001; FRD AC time-based; B2-17E event-only gap |
| 2 | Lifecycle event consumption required? | **Yes** | FRD-005 §6; DEC-CAP006-BQ-001 §§3–4,7 |
| 3 | Both required? | **Yes** | Conjunction of (1) and (2) |
| 4 | Class | **Hybrid** | Event-only fails time AC; Time-only fails clock-state SoT |

### Hybrid explanation (class only)

- **Why:** Only Hybrid satisfies both FRD event-flow state requirements and time-threshold AC without inventing catalog events or OpenAPI.
- **Repository evidence:** FRD-005 §§6–7; DEC-CAP006-BQ-001; ARC-CAP006-001; ADR-001/009; B2-17E/18/19.
- **Boundary:** Class Accept only — events update/supply clock state; Time Source supplies time stimulus; KPI evaluates and emits EVT-004 via outbox path.
- **Deferred:** scheduler, cron, polling interval, worker, retry, queue, SQL, persistence, timer implementation.

## 3. Architecture decision

**ACCEPT ADR-CAP006-001** at version **2.0** with:

> **Mechanism class = Hybrid**  
> (lifecycle event consumption **and** Time Source — both mandatory)

Concrete runtime remains **Deferred**. CAP-006 engine delivery status **unchanged** (Planned / Stay Deferred). This closure does **not** authorize FR-030 engineering start by itself.

## 4. Repository impact

| Artifact | Action |
|---|---|
| `ADR-CAP006-001_Evaluation_Mechanism.md` | → **v2.0 Accepted** (class Hybrid) |
| `ARC-CAP006-001_Time_Source.md` | Governing ADR status note updated |
| This evidence | Created |
| Metadata | ADR index, README, CHANGELOG, Cap Register note, Traceability, Governance README |
| OpenAPI / Event Catalog / FRD / BR / code / DB | **Unchanged** |

## 5. Deferred items

Scheduler · cron · polling interval · worker · retry · queue · SQL · persistence · timer implementation · recovery/catch-up · engine observability · runtime design Accept.

## 6. Recommended next sprint

**B2-21 — CAP-006 Runtime Design Readiness (governance audit)** — determine whether repository already contains non-invent patterns sufficient to specify runtime **without** inventing scheduler frameworks; **or** keep engine Stay Deferred. No implementation unless gate explicitly opens.

---

*End of GOV-B2-20-ARB-001.*
