# B2-09 — Queue Architecture Rationalization

| Field | Value |
|---|---|
| Document ID | GOV-B2-09-QUEUE-001 |
| Sprint | B2-09 |
| Date | 2026-08-01 |
| Authority | Architecture Review Board / Chief Enterprise Architect |
| Scope | Queue architecture disposition **only** — no BE/FE/OpenAPI/BR/FRD content edits |
| Prerequisite | B2-08 PORTFOLIO RATIONALIZATION COMPLETE |
| Verdict | **QUEUE ARCHITECTURE RATIONALIZATION COMPLETE** |

## 1. Decision Summary (ONE authoritative architecture)

ECMP has **three distinct “queue” domains**. They must not be collapsed into one API.

| Architecture lane | Authoritative SoT | Status |
|---|---|---|
| **A. Operational Case Workload Dashboard (CAP-007 / BP-006)** | **API-040** `GET /v1/dashboard/queues` ← FR-040 / FRD-006 / TRC-L-008 | **KEEP as target SoT** · **DEFER build** until FRD DoR |
| **B. Visit-context Queue (CAPABILITY-003)** | **queue-service** API-360…381 | **KEEP** as separate bounded context — **not** CAP-007 |
| **C. Aggregate Supervisor Visibility (Batch-1)** | **API-513** `GET /api/v1/cm/supervisor/queue` | **KEEP** under DEC-020 Aggregate — **not** CAP-007 SoT |

**Explicit non-SoT for CAP-007:**

- API-390 `GET /api/v1/dashboard/queue` — Visit QueueTicket widget (CAPABILITY-013) — **KEEP** · **do not promote** to FR-040
- API-522 escalated-queue — **DEFER** with FRD-CM-002
- Notification `notification_queue` — **KEEP** naming · **out of** CAP-007
- Case list API-005 / complaint search — work lists · **not** FR-040 dashboard

**No new Queue API invented.** No OpenAPI/BR/FRD/code changed in this sprint.

## 2. Alternatives considered

| Option | Verdict | Why (evidence) |
|---|---|---|
| A. Promote API-390 as CAP-007 SoT | **Reject** | Aggregates QueueTicket WAITING/SERVING — not case workload (queue_provider.py; FRD-006 asks case queue) |
| B. Promote API-513 as CAP-007 SoT | **Reject** | Later-review + no-Case aging only (batch1 OpenAPI/router); ≠ FR-040 unit workload dashboard |
| C. Invent new Queue API | **Forbidden** | Sprint rules |
| D. API-040 sole CAP-007 SoT; keep A/B/C lanes separate | **Accept** | Matches BP-006/FR-040/TRC-L-008 + existing Implemented surfaces without rewrite |

## 3. Migration strategy (docs/governance only — no implementation)

| Phase | Action | Compatibility |
|---|---|---|
| **Phase 1** (this sprint) | Freeze dispositions; publish this decision | No runtime change |
| **Phase 2** (future, gated) | FRD-006 DoR → merge API-040 draft normatively | API-390/513 unchanged |
| **Phase 3** (future eng) | Implement API-040 consumers; optionally wire FE dashboard to CAP-007 | Do not remove API-390/513 without separate DEC |
| **Rollback** | Revert governance docs only; no schema/API rollback needed (no code shipped) | — |

## 4. Related

- Capability Register CAP-007 disposition updated
- B2-08 portfolio: CAP-007 Merge candidate → resolved as **multi-lane KEEP + API-040 target**

---

*End of GOV-B2-09-QUEUE-001.*
