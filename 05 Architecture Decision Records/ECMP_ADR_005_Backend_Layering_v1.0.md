# ECMP_ADR_005_Backend_Layering_v1.0

| Field | Value |
|---|---|
| ID | ADR-005 |
| Version | 1.0 |
| Owner | Tech Lead |
| Reviewer | Solution Architect |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

- ADR Status: Accepted
- Date: 2026-07-21
- Decision Owners: Tech Lead, Solution Architect
- Related Domains: Implementation (backend)

## Context
Prinsip `Presentation → Application → Domain ← Infrastructure` disebut di Reference Architecture tetapi belum diputuskan sebagai mandat. Backend Sprint-01 semula satu file `main.py`. Scaffold 4-layer penuh untuk service 2-endpoint adalah over-engineering (lihat `27 Project Decisions/archive/ECMP_SPRINT0_SENIOR_ENGINEER_REVIEW.md` §3).

## Decision Drivers
- Logika bisnis harus dapat diuji tanpa HTTP client
- Hindari indirection prematur pada aggregate tunggal
- Pintu tetap terbuka untuk layering penuh saat aggregate bertambah

## Options Considered
### Option A — Full Clean Architecture (4 package + ports/adapters)
Ditolak: ceremony > nilai untuk 2 endpoint.
### Option B — Minimal split (dipilih)
### Option C — Defer total (tetap satu file)
Ditolak: business logic tercampur route handler, tidak bisa diuji terpisah.

## Decision
**Minimal split wajib** untuk `implementation/backend`:

```text
app/
├── main.py        # Presentation: FastAPI routes + error handlers saja
├── service.py     # Application: business actions (register_case, get_case)
├── models.py      # Domain/persistence: SQLAlchemy models (Case, AuditLog, Outbox)
├── schemas.py     # Kontrak request/response (Pydantic, selaras OpenAPI)
├── auth.py        # AuthN/AuthZ dependency
├── errors.py      # ApiError hierarchy → error envelope {code, message, details?}
├── db.py          # Infrastructure: engine/session
└── settings.py    # Konfigurasi via environment
```

Aturan:
1. Route handler tidak boleh memuat business rule; hanya validasi kontrak + delegasi ke `service`.
2. `service` tidak boleh mengimpor FastAPI.
3. Full layering (package `domain/`, `application/`, repository interface) baru diadopsi saat service punya >1 aggregate — direview di gate G1.
4. CQRS **ditunda** (OQ-003 Resolved).

## Consequences
- Positif: business action `register_case` unit-testable; struktur tumbuh organik.
- Negatif: refactor kecil dibutuhkan saat naik ke layering penuh (diterima).
