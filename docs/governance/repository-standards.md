# Repository Standards

| Field | Value |
|---|---|
| ID | EAR-PORTAL-MIRROR |
| Version | 0.2 |
| Owner | Enterprise Architecture |
| Reviewer | PMO |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

The repository standards (EAR-STD-006, 🟢 Approved) govern how the knowledge repository itself is maintained:

- **Folder naming** `NN Name` (stable two-digit numbering, renames need Architecture Board approval).
- **File naming** `ECMP_<Area>_<DocumentName>_v<Major.Minor>.<ext>`.
- **Versioning**: major = scope/breaking/new baseline, minor = non-breaking; enterprise IDs stay stable across versions.
- **Archiving**: never delete approved artifacts without trace; move superseded versions to `archive/` and mark 🔴 Deprecated with a link to the replacement.
- **Review & approval**: Author → Reviewer → Owner → Approver; 🟢 Approved only after sign-off; `Last/Next Review` metadata mandatory.
- **Format policy**: Markdown/YAML/OpenAPI for living docs; diagram sources in `23 Assets`; Word only for formal distribution.
- **Traceability**: approved BR/FR/API/Event changes must update `26 Traceability`.

**Canonical source:** `00 Repository Guide/REPOSITORY_STANDARDS.md`.
