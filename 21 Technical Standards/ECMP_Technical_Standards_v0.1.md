# ECMP Technical Standards

| Field | Value |
|---|---|
| ID | TS-001 |
| Version | 0.2 |
| Owner | Tech Lead |
| Reviewer | Solution Architect |
| Approver | Architecture Board |
| Status | 🟢 Approved (baseline Sprint-01) |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

Standar implementasi teknis untuk semua kode ECMP. Baseline ini diturunkan dari implementasi aktual `implementation/backend` dan ADR yang sudah Accepted — bukan aspirasi. Deviasi membutuhkan ADR (lihat `../18 Architecture Governance`).

## 1. Python / FastAPI Standard

Stack: Python 3.12+, FastAPI, SQLAlchemy 2.x, Pydantic v2, Alembic, PostgreSQL (ADR-004).

### 1.1 Struktur modul (ADR-005 — minimal split)
```text
app/
├── main.py        # Presentation: routes + error handlers SAJA
├── service.py     # Application: business actions (register_case, get_case)
├── models.py      # Persistence: SQLAlchemy models (cases, audit_log, outbox)
├── schemas.py     # Kontrak request/response (Pydantic, selaras OpenAPI)
├── auth.py        # AuthN/AuthZ dependency
├── errors.py      # ApiError hierarchy → error envelope
├── db.py          # Infrastructure: engine/session
└── settings.py    # Konfigurasi via environment
```

### 1.2 Aturan dependensi
- Arah dependensi: `main.py → service.py → models.py/db.py`. Tidak boleh dibalik.
- **Route handler dilarang memuat business rule.** Handler hanya: validasi kontrak (via Pydantic), delegasi ke `service`, mapping hasil ke response schema.
- `service.py` **tidak boleh mengimpor FastAPI** — business action harus bisa diuji tanpa HTTP client.
- Full layering (package `domain/`, `application/`, repository interface) baru diadopsi saat service punya >1 aggregate — direview di gate G1 (ADR-005 aturan 3).

### 1.3 Bahasa
- Pydantic **v2** untuk semua kontrak; `Literal[...]` untuk enum kontrak (contoh: `CaseType`, `Priority` di `schemas.py`).
- Type hints wajib pada signature publik; `from __future__ import annotations` di setiap modul.
- Lint: **ruff** dikonfigurasi di `implementation/backend/pyproject.toml` — line length 100, rules `E,F,W,I,B`, ignore `N815` (field camelCase disengaja untuk kontrak API) dan `B008` (idiom `Depends(...)` FastAPI). Ruff hijau adalah syarat CI.

## 2. API / REST Standard

- Resource = **kata benda jamak**: `/v1/cases`, `/v1/cases/{caseId}`. Bukan verb (`/createCase` dilarang).
- Semua path produk diprefix **`/v1`** (ADR-006). `/health` tetap tanpa versi (operasional).
- Endpoint baru **hanya boleh ada jika sudah terdaftar** di `07 API Catalog/openapi/` (catalog-first). **Pengecualian tunggal:** endpoint dev berprefix `/_dev/` yang di-gate flag `ECMP_ENABLE_DEV_ENDPOINTS` (default mati; **dilarang aktif di deployment shared/prod** — di dalam proses test suite/CI flag boleh dinyalakan karena diperlukan untuk menguji endpoint dev itu sendiri) — selaras DoD `22 Engineering Handbook`. Docs interaktif FastAPI (`/_dev/docs`, `/_dev/openapi.json`) masuk pengecualian yang sama dan mengikuti flag.

### 2.1 Status code map
| Situasi | Status | `code` di envelope |
|---|---|---|
| Create sukses | 201 | — |
| Read sukses | 200 | — |
| Payload/enum/field invalid | 400 | `VALIDATION_ERROR` |
| Token hilang/salah | 401 | `UNAUTHENTICATED` |
| Token sah tanpa permission | 403 | `FORBIDDEN` |
| Resource tidak ada | 404 | `NOT_FOUND` |

### 2.2 Error envelope (wajib di SEMUA respons 4xx)
```json
{ "code": "VALIDATION_ERROR", "message": "...", "details": { "caseType": "..." } }
```
`details` opsional (dipakai untuk validation error per-field). Tidak ada format error lain — termasuk default FastAPI `{"detail": ...}`; error handler di `main.py` menormalkan semuanya ke envelope ini.

### 2.3 Idempotency
`Idempotency-Key` **out of scope Sprint-01** (FRD §9, DEC-002). Ditinjau ulang saat ada integrasi multi-client nyata. Dilarang membangun mekanisme idempotency sebelum keputusan itu.

