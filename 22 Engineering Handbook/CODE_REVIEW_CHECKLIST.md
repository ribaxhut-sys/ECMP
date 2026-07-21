# Code Review Checklist

| Field | Value |
|---|---|
| ID | ENG-004 |
| Version | 0.1 |
| Owner | Engineering Manager |
| Reviewer | Tech Lead |
| Approver | Engineering Manager |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

Checklist untuk **reviewer** PR `implementation/**`. Fokus pada hal yang tidak tertangkap otomatis oleh CI. Author memakai `PR_CHECKLIST.md` (ENG-002); reviewer memakai daftar ini.

## 1. Kontrak vs runtime
- [ ] Path, method, status code, dan bentuk payload sama persis dengan OpenAPI di `07 API Catalog/openapi/`.
- [ ] Field API camelCase, kolom DB snake_case; mapping hanya di boundary (TS-001 §4).
- [ ] Endpoint baru sudah ada di katalog SEBELUM kode ini (catalog-first). Tidak ada endpoint "bonus".
- [ ] Event yang di-emit terdaftar di `08 Event Catalog/events/events.yaml` dengan payload sesuai.

## 2. Error envelope
- [ ] Semua jalur 4xx mengembalikan `{code, message, details?}` — tidak ada `{"detail": ...}` bawaan FastAPI yang lolos.
- [ ] Kode benar: 400 `VALIDATION_ERROR`, 401 `UNAUTHENTICATED`, 403 `FORBIDDEN`, 404 `NOT_FOUND`.
- [ ] Semantik 401 vs 403 benar: token hilang/salah → 401; token sah tanpa permission → 403 (ADR-007).
- [ ] `message`/`details` tidak membocorkan PII atau internal (stack trace, SQL).

## 3. Audit & konsistensi write (BR-008 / ADR-009)
- [ ] Setiap write bisnis menulis record `audit_log` **dalam transaksi yang sama** — bukan setelah commit.
- [ ] Tidak ada kode yang meng-UPDATE/DELETE `audit_log` (append-only).
- [ ] Event keluar lewat tabel `outbox` dalam transaksi yang sama; tidak ada publish langsung ke broker/HTTP dari service.
- [ ] Entitas mutable mengisi `created_at/created_by/updated_at/updated_by` (UTC).

## 4. Layering (ADR-005)
- [ ] Route handler bebas business rule; logika ada di `service.py`.
- [ ] `service.py` tidak mengimpor FastAPI.

## 5. Secret & konfigurasi
- [ ] Tidak ada token, password, connection string, atau key literal di kode/tes/fixture.
- [ ] Konfigurasi baru lewat `settings.py` + entri di `.env.example` (tanpa nilai rahasia).
- [ ] Tidak ada logging PII (`description`, `subject`, data pelanggan) atau credential.

## 6. Scope (DEC-001 / DEC-002)
- [ ] Perubahan berada dalam otorisasi build aktif. Non-goals DEC-002 (assign/status transition, notification delivery, appointment/work order, frontend produk, idempotency key, audit-on-read, broker, SSO/IdP, framework generik) → **tolak PR**, arahkan ke gate yang tepat.
- [ ] Tidak ada fitur yang menyimpang dari baseline bisnis DEC-001 tanpa keputusan baru.
- [ ] PR merujuk BR/FR/ADR ID yang relevan; klaim di deskripsi PR cocok dengan diff.

## Sikap review
- Blocking = pelanggaran kontrak, audit, secret, atau scope. Style yang sudah dijaga ruff tidak perlu diperdebatkan manual.
- Reviewer boleh (dan sebaiknya) menjalankan tes lokal bila jalur transaksi/migrasi berubah.

## Related
- `DEFINITION_OF_DONE.md` (ENG-003), `PR_CHECKLIST.md` (ENG-002)
- `../21 Technical Standards/ECMP_Technical_Standards_v0.1.md` (TS-001)
