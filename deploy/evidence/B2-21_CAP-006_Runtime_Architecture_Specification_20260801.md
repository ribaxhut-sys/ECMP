# B2-21 — CAP-006 Runtime Architecture Specification

| Field | Value |
|---|---|
| Document ID | GOV-B2-21-ARC-001 |
| Sprint | B2-21 |
| Date | 2026-08-01 |
| Authority | Architecture Review Board / Solution Architect / Repository Governance |
| Scope | Specify **ONE** official **conceptual** Runtime Architecture for CAP-006 (stages, responsibilities, boundaries, ownership) |
| Non-goals | No Backend / Frontend / DB / OpenAPI / Event Catalog / FRD body / BR; no scheduler, cron, polling, worker, retry, queue, SQL, persistence, thread, timer, algorithms |
| Prerequisite | ADR-CAP006-001 Accepted Hybrid (B2-20); ARC-CAP006-001 Accepted (B2-19); FRD-005 LOCKED; DEC-CAP006-BQ-001 |
| Verdict | **RUNTIME ARCHITECTURE SPECIFIED** |

## 1. Repository files audited

| Artifact | Finding used |
|---|---|
| `ADR-CAP006-001_Evaluation_Mechanism.md` | Class Hybrid Accepted; concrete runtime Deferred |
| `ARC-CAP006-001_Time_Source.md` | Time Source mandatory; KPI runtime/infrastructure concern |
| FRD-005 LOCKED | Event flow EVT-001/003/005/007; AC time passes `dueAt`; ownership §2a |
| DEC-CAP006-BQ-001 | Start/stop/reopen; warning 80% Notification; Admin config; KPI evaluation |
| ADR-001 | Inter-domain event-driven; near-real-time breach goal |
| ADR-009 | Outbox official; broker deferred; no generic retry/DLQ |
| Data Dictionary | SLA Clock → ECMF; SLA Config → Admin; Breach/evaluation → KPI; Dashboard/Notification entities |
| Event Catalog | EVT-001/003/005/006/007 consumers KPI; EVT-004 producer KPI → Notification/Dashboard |
| `EXECUTION_RUNTIME_ARCHITECTURE.md` (ARCH-EXEC-RT-001) | Exists as separate Execution foundation — **not** adopted as CAP-006 Runtime Architecture SoT |
| Capability Register / Traceability | CAP-006 engine Planned / Stay Deferred; TRC-L-007 Planned |

## 2. Architecture Concept

| ID | Official name | Status |
|---|---|---|
| **ARC-CAP006-002** | **Runtime Architecture** | 🟢 **Accepted** (conceptual only) |

Path: `05 Architecture Decision Records/ARC-CAP006-002_Runtime_Architecture.md`

**Layer stack (official):**

| Layer | Artifact | Status |
|---|---|---|
| Mechanism class | ADR-CAP006-001 | Accepted — **Hybrid** |
| Time stimulus concept | ARC-CAP006-001 | Accepted |
| Conceptual runtime | **ARC-CAP006-002** | **Accepted (B2-21)** |
| Concrete runtime / engine | — | **Deferred** (unchanged) |

## 3. Defined (summary of nine)

| # | Topic | Specification (summary) |
|---|---|---|
| 1 | Runtime stages | RS-01…RS-08: config awareness → arm → status sync → time observation → warn → breach/emit → stop → reopen |
| 2 | Runtime responsibilities | KPI evaluates/emits; ECMF clock attributes; Admin config; Notification/Dashboard consume; outbox durable path |
| 3 | Runtime boundaries | Hybrid loop in; tech invent / dual ownership / DEC-012 track / ARCH-EXEC-RT-001 adoption out |
| 4 | State ownership | Clock attrs ECMF; Config Admin; evaluation/breach/performance facts KPI |
| 5 | Evaluation ownership | KPI only (+ Time Source as KPI stimulus concept) |
| 6 | Event ownership | Per catalog producers; EVT-004 = KPI; no time-tick invent |
| 7 | Configuration ownership | Administration SoT; KPI reads; DEC-004/005 / SLA-MTX baselines |
| 8 | Notification boundary | Downstream consequence consumer only |
| 9 | Dashboard boundary | Read/consumer surface only |

## 4. What was persisted

| Artifact | Action |
|---|---|
| `ARC-CAP006-002_Runtime_Architecture.md` | **Created** — Accepted conceptual Runtime Architecture |
| This evidence file | Created |
| Metadata sync | ADR README, ADR index, CHANGELOG, Cap Register note, Traceability, Governance README, ADR-CAP006-001 / ARC-CAP006-001 cross-refs |

## 5. Repository impact

| Concern | Result |
|---|---|
| Official CAP-006 Runtime Architecture | **ONE** — ARC-CAP006-002 |
| CAP-006 engine delivery | **Unchanged** — Planned / Stay Deferred |
| FRD-005 / BR / OpenAPI / Event Catalog / DB / code | **Unchanged** |
| FR-030 engineering authorization | **Not granted** by this sprint |

## 6. Deferred technical design

Scheduler · cron · polling · worker · retry · queue · SQL · persistence · thread · timer implementation · algorithms · recovery/catch-up · engine observability · ARCH-EXEC-RT-001 binding · FR-030 implementation.

## 7. Recommended next sprint

**B2-22 — CAP-006 Concrete Runtime Non-Invent Gate (governance-only)** — audit whether repository already contains sufficient non-invent patterns to fulfill Time Source + Hybrid **without** inventing scheduler frameworks; produce Accept/Defer verdict for concrete technical design readiness. **No** FR-030 engineering unless a separate engineering gate explicitly opens.

---

*End of GOV-B2-21-ARC-001.*
