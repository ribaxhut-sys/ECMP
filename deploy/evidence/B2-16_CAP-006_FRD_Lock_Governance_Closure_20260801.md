# B2-16 — CAP-006 FRD Lock & Governance Closure

| Field | Value |
|---|---|
| Document ID | GOV-B2-16-LOCK-001 |
| Sprint | B2-16 |
| Date | 2026-08-01 |
| Authority | ARB / Business Architect / Solution Architect / Domain Architect / Repository Governance / Technical Writer |
| Scope | Freeze FRD-005 as official SoT for CAP-006; apply DEC-CAP006-BQ-001; sync repository metadata |
| Non-goals | No Backend / Frontend / DB / BR body / OpenAPI / Event Catalog / invent scheduler / invent SLA algorithm / invent APIs or events |
| Prerequisite | B2-15 **CAP-006 BUSINESS READY** (`B2-15_CAP-006_Business_Decision_Closure_20260801.md`) |
| Architecture Recommendation | **LOCK FRD-005** |
| Engineering Verdict | **CAP-006 NOT READY FOR IMPLEMENTATION** (technical blockers remain) |

## 1. Applied decisions (DEC-CAP006-BQ-001)

| § | Decision | Applied to |
|---|---|---|
| 1 | CAP-006 SoT = FRD-005 / FR-030 / SLA-MTX / EVT-004 | FRD-005 §1, §8, §9 |
| 2 | Calendar 24x7; Working Day DEFERRED | FRD-005 §4, §8 |
| 3–5 | Clock start/stop/reopen; pause OOS | FRD-005 §5, §8 |
| 6–7 | Warning 80%; breach → EVT-004 | FRD-005 §5, §6; refs DEC-005 |
| 8 | Admin owns SLA Config | FRD-005 §2, §7 |
| 9 | Case-type differentiation DEFERRED | FRD-005 §8 |
| 10 | Detection outcome in scope; mechanism = eng/ADR | FRD-005 §8; DoR blockers |
| 11 | ECMF clock attributes vs KPI runtime (separation) | FRD-005 §2a |

## 2. DoR re-run (Engineering Ready?)

| Item | Result |
|---|---|
| Business / BQ | **PASS** (CLOSED / DEFERRED via DEC-CAP006-BQ-001) |
| Governance / Architecture ownership | **PASS** (documented separation) |
| FRD-005 LOCKED | **PASS** (this sprint) |
| EVT-004 Implemented | **FAIL** — status Planned |
| OpenAPI for FR-030 | **FAIL** — `api: []` on TRC-L-007; no CAP-006 API invented here |
| Event bus / evaluation trigger | **FAIL** — mechanism ADR pending (not invented) |
| KPI Dictionary §2 sync to SLA-MTX | **PARTIAL** — DEC-005 follow-up open |
| TRC-L-007 / TC-030 | **PARTIAL** — remain Planned until implement |
| Engineering start authorized | **NO** |

## 3. Remaining technical blockers (post-FRD LOCK)

1. Explicit implementation authorization after DEC-002 / sprint gate (engine still Stay Deferred until scheduled).
2. EVT-004 remains **Planned** — emission path not Implemented.
3. Evaluation mechanism ADR (event-driven vs job) — outcome locked; mechanism not specified as business policy.
4. TRC-L-007 `api: []` — any HTTP surface must follow contract-first (no invent in B2-16).
5. Sync KPI Dictionary targets `[TBD]` → SLA-MTX-001 / DEC-005 (documentation hygiene).
6. CAP-005 production notification engine Stay Deferred — warning/breach delivery path may be stub-limited.
7. Mode A BQ-005 (“SLA countdown NOT activated”) applies to Aggregate Case Working Day track — **not** a repeal of CAP-006; keep dual-track awareness in delivery planning.

## 4. Repository sync performed

- FRD-005 → **LOCKED** v0.2
- `03 Functional Requirements/README.md` classification
- Capability Register CAP-006 metadata + B2-15/B2-16 notes
- `OPEN_QUESTIONS.md` BQ-CAP006 CLOSED
- `traceability.yaml` / `TRACEABILITY_MATRIX.md` TRC-L-007 notes
- `13 Test Strategy` TC-030 metadata note
- `CHANGELOG.md` [Unreleased]
- Evidence: this file + B2-15 pack

---

*End of GOV-B2-16-LOCK-001.*
