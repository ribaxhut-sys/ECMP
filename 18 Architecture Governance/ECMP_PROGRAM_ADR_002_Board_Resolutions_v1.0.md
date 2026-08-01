# PROGRAM-ADR-002 — Architecture Board Resolutions (Traceability)

| Field | Value |
|---|---|
| ID | GOV-BR-ADR-002 |
| Program | PROGRAM-ADR-002 |
| Phase | PHASE-0 (Board Resolution execution — recorded) |
| Version | 1.0 |
| Owner | Architecture Board Chair |
| Approver | Architecture Board |
| Status | 🟢 Recorded |
| Last Review | 2026-07-30 |
| Next Review | On next Architecture Board program resolution |

## Purpose

Provide a single governance traceability point for Architecture Board Resolutions issued under **PROGRAM-ADR-002**, so ADR and architecture documents that cite `BR-00n` can be verified without inventing or altering Board decisions.

This document **records** Board Resolutions already applied. It does **not** create new resolutions, reinterpret them, or change ADR lifecycle statuses.

## Board Resolutions (PROGRAM-ADR-002)

| ID | Resolution (verbatim intent) | Applied to | Notes |
|---|---|---|---|
| **BR-001** | Canonical ADR lifecycle: `PROPOSED`, `ACCEPTED`, `SUPERSEDED`, `DEPRECATED`, `REJECTED` | `18 Architecture Governance/README.md`; ADR template; `STATUS_BADGES.md` | Lifecycle vocabulary only |
| **BR-002** | Canonical Architecture Documents lifecycle: `DRAFT`, `REVIEW`, `BASELINE`, `ARCHIVED` | Governance README; FE-ARCH / FE-STD lifecycle | Non-ADR architecture docs |
| **BR-003** | FE-ARCH-001 → lifecycle **BASELINE** | `docs/frontend/FRONTEND_ARCHITECTURE_v1.2.md` | Frontend architecture |
| **BR-004** | FE-STD-001 → lifecycle **BASELINE** | `docs/frontend/FRONTEND_DEVELOPMENT_STANDARDS_v1.0.md` | Frontend standards |
| **BR-005** | ADR-014 Board Disposition: **Needs Revision** (references/metadata; coordinated revision required) | ADR-014 package (PROGRAM-ENTERPRISE-001) | Does not Accept ADR-014 |
| **BR-006** | ADR-015 Board Disposition: **Needs Revision** (references/metadata; coordinated revision required) | ADR-015 package (PROGRAM-ENTERPRISE-001) | Does not Accept ADR-015 |
| **BR-007** | ADR-013 **remain active**; do not supersede via FE documentation; future stack change requires a separate ADR | ADR-013; FE OD-FE-001 | Orthogonal to ADR-014/015 package |
| **BR-008** | Implementation Authorization: **AUTHORIZED WITH CONDITIONS** | FE-ARCH / FE-STD delivery posture | Conditions remain as recorded in FE-ARCH |

## Traceability from ADR-014 / ADR-015

