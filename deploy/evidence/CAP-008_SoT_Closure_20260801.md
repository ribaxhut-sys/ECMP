# CAP-008 Source of Truth Closure — 2026-08-01

| Field | Value |
|---|---|
| Document ID | GOV-SOT-CAP008-001 |
| Program | CAP-008 SoT Closure Sprint |
| Date | 2026-08-01 |
| Authority | Architecture Review Board (independent closure execution) |
| Capability | **CAP-008** Case Management Batch-2 Mode A |
| Status | **EXECUTED** |
| Scope | Documentation / catalog / traceability / provenance only |
| Explicitly excluded | Features · CAP-008 redesign · Business Rules · Mode B · OIDC · Enterprise Platform |

## Mission

Synchronize repository documentation with the already implemented and RC-validated CAP-008 Mode A (`v1.2.0-rc.1`).

## Actions completed

| # | Action | Result |
|---|---|---|
| 1 | FRD Lock | FRD-CM-B2-001 → 🔒 **LOCKED** |
| 2 | OpenAPI Normative sync | `cm-case-management.v1.yaml` **1.0.0**; API-530…535 **Implemented (lab)** in catalog README |
| 3 | Capability Register sync | CAP-008 → **Implemented (lab)** (CAP-001…007 unchanged) |
| 4 | Traceability sync | `traceability.yaml` v0.11 — TRC-L-011…016 **Approved** (FR-CM-B2-001…006 ↔ API-530…535) |
| 5 | Release provenance verification | Tag `v1.2.0-rc.1` → `6890f50` verified; REL-RC + CHANGELOG tip aligned |

## Authoritative RC tip

| Item | Value |
|---|---|
| Annotated tag | `v1.2.0-rc.1` |
| Tag tip (commit) | `6890f50d8243ba30589a3d88f0c0efcef791ce01` |
| Source freeze ancestor | `b7d8e2cee864263ff92a1941a9181a629ce46550` |
| REL-RC-001 | **PASS (lab)** |
| Production `v1.2.0` | **not authorized** (REL-SEC-001 NO-GO — external IdP; out of this closure) |

## Files updated

See chat / git status for full list. Primary:

- `03 Functional Requirements/ECMP_FRD_Case_Management_Batch2_v1.0.md`
- `03 Functional Requirements/README.md`
- `07 API Catalog/openapi/cm-case-management.v1.yaml`
- `07 API Catalog/README.md`
- `01 Business Blueprint/ECMP_Capability_Register_v0.1.md`
- `26 Traceability/traceability.yaml`
- `docs/product/CAP-008_Case_Management_Business_Capability_Specification_v1.0.md`
- `docs/product/README.md`
- `deploy/evidence/REL_RC_001_CAP-008_Mode_A_Assessment_20260801.md`
- `CHANGELOG.md`
- `docs/releases/v1.2.0.md`
- this file

## Remaining inconsistencies (explicitly out of CAP-008 closure or deferred)

| Item | Disposition |
|---|---|
| EVT catalog IDs Aggregate CAP-008 | **NOT SPECIFIED** (unchanged; no invention) |
| Formal TC-catalog IDs CAP-008 | Deferred — lab suite `test_cm_case_mode_a.py` cited |
| CAP-002…007 register vs TRC | Out of CAP-008 closure scope |
| Git annotated tag `v1.0.0` | **NOT FOUND** (foundation line; not CAP-008) — documented only |
| Production AuthN / OIDC | External — not touched |
| `API_CATALOG.generated.md` | May lag until generator re-run |

## Verdict

**SOT CLOSURE COMPLETE** for CAP-008 Mode A documentation synchronization against RC-validated implementation.

## Program Closure (follow-on)

Program Closure pack recorded 2026-08-01:  
`18 Architecture Governance/ECMP_PROGRAM_CAP008_000_Program_Closure_Index_v1.0.md` — **PROGRAM CLOSED**.

---

*End of GOV-SOT-CAP008-001.*
