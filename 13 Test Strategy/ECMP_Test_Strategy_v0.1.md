# ECMP Test Strategy

| Field | Value |
|---|---|
| ID | TST-001 |
| Version | 0.3 |
| Owner | QA Lead |
| Reviewer | BA / Tech Lead |
| Approver | Architecture Board |
| Status | 🟢 Approved (Sprint-10 RC1 exit criteria) |
| Last Review | 2026-07-22 |
| Next Review | 2027-01-22 |

Strategi pengujian ECMP dari fase slice (Sprint-01 → gate G1) hingga **RC exit criteria**
untuk Release Candidate internal / DEV (Sprint-10). Semua klaim merujuk pada pipeline dan
tes yang benar-benar ada; jenis tes yang belum relevan ditandai backlog dengan trigger.

## 1. Test Levels (yang berjalan sekarang)

| Level | Alat | Lokasi | Kapan jalan |
|---|---|---|---|
| Unit + API | pytest + FastAPI `TestClient` | `implementation/backend/tests/` | Lokal (SQLite file via `ECMP_DATABASE_URL` default) dan CI (PostgreSQL service) |
| Frontend unit | Vitest + Testing Library | `implementation/frontend/src/**/*.test.*` | Lokal dan `frontend-ci.yml` |
| Contract (schema) | Catalog OpenAPI ↔ runtime FastAPI schema | `tests/test_contract_conformance.py` + `openapi-spec-validator` di CI | Setiap PR/push backend / katalog API |
| Contract (response body) | HTTP via TestClient + JSON Schema vs catalog components | `tests/test_response_body_contract.py` | Setiap PR/push backend (pytest suite) |
| Migration | `alembic upgrade head` terhadap PostgreSQL 16 kosong | step "Run migrations" di `backend-ci.yml` | Setiap PR/push backend |
| Lint | ruff (backend), eslint (frontend) | CI masing-masing | Setiap PR/push path terkait |
| Bundle budget (warning) | `npm run check:bundle-budget` | `frontend-ci.yml` (`continue-on-error`) | Setelah production build |
| Accessibility (warning) | axe-core smoke (`npm run test:a11y`) | `frontend-ci.yml` (`continue-on-error`) | Setelah build |

Catatan level API: business action juga tercakup unit-level karena `service.py` bebas FastAPI (ADR-005) — bisa dites tanpa HTTP bila diperlukan.

## 2. Mapping TC → tes nyata

Sumber ID: `26 Traceability/traceability.yaml`. Tes backend di `implementation/backend/tests/`.

| TC | Deskripsi | Tes nyata | Status |
|---|---|---|---|
| TC-001 | Create complaint with valid customer succeeds | `test_create_and_get_case` (jalur create, 201 + status `REGISTERED`); negatif: `test_create_invalid_enum_400_with_details`, `test_create_missing_mandatory_field_400`, `test_create_boundary_violations_400` | ✅ Implemented |
| TC-002 | Get case by id returns case | `test_create_and_get_case` (jalur get), `test_readonly_principal_can_read`, `test_case_survives_engine_reset`; negatif: `test_get_not_found_404_with_error_envelope`, `test_get_missing_token_401`, `test_get_without_permission_403` | ✅ Implemented |
| TC-003 | Assign case updates assignee and emits event | `test_tc003_*` di `test_lifecycle.py` | ✅ Implemented |
| TC-004 | Invalid status transition rejected | `test_tc004_*` di `test_lifecycle.py` | ✅ Implemented |
| TC-005 | Audit record persisted on create (same transaction) | `test_create_persists_audit_and_outbox_in_one_transaction` (audit `case.create` + outbox `EVT-001` — BR-008/ADR-009) | ✅ Implemented |

Jalur AuthN/AuthZ (ADR-007) juga ter-cover: `test_create_missing_token_401_with_error_envelope`, `test_create_invalid_token_401`, `test_create_without_permission_403`.

## 3. Entry / Exit Criteria per Gate

### Gate G0 (platform floor — DEC-002)
- **Entry:** slice create/get terdefinisi di FRD + OpenAPI; CI pipeline ada.
- **Exit (aspek tes):** backend CI hijau penuh (ruff → contract → migrate → pytest terhadap PostgreSQL); TC-001, TC-002, TC-005 implemented dan lulus; error envelope terverifikasi di tes untuk 400/401/403/404. Status: **terpenuhi** — tersisa sign-off manusia (Tech Lead + SA).

