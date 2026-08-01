# Sprint Context Pack

| Field | Value |
|---|---|
| ID | AI-SPRINT-000 |
| Version | 1.1 |
| Owner | PMO / Eng Manager |
| Reviewer | Domain POs |
| Approver | Business Owner |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## How to Use
Before implementation in Cursor/Claude:
1. Identify active sprint file (e.g. `Sprint-01.md`)
2. Load linked domain + API/Event context
3. Implement only sprint scope
4. Update sprint status/notes at end of work

## Active Sprint
**G2 EXITED (Mode A)** — DEC-021 (2026-08-01). G1 exited earlier (DEC-006).  
Berikutnya: residual Sprint-03 hanya bila DoD memerlukannya (FR-040 / FR-030 event-clock **setelah** broker re-eval), SIT dual-SoT (`Mode_A_SIT_SoT_Choice_20260801.md`), dan **U-5** sign-off manusia.  
Customer 360 (API-010) & Mode B tetap deferred/CLOSED. Lihat `REGRESSION_PACK_G2.md` + `DEV_RUNBOOK.md`.

## Vocabulary Map
| Term | Meaning |
|---|---|
| Slice | Sprint-01 vertical slice (case create/get) |
| B1 (Build-1) | Build portion of Sprint-01 (the slice) |
| G1 | Entry gate of Sprint-02 (lifecycle contract gate) |
| B2 | Sprint-02 build (assign/status) |
| B3 | Sprint-03 build (notification stub) |

## Implementation Roadmap
Forward roadmap (Sprint-02 → Sprint-03 → SIT/UAT, epics/stories/critical path):
[`IMPLEMENTATION_ROADMAP_v0.1.md`](./IMPLEMENTATION_ROADMAP_v0.1.md) — historical foundation planning.

**CAP-008 Mode A:** **PROGRAM CLOSED** — use [`CAP008_ROADMAP_RESET_v1.0.md`](./CAP008_ROADMAP_RESET_v1.0.md) (do not schedule further CAP-008 Create…Close delivery).

## Implementation Readiness
Before treating Sprint-01 as coding-authorized for a team, follow:
[`IMPLEMENTATION_READINESS_ROADMAP.md`](./IMPLEMENTATION_READINESS_ROADMAP.md) (current version per its metadata — historical planning artifact; see its banner)

**Build authorization:** product feature coding starts at **B1**, only after gate sprint **G0** is complete. Assign/status requires **G1 → B2**. Notification requires **G2 → B3**.
