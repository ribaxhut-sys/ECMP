# FRD-CM-001 v1.1 LOCKED — Release Notes

| Field | Value |
|---|---|
| Document ID | GOV-RN-FRD-CM-001 |
| Subject | `03 Functional Requirements/ECMP_FRD_Complaint_Management_Batch1_v1.1.md` |
| Version | 1.1 LOCKED |
| Date | 2026-07-29 |
| Authority | CTO Decision D-08 |
| Delta Review | GOV-DELTA-FRD-CM-001 — Completed |
| Status | 🔒 LOCKED — Source of Truth for Batch 1 implementation |

---

## Release Notes (short)

FRD-CM-001 **v1.1** is **LOCKED** as the Batch 1 Source of Truth (FR-001…FR-004).

- Claude Delta Review completed with recommendation **APPROVE FOR CTO**.
- CTO Decision **D-08** closes the governance gate: no FR redesign, no business-rule change, no FR renumbering, no Batch 1 scope change.
- Three Delta Review implementation-level ambiguities are parked as **Open Questions / Architecture Decision candidates** (OQ-CM-B1-012…014): Request Id lifetime/TTL, Request Id generation authority, attachment `TRANSFERRED` status semantics.
- Functional content of Draft v1.1 (D-01…D-07 corrections) is unchanged at LOCK.

Implementation planning and detailed design MAY proceed against this FRD. Foundation artifact statuses (BR-CM-CAT-001 Draft, ADR-014/015 Proposed) remain unchanged. **OQ-CM-B1-001 is Closed** by **DEC-020** (dual SoT / controlled coexistence — not wholesale Sprint SoT retirement).

---

## Changelog — Draft v1.1 → v1.1 LOCKED

| Area | Change |
|---|---|
| Header Status | `Draft v1.1` → `LOCKED` |
| Related artifacts | Delta Review + Release Notes linked; Supersedes closes Draft v1.1 |
| §1.1 Document Control | Normative LOCKED SoT language; D-08 recorded; D-01 foundation-gate caveat retained; **OQ-CM-B1-001 later Closed by DEC-020** (PROGRAM-DOC-001 sync) |
| §1.3 CTO Decisions | **D-08** added (LOCK + park three ADR-candidate OQs) |
| §2.1 Purpose | Wording updated to LOCKED Batch 1 Source of Truth (no FR redesign) |
| §18 Open Questions | **OQ-CM-B1-012**, **OQ-CM-B1-013**, **OQ-CM-B1-014** added |
| §18.1 | Architecture Decision Candidates table (idempotency TTL, key provenance, TRANSFERRED semantics) |
| §19 Document History | Entry `1.1 LOCKED` added |
| Architecture Review Checklist | Claude Delta Review = Completed; CTO Approval → LOCKED = Completed; D-01…D-08 |
| §20.3 / §20.5 | OQ range extended; LOCK Gate Closure replaces “Ready for Claude Delta Review” |
| FR-001…FR-004 | **Unchanged** |
| Business Rules | **Unchanged** |
| FR numbering | **Unchanged** |
| Batch 1 scope | **Unchanged** (still FR-001…FR-004; Case create remains Batch 2) |

### Explicit non-changes

- No functional requirement redesign
- No business rule invent / modify
- No FR / BR / DM renumbering
- No Batch 1 scope expansion or contraction beyond Draft v1.1

---

## Related

- `03 Functional Requirements/ECMP_FRD_Complaint_Management_Batch1_v1.1.md` (LOCKED SoT)
- `18 Architecture Governance/reviews/ECMP_FRD_CM_001_Delta_Review_v1.1.md` (GOV-DELTA-FRD-CM-001)
- `18 Architecture Governance/reviews/ECMP_FRD_CM_001_Revision_Plan_v1.1.md` (GOV-RP-FRD-CM-001)
- `18 Architecture Governance/reviews/ECMP_FRD_CM_001_Architecture_Review_v1.0.md` (GOV-REV-FRD-CM-001)

---

*End of GOV-RN-FRD-CM-001 — FRD-CM-001 v1.1 LOCKED Release Notes.*
