# B2-12 — CAP-007 FRD Lock & Governance Closure

| Field | Value |
|---|---|
| Document ID | GOV-B2-12-LOCK-001 |
| Sprint | B2-12 |
| Date | 2026-08-01 |
| Authority | ARB / BA / Repository Governance / Chief Solution Architect |
| Scope | Apply DEC-CAP007-BQ-001 to governance artifacts; FRD LOCK |
| Non-goals | No Backend / Frontend / BR body / CAP-008 / Queue / API-390 / API-513 / Mode B |
| Prerequisite | B2-11 BUSINESS DECISION READY |
| Architecture Recommendation | **LOCK FRD** |
| Engineering Verdict | **CAP-007 NOT READY** |

## 1. Applied decisions (DEC-CAP007-BQ-001)

| § | Decision | Applied to |
|---|---|---|
| 1 | Sprint ECMF Case SoT | FRD-006 §1; OpenAPI draft metadata; TC-040 |
| 2 | `dashboard:read` | FRD-006 §6; OpenAPI draft; SEC-RAM-001 v0.4 Planned Sprint-03; TC-040 |
| 3 | Drill-down API-002/005 | FRD-006 §1/§7; TC-040 step 2 |
| 4 | Supervisor-only v0.1 | FRD-006 §2; OpenAPI draft; SEC-RAM; TC-040 |
| 5 | FR-030 Deferred | FRD-006 §6 |

## 2. DoR re-run (Engineering Ready?)

| Item | Result |
|---|---|
| Business / BQ | PASS (CLOSED) |
| Governance / Architecture | PASS (B2-09 + B2-12 LOCK) |
| FRD LOCKED | PASS |
| OpenAPI normative | **FAIL** — still draft / Do NOT implement |
| Security mapping documented | PASS (Planned) |
| Traceability | PARTIAL — TRC-L-008 Planned until implement |
| TC-040 | PARTIAL — Planned until normative API |
| Engineering start authorized | **NO** |

## 3. Remaining blockers for implementation

1. Merge API-040 draft → normative OpenAPI (catalog gate)  
2. Explicit implementation authorization after normative merge  
3. TRC-L-008 / TC-040 remain Planned until code+contract

---

*End of GOV-B2-12-LOCK-001.*
