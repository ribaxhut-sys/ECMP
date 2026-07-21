# AI Rules (Hard Constraints)

| Field | Value |
|---|---|
| ID | AI-RULES-001 |
| Version | 1.0 |
| Owner | Enterprise Architecture |
| Reviewer | Architecture Board |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Must Follow

1. **Do not change Business Rules without ADR** (and governance review when material).
2. **Do not create APIs outside API Catalog** — add/update OpenAPI first or in the same change.
3. **Follow Engineering Standards** (`21`, `22`, `ai/08_standards.md`).
4. **Every endpoint must have OpenAPI** definition under `07 API Catalog/openapi/`.
5. **Every schema change must have a migration plan/artifact** (documented; code migration when implementation exists).
6. **Every domain event must be in Event Catalog** (`08 Event Catalog/events/events.yaml`).
7. **ECMP is not Customer Master SoR** — reuse existing customer master (read/integration only unless officially approved write-back).
8. **Status transitions must follow configured workflow** — no ad-hoc status inventing.
9. **Security by default** — role/org authorization required for sensitive actions.
10. **Traceability update required** when BR/FR/API/Event/Test relationships change (`26 Traceability`).
11. **Architecture deviations require ADR** + Architecture Review.
12. **Do not invent in-scope features** that contradict Blueprint Out of Scope; create `OQ-xxx` instead.
13. **Keep docs in sync with code** — if design changes during implementation, update EKR artifacts in the same effort.
14. **Use enterprise IDs** (`BP/BR/FR/API/EVT/ADR/...`) in plans, PRs, and commits when relevant.
15. **Respect tool roles**: ChatGPT for architecture/business review; Claude/Cursor for implementation against approved specs.

## Stop-the-line Conditions
If any rule above would be violated, stop and:
- propose ADR / Open Question / Catalog update first, or
- ask for human approval before continuing.
