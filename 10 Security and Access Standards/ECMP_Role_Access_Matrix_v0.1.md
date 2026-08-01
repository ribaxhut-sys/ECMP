# ECMP Role Access Matrix v0.1

> Nama file `..._v0.1.md` sengaja dipertahankan agar tautan lintas-dokumen stabil; **versi konten otoritatif = field `Version` di header** (saat ini 0.3).

| Field | Value |
|---|---|
| ID | SEC-RAM-001 |
| Version | 0.4 |
| Owner | Security Officer |
| Reviewer | Tech Lead / Domain PO ECMF |
| Approver | Business Owner |
| Status | 🟢 Approved (Sprint-01 enforced; Sprint-02/03 Planned rows) |
| Last Review | 2026-08-01 |
| Next Review | 2027-01-21 |

## Scope
Matriks minimal untuk Sprint-01 (per senior review Task 5 & DEC-002). **Hanya** role dan permission yang benar-benar ada di kode. Role/permission lain di luar lingkup gate ini dan TIDAK boleh diimplementasikan tanpa revisi dokumen ini.

Versi 0.2 menambahkan bagian **Planned — Sprint-02** sebagai revisi prasyarat yang diminta FRD-002/FRD-003; seluruh isinya berstatus Planned (belum enforced di kode).

Versi 0.3 (Sprint-02A contract freeze, **DEC-006** 2026-07-21): nama permission Sprint-02 **difinalkan** — `cases:assign` dan `cases:status` (kandidat `cases:transition` ditolak; nama mengikuti endpoint API-004 `POST /v1/cases/{caseId}/status`). Definisi beku; status enforcement tetap Planned sampai implementasi Sprint-02B.

Versi 0.4 (B2-12 / **DEC-CAP007-BQ-001** 2026-08-01): Planned Sprint-03 menambahkan pemetaan **`dashboard:read`** → API-040 (CAP-007 / FRD-006 LOCKED). Nama permission **tidak diinvent** — sudah dipakai CAPABILITY-013 / DEC-016. Enforcement API-040 tetap Planned sampai kontrak API-040 normatif + implementasi.

## Roles

| Role | Deskripsi | Principal contoh (slice) |
|---|---|---|
| CS Agent | Customer Service — membuat dan melihat case | `cs.agent.1` (token `ECMP_DEV_TOKEN`) |
| Viewer | Read-only — hanya melihat case | `viewer.1` (token `ECMP_DEV_READONLY_TOKEN`) |

## Permission Matrix

| Permission | CS Agent | Viewer | Enforced di |
|---|---|---|---|
| `cases:create` | ✅ | ❌ | `app/auth.py` + `POST /v1/cases` |
| `cases:read` | ✅ | ✅ | `app/auth.py` + `GET /v1/cases/{id}` (+ timeline/notes list Sprint-06) |
| `cases:notes:create` | ✅ | ❌ | `app/auth.py` + `POST /v1/cases/{id}/notes` (Sprint-06) |

## Planned — Sprint-02 (menunggu DoR FRD-002/003, revisi ini prasyaratnya)

> **Status: PLANNED — belum enforced di kode.** Bagian ini adalah revisi matriks yang menjadi prasyarat FRD-002 (Lifecycle) dan FRD-003 (Customer 360) sesuai Dependencies masing-masing FRD. Implementasi menunggu G0 exit (DEC-002) dan DoR FRD terkait. Permission slice yang implemented tetap hanya tabel di atas.

### Role Planned
| Role | Deskripsi | Persona | Sumber |
|---|---|---|---|
| Supervisor | Assign/reassign case ke handler/unit di unitnya | P-02 | FRD-002 (FR-003) |
| Handler | Menjalankan transisi status pada case yang di-assign padanya | P-04 | FRD-002 (FR-004) |

### Permission Matrix Planned
| Permission | CS Agent | Supervisor | Handler | Viewer | Target enforcement | Sumber |
|---|---|---|---|---|---|---|
| `cases:assign` (nama beku, DEC-006) | ❌ | ✅ Planned | ❌ | ❌ | `POST /v1/cases/{caseId}/assign` (API-003, contract frozen) | FRD-002 FR-003, BR-002 |
| `cases:status` (nama beku, DEC-006) | ❌ | ❌ | ✅ Planned | ❌ | `POST /v1/cases/{caseId}/status` (API-004, contract frozen) | FRD-002 FR-004, BR-001 |
| `cases:read` | ✅ (implemented) | ✅ Planned | ✅ Planned | ✅ (implemented) | `GET /v1/cases/{caseId}` | FRD-002 |
| `customers:read` | ✅ Planned — **unmasked** (role CS per BR-CRM-02 baseline) | ✅ Planned — masked | ✅ Planned — masked | ✅ Planned — masked | `GET /v1/customers/{customerId}` (API-010) | FRD-003 FR-010, BR-CRM-02 |

## Planned — Sprint-03 (CAP-007 / FRD-006 — DEC-CAP007-BQ-001)

> **Status: PLANNED — API-040 belum normatif / belum diimplementasi pada path Sprint ECMF.**  
> Permission code `dashboard:read` sudah ada di matriks RBAC foundation (CAPABILITY-013 / DEC-016). Baris ini hanya memetakan **API-040** CAP-007.

| Permission | CS Agent | Supervisor | Handler | Viewer | Target enforcement | Sumber |
|---|---|---|---|---|---|---|
| `dashboard:read` | ❌ | ✅ Planned (unit-scoped) | ❌ | ❌ | `GET /v1/dashboard/queues` (API-040) | FRD-006 FR-040, DEC-CAP007-BQ-001 §2/§4, DEC-016 |

Catatan Sprint-03:
- Actor v0.1 = **Supervisor unit-scoped only**; Manager/Executive deferred (DEC-CAP007-BQ-001 §4).
- Tidak menambah permission baru selain `dashboard:read`.

Catatan:
- Masking BR-CRM-02 (baseline DEC-004): field kontak pelanggan (phone/email) **dimask** untuk role non-CS; role CS Agent melihat unmasked (need-to-know).
- Assignment lintas unit hanya supervisor unit induk (BR-002 / BR-ECMF-02, baseline DEC-004); enforcement org-unit menunggu claims `orgUnitId` (limitation L-3, gate G1).
- ~~Nama permission transisi status mengikuti endpoint `POST /v1/cases/{caseId}/status`; bila FRD-002/OpenAPI memfinalkan nama lain (mis. `cases:transition`), revisi berikut menyelaraskan.~~ **Selesai (DEC-006):** nama final = `cases:status`, dibekukan bersama kontrak API-004; alias `cases:transition` tidak dipakai dan referensinya di dokumen lain sudah diselaraskan.

## Semantik status HTTP (ADR-007)
- Token hilang/salah → **401** `UNAUTHENTICATED`
- Token sah tanpa permission → **403** `FORBIDDEN`

## SoT (ADR-008)
Role/Permission dimiliki **Core Platform**. Administration hanya konfigurator (proses perubahan + approval BR-ADM-01). Matriks ini adalah baseline dokumen sampai persistensi Role/Permission dibangun.

## Related
- `ECMP_AuthN_Limitations_Register_v0.1.md`
- ADR-007, ADR-008, BR-007, BR-008
