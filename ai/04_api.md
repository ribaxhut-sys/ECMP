# 04 — API Context

| Field | Value |
|---|---|
| ID | AI-CTX-004 |
| Version | 1.0 |
| Owner | Backend Lead |
| Reviewer | Solution Architect |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Rules
- No endpoint without OpenAPI in `07 API Catalog/openapi/`. Satu-satunya pengecualian: endpoint dev yang di-gate flag `ECMP_ENABLE_DEV_ENDPOINTS` dan berprefix `/_dev/` (mati default; dilarang di deployment shared/prod — boleh nyala di dalam proses test suite; lihat DoD `22 Engineering Handbook`). Docs interaktif FastAPI juga hidup di `/_dev/` mengikuti flag ini. Konformansi runtime vs spec dijaga `tests/test_contract_conformance.py`.
- Update generated catalog: `python tools/generate_api_catalog.py`
- AuthN/AuthZ required by default. 401 = `UNAUTHENTICATED`, 403 = `FORBIDDEN` (ADR-007).
- Error model wajib: envelope `{code, message, details?}` untuk semua 4xx/5xx (lihat `21 Technical Standards`).
- Versioning: URL prefix `/v1` per ADR-006; breaking change = bump prefix + deprecation policy (2 minor + `Sunset` header).
- Pagination list API: `page`/`pageSize` + `PageMeta` (lihat template `24 Templates/API_SPEC_TEMPLATE.yaml`).

## Starter Spec
- `07 API Catalog/openapi/case-service.v1.yaml`

## IDs
Use `API-xxx` in FRD/traceability/PRs.
