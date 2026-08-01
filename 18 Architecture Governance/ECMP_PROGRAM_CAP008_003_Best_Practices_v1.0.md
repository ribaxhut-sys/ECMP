# CAP-008 Best Practices

| Field | Value |
|---|---|
| Document ID | GOV-CAP008-CLOSE-003 |
| Version | 1.0 |
| Date | 2026-08-01 |
| Status | 🔒 Recorded |
| Authority | Architecture Review Board |

## Practices retained for future Complaint Module capabilities

1. **BQ Lock Pack before FRD LOCK** — Residual BQ must be ZERO for the delivery slice.
2. **BCS → FRD → OpenAPI → Code → RC → SoT Closure → Program Closure** — do not skip SoT Closure after RC.
3. **Namespace discipline (DEC-020)** — Aggregate `/api/v1/cm` vs foundation `/api/v1/complaints` vs Sprint `/v1/cases` never silently merged.
4. **Trace IDs that cannot collide** — use `FR-CM-B2-*` / `API-5xx` / `TRC-L-*` with CAP id in description.
5. **Lab claim language** — always qualify Implemented **(lab)** / PASS **(lab)** when Mode B / real IdP absent.
6. **REL-RC-001 before production language** — Production notes remain DRAFT until REL-SEC-001 GO.
7. **Evidence packs under `deploy/evidence/`** — assessments, SoT closure, program closure indexed from Release Management README.
8. **Constitution filter on every change** — Complaint Module COMPLETE > platform expansion.
9. **Provenance = annotated tag tip** — CHANGELOG and REL-RC cite `git rev-parse <tag>^{}`.
10. **Close programs explicitly** — CLOSED + Follow-up NONE prevents reopen of locked FRD/OpenAPI without a new CR.

---

*End of GOV-CAP008-CLOSE-003.*
