# B2-17E — ADR-CAP006-001 Architecture Board Decision Closure

| Field | Value |
|---|---|
| Document ID | GOV-B2-17E-ARB-001 |
| Sprint | B2-17E |
| Date | 2026-08-01 |
| Authority | Architecture Review Board / Chief Software Architect / Domain Architect / Repository Governance |
| Scope | Determine whether repository evidence suffices to **Accept** an evaluation mechanism for ADR-CAP006-001 |
| Non-goals | No Backend / Frontend / DB / OpenAPI / Event Catalog / FRD / BR; no invent scheduler, polling, retry, algorithm |
| Prerequisite | ADR-CAP006-001 Proposed (B2-17D); FRD-005 LOCKED (B2-16); DEC-CAP006-BQ-001 (B2-15) |
| Verdict | **ADR-CAP006-001 DEFERRED** |

## 1. Board finding (summary)

| Option | Meets FRD AC (time passes `dueAt`) without invent? | Repo design sufficient to Accept? |
|---|---|---|
| Event-only (lifecycle EVT-001/003/005/007 only) | **No** — no catalog event at `dueAt` | **No** |
| Job | Conceptually could meet time AC | **No** — only the word “job” in FRD §8; no job/scheduler design in repo; Accepting would require inventing scheduler/poll/store |

**ARB Decision:** Mechanism selection remains **NOT SPECIFIED**. ADR stays **Proposed**. Not Accepted.

## 2. Related

- `05 Architecture Decision Records/ADR-CAP006-001_Evaluation_Mechanism.md`
- `deploy/evidence/B2-17D_CAP-006_ADR-CAP006-001_Repository_Persist_20260801.md`

---

*End of GOV-B2-17E-ARB-001.*