### Gate G1 (lifecycle contract — assign/status)
- **Entry:** OpenAPI API-003/API-004 dan payload EVT-002/EVT-003 merged **sebelum kode** (contract-PR terpisah); transition matrix disepakati.
- **Exit:** TC-003/TC-004 implemented — termasuk tes transisi ilegal (state tidak berubah), authz permission baru (`cases:assign` dst.), dan audit/outbox pada assign/status mengikuti pola create; CI tetap hijau.

### RC Exit Criteria (Sprint-10 — internal / DEV validation)

Berlaku untuk tag `vX.Y.Z-rc.N` (lihat `16 Release Management/ECMP_RC_Release_Checklist_v0.1.md`).
**Bukan** exit criteria shared UAT/PROD (tetap diblokir ADR-010 / ADR-012).

| Area | Floor / expectation | Evidence |
|---|---|---|
| Backend coverage | pytest `--cov-fail-under=90` terhadap `app` | `backend-ci.yml` |
| Frontend coverage | Vitest coverage thresholds ≥ measured baseline (lines/statements **12%**, functions/branches **50%**) | `frontend-ci.yml` → `npm run test:coverage` + `vite.config.ts` |
| Contract tests | (1) Schema conformance catalog ↔ runtime; (2) **Response-body** validation of live HTTP JSON against OpenAPI component schemas for create/get/list/assign/status/timeline/notes + Error envelope | `test_contract_conformance.py`, `test_response_body_contract.py` |
| Integration / E2E | **Required for RC:** API integration via FastAPI `TestClient` (same process as CI). **Not required for RC1:** full browser E2E (Playwright/Cypress) — remains backlog until shared SIT exists. Manual UI smoke on DEV optional and recorded in RC checklist notes. | pytest suite; backlog §6 |

RC Go hanya jika keempat baris di atas terpenuhi pada commit kandidat + checklist REL-RC-001 lengkap.

## 4. Tanggung Jawab

| Peran | Tanggung jawab tes |
|---|---|
| Developer | Menulis/meng-update tes bersama kode (DoD ENG-003 butir 2); menjaga mapping TC → tes saat menambah TC |
| Tech Lead | Review kecukupan tes di PR (ENG-004); memutuskan kapan level tes baru dibutuhkan |
| QA Lead | Memelihara dokumen ini + mapping TC di traceability; merumuskan exit criteria tes per gate / RC |
| BA | Memastikan setiap AC di FRD punya TC ID |
| Release Manager | Memverifikasi RC exit criteria pada checklist REL-RC-001 sebelum tag |

## 5. Test Data & Environment
- Tes tidak bergantung state eksternal: fixture drop/create data per tes; skema dari Alembic.
- Lokal: SQLite file (`ecmp_test.db`) untuk kecepatan; CI: PostgreSQL 16 service — paritas dengan target produksi diverifikasi tiap PR. Perilaku yang berbeda antar dua DB harus dites di CI (PostgreSQL adalah wasit).
- Data uji sintetis (`CUST-10001`); dilarang data pelanggan nyata di repo/tes.
- Frontend Vitest memakai jsdom — bukan pengganti browser E2E.

## 6. Backlog (dengan trigger, bukan wacana)
- **Browser E2E (Playwright/Cypress)** — trigger: environment SIT ter-provision + keputusan tooling; bukan blocker RC1 internal.
- **Performance test** — target numerik ada via DEC-005 (p95 baca <300ms, tulis <800ms, throughput baseline 10 rps — lihat `04 Solution Architecture/ECMP_NFR_Specification_v0.1.md`). Blocker: environment SIT belum ter-provision (ADR-010). Pendekatan: smoke k6/locust terhadap SIT begitu tersedia.
- **Security scan (SAST)** — kandidat penambahan CI sebelum shared UAT (bersamaan aktivasi fase target ADR-007 / ADR-012). Dependency audit sudah ada (`pip-audit`, `npm audit`).
- **Outbox relay test** — saat broker dipilih (trigger ADR-009).
- **Hardening quality gates** — bundle-size + a11y dari warning → blocking setelah baseline stabil (post-RC1).
- **Naikkan frontend coverage floor** — seiring penambahan unit/component tests; threshold tidak boleh diturunkan tanpa QA Lead.

## Related
- `../26 Traceability/traceability.yaml` — SoT mapping TC
- `../.github/workflows/backend-ci.yml` — pipeline backend
- `../.github/workflows/frontend-ci.yml` — pipeline frontend (coverage + warning gates)
- `../16 Release Management/ECMP_RC_Release_Checklist_v0.1.md` (REL-RC-001)
- `../22 Engineering Handbook/DEFINITION_OF_DONE.md` (ENG-003)
- `../27 Project Decisions/DEC-002_Build_Authorization_G0_v1.0.md`
