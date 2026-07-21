# ECMP Test Strategy

| Field | Value |
|---|---|
| ID | TST-001 |
| Version | 0.2 |
| Owner | QA Lead |
| Reviewer | BA / Tech Lead |
| Approver | Architecture Board |
| Status | 🟢 Approved (baseline Sprint-01) |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

Strategi pengujian ECMP untuk fase slice (Sprint-01 → gate G1). Semua klaim di sini merujuk pada pipeline dan tes yang benar-benar ada; jenis tes yang belum relevan (UI, performance, security scan) ditandai sebagai backlog dengan trigger yang jelas.

## 1. Test Levels (yang berjalan sekarang)

| Level | Alat | Lokasi | Kapan jalan |
|---|---|---|---|
| Unit + API | pytest + FastAPI `TestClient` | `implementation/backend/tests/test_cases.py` | Lokal (SQLite file via `ECMP_DATABASE_URL` default) dan CI (PostgreSQL service) |
| Contract | `openapi-spec-validator` terhadap `07 API Catalog/openapi/case-service.v1.yaml` | step "Validate OpenAPI contract" di `backend-ci.yml` | Setiap PR/push yang menyentuh backend atau katalog API |
| Migration | `alembic upgrade head` terhadap PostgreSQL 16 kosong | step "Run migrations" di `backend-ci.yml` | Setiap PR/push backend |
| Lint | ruff (`pyproject.toml`) | step pertama CI | Setiap PR/push backend |

Catatan level API: business action juga tercakup unit-level karena `service.py` bebas FastAPI (ADR-005) — bisa dites tanpa HTTP bila diperlukan.

## 2. Mapping TC → tes nyata

Sumber ID: `26 Traceability/traceability.yaml`. Semua tes di `implementation/backend/tests/test_cases.py`.

| TC | Deskripsi | Tes nyata | Status |
|---|---|---|---|
| TC-001 | Create complaint with valid customer succeeds | `test_create_and_get_case` (jalur create, 201 + status `REGISTERED`); negatif: `test_create_invalid_enum_400_with_details`, `test_create_missing_mandatory_field_400`, `test_create_boundary_violations_400` | ✅ Implemented |
| TC-002 | Get case by id returns case | `test_create_and_get_case` (jalur get), `test_readonly_principal_can_read`, `test_case_survives_engine_reset`; negatif: `test_get_not_found_404_with_error_envelope`, `test_get_missing_token_401`, `test_get_without_permission_403` | ✅ Implemented |
| TC-003 | Assign case updates assignee and emits event | — | 🕓 Planned (Sprint-02; kontrak dibekukan di gate G1 sebelum kode) |
| TC-004 | Invalid status transition rejected | — | 🕓 Planned (Sprint-02, gate G1) |
| TC-005 | Audit record persisted on create (same transaction) | `test_create_persists_audit_and_outbox_in_one_transaction` (audit `case.create` + outbox `EVT-001` dalam satu transaksi — BR-008/ADR-009) | ✅ Implemented |

Jalur AuthN/AuthZ (ADR-007) juga ter-cover: `test_create_missing_token_401_with_error_envelope`, `test_create_invalid_token_401`, `test_create_without_permission_403`.

## 3. Entry / Exit Criteria per Gate

### Gate G0 (platform floor — DEC-002)
- **Entry:** slice create/get terdefinisi di FRD + OpenAPI; CI pipeline ada.
- **Exit (aspek tes):** backend CI hijau penuh (ruff → contract → migrate → pytest terhadap PostgreSQL); TC-001, TC-002, TC-005 implemented dan lulus; error envelope terverifikasi di tes untuk 400/401/403/404. Status: **terpenuhi** — tersisa sign-off manusia (Tech Lead + SA).

### Gate G1 (lifecycle contract — assign/status)
- **Entry:** OpenAPI API-003/API-004 dan payload EVT-002/EVT-003 merged **sebelum kode** (contract-PR terpisah); transition matrix disepakati.
- **Exit:** TC-003/TC-004 implemented — termasuk tes transisi ilegal (state tidak berubah), authz permission baru (`cases:assign` dst.), dan audit/outbox pada assign/status mengikuti pola create; CI tetap hijau.

## 4. Tanggung Jawab

| Peran | Tanggung jawab tes |
|---|---|
| Developer | Menulis/meng-update tes bersama kode (DoD ENG-003 butir 2); menjaga mapping TC → tes saat menambah TC |
| Tech Lead | Review kecukupan tes di PR (ENG-004); memutuskan kapan level tes baru dibutuhkan |
| QA Lead | Memelihara dokumen ini + mapping TC di traceability; merumuskan exit criteria tes per gate |
| BA | Memastikan setiap AC di FRD punya TC ID |

## 5. Test Data & Environment
- Tes tidak bergantung state eksternal: fixture `fresh_db` drop/create skema per tes.
- Lokal: SQLite file (`ecmp_test.db`) untuk kecepatan; CI: PostgreSQL 16 service — paritas dengan target produksi diverifikasi tiap PR. Perilaku yang berbeda antar dua DB harus dites di CI (PostgreSQL adalah wasit).
- Data uji sintetis (`CUST-10001`); dilarang data pelanggan nyata di repo/tes.

## 6. Backlog (dengan trigger, bukan wacana)
- **UI test** — saat frontend produk dimulai (di luar non-goals DEC-002).
- **Performance test** — separuh trigger sudah terpenuhi: target numerik ada via DEC-005 (p95 baca <300ms, tulis <800ms, throughput baseline 10 rps — lihat `04 Solution Architecture/ECMP_NFR_Specification_v0.1.md`). Blocker tersisa: environment SIT belum ter-provision (baseline platform ADR-010, aktif setelah fase target ADR-007). Pendekatan terencana: smoke test k6/locust terhadap SIT (skenario create/get case pada target DEC-005) begitu environment tersedia.
- **Security scan (SAST/dep audit)** — kandidat penambahan CI sebelum shared UAT (bersamaan aktivasi fase target ADR-007).
- **Outbox relay test** — saat broker dipilih (trigger ADR-009).

## Related
- `../26 Traceability/traceability.yaml` — SoT mapping TC
- `../.github/workflows/backend-ci.yml` — pipeline aktual
- `../22 Engineering Handbook/DEFINITION_OF_DONE.md` (ENG-003)
- `../27 Project Decisions/DEC-002_Build_Authorization_G0_v1.0.md`
