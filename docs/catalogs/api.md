# API Catalog

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

The API Catalog (API-000, 🟢 Approved baseline) is the contract-first inventory of all ECMP APIs:

- **Implemented (Sprint-01, case-service v1):** API-001 `POST /v1/cases` (create case, emits EVT-001) and API-002 `GET /v1/cases/{caseId}` — both bearer-auth with `cases:create`/`cases:read` permissions; plus unauthenticated `GET /health`.
- **Planned:** API-003 assign case, API-004 change status, API-005 list cases, API-010 customer reference read, API-040 dashboard queues (draft skeletons under `openapi/drafts/`, normative only after gate G1 merge).
- Standards: error envelope `Error{code, message, details?}`, URL versioning `/v1` (ADR-006), pagination per `21 Technical Standards`, NFR baselines per DEC-005.

No API may be created outside this catalog (hard constraint).

**Canonical source:** `07 API Catalog/README.md` and `07 API Catalog/openapi/case-service.v1.yaml`.
