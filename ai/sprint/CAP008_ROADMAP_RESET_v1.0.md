# CAP-008 Roadmap Reset

| Field | Value |
|---|---|
| Document ID | GOV-CAP008-CLOSE-008 |
| Filename | `ai/sprint/CAP008_ROADMAP_RESET_v1.0.md` |
| Version | 1.0 |
| Date | 2026-08-01 |
| Status | 🔒 **Active reset** |
| Authority | Architecture Review Board / PMO |
| Supersedes (for CAP-008 only) | Forward CAP-008 / Batch-2 Case create items in older Mode A “CLOSED” language and stale Sprint-02/03 CAP-008 assumptions |

## 1. Reset statement

**CAP-008 Mode A delivery is CLOSED.**  
Do not schedule further CAP-008 Create/Add/View/Status/Resolve/Close feature work under this program.

`ai/sprint/IMPLEMENTATION_ROADMAP_v0.1.md` remains historical for Sprint-01…03 foundation planning and is **not** the CAP-008 exit roadmap.

## 2. What stops

| Stop | Reason |
|---|---|
| New CAP-008 FR / OpenAPI / BE / FE features | Program CLOSED |
| Reopening BQ-001…014 | LOCKED · Residual ZERO |
| Treating Batch-2 Case create as “future unlock” in Mode A NEXT | Delivered + RC + SoT + Program Closure |

## 3. What continues (outside CAP-008 program)

| Track | Owner cue | Note |
|---|---|---|
| Production promote `v1.2.0` | Release / Security | Blocked on external IdP — not CAP-008 backlog |
| Mode B | Architecture Board | CLOSED until Unlock Resolution |
| CAP-004 / 006 / 007 FRD sync | Domain POs | Separate from CAP-008 |
| Dual-SoT Retirement DEC | Business Owner | Only when BO decides |
| DEC-F4 / FRD-CM-002 | Board | Proposed / Draft — not CAP-008 |
| Mode A keep-green (Batch-1 regression) | Tech Lead | Maintenance, not CAP-008 reopen |

## 4. Recommended PMO queue (post-CAP-008)

1. Hold Production until bilateral IdP contract (external).  
2. Execute **B2-08** portfolio dispositions — `deploy/evidence/B2-08_Capability_Portfolio_Rationalization_20260801.md` (**COMPLETE** 2026-08-01).  
3. Next: **B2-12** FRD-006 LOCKED → **B2-13** API-040 **NORMATIVE** (`deploy/evidence/B2-13_API-040_Normative_Closure_20260801.md`) → **next eng:** implement CAP-007 against `dashboard-queues.v1.yaml` only → then CAP-006 / CAP-004 / CAP-005.  
4. Optional: formal TC-catalog IDs for CAP-008 (documentation only).  
5. Optional: EVT Aggregate IDs when Event Catalog work is authorized.  
6. Do **not** start Mode B coding.  
7. Do **not** reopen CAP-008 Create/Add/View/Status/Resolve/Close delivery.  
8. Do **not** promote API-390 or API-513 as CAP-007/FR-040 SoT (B2-09).

## 5. Pointers

- Program Closure Index: `18 Architecture Governance/ECMP_PROGRAM_CAP008_000_Program_Closure_Index_v1.0.md`  
- Mode A NEXT: update disposition — CAP-008 delivery no longer “future Batch-2”

---

*End of GOV-CAP008-CLOSE-008.*
