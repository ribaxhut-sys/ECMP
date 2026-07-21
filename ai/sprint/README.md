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
**Sprint-01** — Foundation & ECMF Case Core (**🟢 Approved — GO** for slice + G0 platform floor, per DEC-002; see `Sprint-01.md`)

## Vocabulary Map
| Term | Meaning |
|---|---|
| Slice | Sprint-01 vertical slice (case create/get) |
| B1 (Build-1) | Build portion of Sprint-01 (the slice) |
| G1 | Entry gate of Sprint-02 (lifecycle contract gate) |
| B2 | Sprint-02 build (assign/status) |
| B3 | Sprint-03 build (notification stub) |

## Implementation Readiness
Before treating Sprint-01 as coding-authorized for a team, follow:
[`IMPLEMENTATION_READINESS_ROADMAP.md`](./IMPLEMENTATION_READINESS_ROADMAP.md) (current version per its metadata — historical planning artifact; see its banner)

**Build authorization:** product feature coding starts at **B1**, only after gate sprint **G0** is complete. Assign/status requires **G1 → B2**. Notification requires **G2 → B3**.