## 3. Pagination Standard (untuk list API mendatang)

Belum ada list endpoint di Sprint-01; standar ini mengikat begitu list API pertama masuk katalog.

- Query param: `page` (mulai 1, default 1) dan `pageSize` (default **20**, max **100**). `pageSize > 100` → `400 VALIDATION_ERROR`.
- Response memakai komponen **`PageMeta`**:

```json
{ "items": [ ... ], "page": 1, "pageSize": 20, "totalItems": 42 }
```

- `PageMeta` didefinisikan sekali sebagai komponen di OpenAPI dan direferensikan semua list API. Cursor-based pagination baru dipertimbangkan (via ADR) bila ada bukti masalah skala.

## 4. Naming Standard lintas lapisan

- **API & event payload: camelCase.** **Kolom DB: snake_case.** Mapping dilakukan di boundary `service.py`/`schemas.py`, tidak bocor ke lapisan lain.
- Contoh mapping entitas Case (kontrak `schemas.py` ↔ tabel `cases`):

| API (camelCase) | DB (snake_case) |
|---|---|
| `caseId` | `case_id` |
| `customerId` | `customer_id` |
| `caseType` | `case_type` |
| `priority` | `priority` |
| `subject` | `subject` |
| `description` | `description` |
| `status` | `status` |
| `channel` | `channel` |
| `customerVerified` | `customer_verified` |
| `createdAt` | `created_at` |
| `createdBy` | `created_by` |
| `updatedAt` | `updated_at` |
| — (tidak diekspos di response) | `updated_by` |

- Nama event: PascalCase sesuai Event Catalog (`CaseCreated`); ID enterprise (`EVT-001`) disimpan bersama nama di tabel `outbox`.
- Enum kontrak: UPPER_SNAKE (`COMPLAINT`, `HIGH`) — konsisten API dan DB.
- Nilai audit log: `action` memakai verb lowercase bertitik (`case.create`, `case.assign`, ...), `entity_type` memakai nama entity PascalCase (`Case`).
- Konvensi audit di atas **sengaja berbeda** dari gaya enum UPPER_SNAKE; ini normatif untuk `audit_log` dan dirujuk `06 Data Dictionary`.

## 5. Database Standard

- **Setiap perubahan skema wajib lewat Alembic revision** — tidak ada `create_all`/DDL manual di environment bersama. Baseline: `alembic/versions/0001_initial_cases_audit_outbox.py`.
- Kolom audit standar untuk **entitas mutable** (contoh: `cases`): `created_at`, `created_by`, `updated_at`, `updated_by` — semuanya NOT NULL.
- `audit_log` **append-only** (BR-008): tidak ada jalur UPDATE/DELETE di aplikasi; record audit ditulis **dalam transaksi yang sama** dengan write bisnis.
- `outbox` mengikuti pola transactional outbox (ADR-009) — lihat `../19 Reference Architecture/PATTERNS.md` §7.
- Semua timestamp **UTC**, kolom `DateTime(timezone=True)`. Konversi timezone adalah urusan presentasi, bukan penyimpanan.
- Primary key string ber-prefix untuk ID enterprise-visible (`CASE-...`); UUID untuk ID internal (`log_id`, `outbox_id`).

## 6. Logging Standard

- Structured logging (JSON) + correlation-id propagation = **backlog gate G1** — belum ada di slice Sprint-01; dilarang membangun framework logging generik sebelum itu (anti gold-plating).
- Aturan yang berlaku **sekarang**: **dilarang menulis PII ke log** — termasuk `description`, `subject`, dan payload pelanggan. Log hanya boleh memuat ID (`caseId`, `customerId` bila perlu untuk trace) dan metadata teknis.
- Dilarang log token/credential dalam bentuk apa pun.

## 7. Docker Standard

- `implementation/infrastructure/docker-compose.yml` (PostgreSQL 16) adalah standar **DEV lokal**. Aplikasi jalan via `uvicorn` di host, bukan dalam container.
- Konfigurasi aplikasi via environment (`settings.py`); template di `implementation/backend/.env.example`, file `.env` di-gitignore.
- Image build aplikasi (Dockerfile, registry, tagging) = **keputusan deployment** yang menunggu pemilihan platform target — lihat `../14 Deployment Standards` (DEP-001). Dilarang membuat Dockerfile "sekalian" tanpa keputusan itu.

## Related
- ADR-004/005/006/007/009 (`../05 Architecture Decision Records`)
- `../07 API Catalog`, `../08 Event Catalog`
- `../22 Engineering Handbook` (kolaborasi harian), `../13 Test Strategy`
