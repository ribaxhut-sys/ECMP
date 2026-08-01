# ECMP Backend (Sprint-01)

| Field | Value |
|---|---|
| ID | IMP-BE-001 |
| Version | 0.3 |
| Owner | Tech Lead |
| Reviewer | Solution Architect |
| Approver | Engineering Manager |
| Status | 🟢 Approved (G0 floor landed) |
| Last Review | 2026-07-21 |
| Next Review | 2026-08-21 |

## Stack (ADR-004)
- Python 3.12+ / FastAPI
- PostgreSQL + Alembic — wajib untuk CI/shared env (DoD). SQLite fallback **hanya legal untuk eksperimen dev lokal tanpa Docker**; skema otoritatif tetap Alembic (`create_all` di lifespan hanya safety net jalur fallback ini)
- OpenAPI SoT: `../../07 API Catalog/openapi/case-service.v1.yaml` (base path `/v1` per ADR-006)
- Events: transactional outbox (ADR-009), kontrak di `../../08 Event Catalog/events/events.yaml`

## Struktur (ADR-005 — minimal split)
```text
app/
├── main.py      # Presentation: routes + error handlers
├── service.py   # Application: business actions (register_case, get_case)
├── models.py    # SQLAlchemy models (cases, audit_log, outbox)
├── schemas.py   # Kontrak Pydantic (camelCase, selaras OpenAPI)
├── auth.py      # AuthN/AuthZ (ADR-007 slice phase)
├── errors.py    # Error envelope {code, message, details?}
├── db.py        # Engine/session
└── settings.py  # Konfigurasi via environment
alembic/         # Migrasi (revision 0001: cases, audit_log, outbox)
```

## Quick start
```bash
# 1. Database (PostgreSQL via Docker; atau lewati untuk SQLite lokal)
docker compose -f ../infrastructure/docker-compose.yml up -d

# 2. Konfigurasi
cp .env.example .env   # sesuaikan bila perlu; JANGAN commit .env

# 3. Install + migrasi + run
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements.txt        # runtime; tooling tes/lint: requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload
```
API docs interaktif hanya aktif saat `ECMP_ENABLE_DEV_ENDPOINTS=true`, di
http://localhost:8000/_dev/docs (prefix `/_dev/` per pengecualian catalog-first TS-001 §2).
Endpoint produk di bawah `/v1`.

## Konfigurasi environment (ADR-010)
- `ECMP_ENV=dev` (default) | `sit` | `uat` | `prod`. Di luar `dev`, aplikasi **menolak start**
  bila `ECMP_DEV_TOKEN` tidak di-set (default `dev-token` dilarang) atau dev endpoints aktif
  (gate ADR-007, ditegakkan `settings.validate_runtime_config`).

## Auth (slice — lihat ADR-007 + Limitations Register)
- `Authorization: Bearer <ECMP_DEV_TOKEN>` → CS Agent (`cases:create`, `cases:read`)
- `Authorization: Bearer <ECMP_DEV_READONLY_TOKEN>` → Viewer (`cases:read`)
- `Authorization: Bearer <ECMP_DEV_SUPERVISOR_TOKEN>` → Supervisor (`cases:assign`, `cases:read`, `cases:create`, `dashboard:read`; supervised `UNIT-01`)
- `Authorization: Bearer <ECMP_DEV_NOPERM_TOKEN>` → principal tanpa permission (untuk uji 403)
- 401 = autentikasi gagal; 403 = tanpa permission. DEV/CI only.

## CAP-007 / API-040 (B2-14)
- `GET /v1/dashboard/queues` — aggregates unit-scoped (permission `dashboard:read`); kontrak `../../07 API Catalog/openapi/dashboard-queues.v1.yaml` 1.0.0.
- Tes: `tests/test_dashboard_queues_api040.py` (TC-040).
- Tidak memakai API-390 / API-513.

## Audit & Events (G0)
- Create case menulis `cases` + `audit_log` (BR-008/FR-001c) + `outbox` (EVT-001) dalam **satu transaksi**.
- `/_dev/events` (inspektur outbox) dan `POST /_dev/outbox/drain` (publisher in-process DEV
  per ADR-009 §2 — menandai `published_at`) hanya aktif bila `ECMP_ENABLE_DEV_ENDPOINTS=true`.
- Broker/relay nyata menggantikan drainer ini pada trigger revisit ADR-009.

## Tests & lint
```bash
pip install -r requirements-dev.txt
pytest -q
ruff check app tests
```
- Skema tes dibuat via `alembic upgrade head` (bukan `create_all`) — drift model vs migrasi
  gagal di suite.
- Default lokal SQLite; **PostgreSQL adalah wasit**. Jalankan suite terhadap Postgres lokal:
  `$env:ECMP_DATABASE_URL="postgresql+psycopg://ecmp:ecmp_local_only@localhost:5432/ecmp"; pytest -q`
  (compose harus jalan; lihat `../infrastructure/docker-compose.yml`).

CI: `.github/workflows/backend-ci.yml` — Postgres service → ruff (backend + tools/portal) →
validasi semua spec OpenAPI (termasuk drafts) → alembic → pytest dengan gate coverage 90% →
job `pip-audit` untuk dependensi runtime.