| ADR citation | Board Resolution | Meaning for the ADR package |
|---|---|---|
| ADR-014 “Needs Revision (PROGRAM-ADR-002 BR-005)” (**historical**) | BR-005 | Content revision + resubmit with ADR-015; **superseded as active disposition** by PROGRAM-BOARD-004 **BR-009** |
| ADR-015 “Needs Revision (PROGRAM-ADR-002 BR-006)” (**historical**) | BR-006 | Content revision + resubmit with ADR-014; **superseded as active disposition** by PROGRAM-BOARD-004 **BR-010** |
| ADR-014 / ADR-015 “ADR-013 remain active (BR-007)” | BR-007 | Package must not supersede ADR-013 |
| ADR-014 v1.4 / ADR-015 v1.3 “Revised — Pending Board Review (PROGRAM-ADR-004)” (**historical authoring disposition**) | BR-005 / BR-006 (authoring response) | Authoring package complete for Board review; **superseded as active disposition** by PROGRAM-BOARD-004 |
| ADR-014 v1.4 **Accepted with Conditions** (active) | PROGRAM-BOARD-004 **BR-009** | See `ECMP_PROGRAM_BOARD_004_Architecture_Board_Resolution_v1.0.md`; C-1 / C-3 / C-7; Mode B CLOSED |
| ADR-015 v1.3 **Accepted with Conditions** (active) | PROGRAM-BOARD-004 **BR-010** | Bilateral Contract (C-3); Mode B CLOSED (C-7) |
| ADR-016 v1.0 **Accepted with Conditions** (active) | PROGRAM-BOARD-006 **BR-011** | See `ECMP_PROGRAM_BOARD_006_Architecture_Board_Resolution_v1.0.md`; C-B6-1…C-B6-7; Mode B CLOSED |
| ADR-017 v1.0 **Accepted with Conditions** (active) | PROGRAM-BOARD-006 **BR-012** | Entitlement architecture; Mode B CLOSED (C-B6-1) |
| ADR-018 v1.0 **Accepted with Conditions** (active) | PROGRAM-BOARD-006 **BR-013** | Org sync; C-B6-3 org-gap Mode B prerequisite; Mode B CLOSED |

## Related execution evidence

- `CHANGELOG.md` — PROGRAM-ADR-002 PHASE-0 Board Resolution execution note
- `18 Architecture Governance/README.md` — ADR and Architecture Documents lifecycles (BR-001 / BR-002)
- `18 Architecture Governance/ECMP_PROGRAM_BOARD_004_Architecture_Board_Resolution_v1.0.md` — BR-009 / BR-010 Accept With Conditions
- `18 Architecture Governance/ECMP_PROGRAM_BOARD_005_Architecture_Board_Review_v1.0.md` — Ready for Resolution (ADR-016/017/018)
- `18 Architecture Governance/ECMP_PROGRAM_BOARD_006_Architecture_Board_Resolution_v1.0.md` — BR-011 / BR-012 / BR-013 Accept With Conditions
- `18 Architecture Governance/ECMP_GOVERNANCE_BASELINE_REFRESH_REPORT_v1.0.md` — PROGRAM-GOVERNANCE-001 hygiene evidence
- `00 Repository Guide/STATUS_BADGES.md` — badge ↔ lifecycle mapping notes
- `05 Architecture Decision Records/README.md` — ADR index dispositions for ADR-013/014/015/016/017/018

## Non-goals

- Does not Accept, Reject, or Supersede any ADR **by itself** (Accept of ADR-014/015 is PROGRAM-BOARD-004; Accept of ADR-016/017/018 is PROGRAM-BOARD-006)
- Does not amend BR-001…BR-008 text
- Does not authorize Mode B AuthN implementation or OpenAPI securitySchemes enterprise changes
- Does not invent Board Accept when Review/Resolution artifacts are missing

## Document history

| Version | Date | Notes |
|---|---|---|
| 1.0 | 2026-07-30 | PROGRAM-ENTERPRISE-001 FINAL EDITORIAL PACKAGE EDIT-05 — Board Resolution traceability record (no resolution changes) |
| 1.0a | 2026-07-30 | PROGRAM-ADR-004 editorial note — ADR-014/015 disposition cite **Revised — Pending Board Review**; BR-001…BR-008 text unchanged; no Accept / no Mode B unlock |
| 1.0b | 2026-07-30 | PROGRAM-GOVERNANCE-001 — mark BR-005/BR-006 and PROGRAM-ADR-004 pending disposition as **historical**; active Accept With Conditions = PROGRAM-BOARD-004 BR-009/BR-010; no Mode B unlock |
| 1.0c | 2026-07-30 | PROGRAM-BOARD-006 — add BR-011/BR-012/BR-013 Accept With Conditions for ADR-016/017/018; Mode B remains CLOSED |