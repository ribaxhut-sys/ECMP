# B2-17D — CAP-006 ADR-CAP006-001 Repository Persist

| Field | Value |
|---|---|
| Document ID | GOV-B2-17D-PERSIST-001 |
| Sprint | B2-17D |
| Date | 2026-08-01 |
| Authority | ARB / Repository Governance / Solution Architect |
| Scope | Persist ADR-CAP006-001 artifact + metadata sync |
| Non-goals | No Backend / Frontend / DB / OpenAPI / Event Catalog / FRD / BR / invent mechanism / select job vs event-only |
| Prerequisite | B2-16 FRD-005 LOCKED; B2-15 DEC-CAP006-BQ-001; prior audit ADR-CAP006-001 NOT FOUND |
| Verdict | **ADR-CAP006-001 REPOSITORY PERSISTED** |

## 1. What was persisted

| Artifact | Path |
|---|---|
| ADR | `05 Architecture Decision Records/ADR-CAP006-001_Evaluation_Mechanism.md` |
| ADR Status | **Proposed** — Decision §B Evaluation mechanism = **NOT SPECIFIED** |
| Evidence | This file |

## 2. Decision content (no invention)

- Records repository-supported constraints (FRD-005, DEC-CAP006-BQ-001, ADR-001, ADR-009, Event Catalog, DD).
- Does **not** choose job vs event-only.
- Does **not** invent scheduler, polling, retry, persistence, API, or payloads.

## 3. Metadata sync

- `05 Architecture Decision Records/ADR_INDEX.generated.md`
- `05 Architecture Decision Records/README.md` (index row)
- `CHANGELOG.md` [Unreleased]
- Capability Register — reference note only; CAP-006 status **unchanged**
- `26 Traceability/traceability.yaml` + `TRACEABILITY_MATRIX.md` — reference ADR-CAP006-001
- `18 Architecture Governance/README.md` — Related pointer

## 4. Explicit non-changes

CAP-006 Planned / Stay Deferred · FRD-005 · Event Catalog · OpenAPI · application code · Business Rules.

---

*End of GOV-B2-17D-PERSIST-001.*
