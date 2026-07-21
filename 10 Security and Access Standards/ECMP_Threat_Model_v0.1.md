# ECMP Threat Model v0.1

| Field | Value |
|---|---|
| ID | SEC-TM-001 |
| Version | 0.1 |
| Owner | Security Architect |
| Reviewer | Tech Lead / Solution Architect |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2026-10-21 |

## 1. Scope & Metodologi
Threat model **STRIDE** untuk lingkup slice nyata Sprint-01 (bukan arsitektur target). Komponen dinilai apa adanya sesuai kode di `implementation/backend/` dan dokumen baseline (ADR-007/008/009, INT-001, SEC-RAM-001, SEC-LIM-001). Kontrol yang dicantumkan hanya kontrol yang **benar-benar ada** di kode/dokumen; residual risk yang diterima sementara dirujuk ke `ECMP_AuthN_Limitations_Register_v0.1.md` (L-1..L-5) beserta gate penutupannya.

Komponen dalam scope:
1. FastAPI case-service (`POST /v1/cases`, `GET /v1/cases/{caseId}`, `/health`, `/_dev/events` flag-gated)
2. Database PostgreSQL (ADR-004; SQLite untuk test lokal)
3. Transactional outbox (ADR-009)
4. AuthN static dev-token dari environment (ADR-007 fase slice)
5. Integrasi Customer Master (INT-001 — stub aktif, real mode planned)
6. CI GitHub Actions (`backend-ci.yml`)

Out of scope versi ini: frontend (non-goal Sprint-0/G0 per DEC-002), message broker (ditunda per ADR-009), fitur Sprint-02+ (assign/status/customer 360 — masuk saat FRD-002/003 lolos DoR).

## 2. Analisis STRIDE per Komponen

### 2.1 FastAPI case-service
| STRIDE | Ancaman | Kontrol existing | Residual risk | Gate penutupan |
|---|---|---|---|---|
| S — Spoofing | Pemalsuan identitas via token tebakan/curian | Bearer token wajib untuk semua endpoint fungsional; token hilang/salah → 401 `UNAUTHENTICATED` (ADR-007) | Token statis tanpa expiry/issuer — bila bocor, akses penuh sesuai principal (**L-1**, **L-2**) | Shared UAT: JWT/OIDC fase target ADR-007 |
| T — Tampering | Payload berbahaya / input tidak valid | Validasi Pydantic → 400 `VALIDATION_ERROR` dengan Error envelope `{code, message, details?}`; batas `description` max 5000 char | Belum ada rate limiting / batas ukuran request agregat | Sebelum shared UAT (lihat Abuse cases §3) |
| R — Repudiation | Aktor menyangkal telah membuat case | Write-audit immutable (BR-008/FR-001c): `audit_log` ditulis dalam transaksi yang sama dengan write bisnis | Read-audit ditunda (**L-4**, OQ-007); principal tetap sehingga atribusi individual lemah (**L-2**) | Review saat UAT (L-4); user store/IdP (L-2) |
| I — Information Disclosure | Bocor data case/PII via response atau log | Error envelope tidak membocorkan stack trace; `description` (dapat memuat PII) dilarang masuk log aplikasi (Security Standards §4); `/_dev/events` mati default (`ECMP_ENABLE_DEV_ENDPOINTS`) dan tetap butuh auth + `cases:read` | Tanpa org-unit scoping — token sah dapat membaca case unit lain (**L-3**) | Gate G1: claims `orgUnitId` + enforcement |
| D — Denial of Service | Flood request create/read | Tidak ada kontrol khusus di slice | Mass create tidak dibatasi (lihat Abuse cases) | Sebelum shared UAT: rate limiting (backlog) |
| E — Elevation of Privilege | Token sah menjalankan aksi di luar permission | AuthZ per-permission: 403 `FORBIDDEN` bila permission hilang (`require_perm`, SEC-RAM-001) | Permission hardcoded di `auth.py` per principal — tidak dinamis sampai persistensi Role/Permission (ADR-008) | Persistensi Role/Permission Core Platform |

### 2.2 Database PostgreSQL / SQLite
| STRIDE | Ancaman | Kontrol existing | Residual risk | Gate penutupan |
|---|---|---|---|---|
| T — Tampering | Modifikasi/penghapusan jejak audit | `audit_log` append-only: tanpa jalur update/delete aplikasi (BR-CP-03); skema dikelola Alembic (revision terkontrol) | Append-only ditegakkan di lapisan aplikasi, belum ada DB-level guard (trigger/permission DB) | Review keamanan DB sebelum PROD (bersama `14 Deployment Standards`) |
| I — Information Disclosure | Akses langsung DB membuka PII (subject, description, customer_id) | Kredensial DB via environment (`.env` git-ignored); tidak ada secret di source | Enkripsi at-rest / kontrol akses DB granular belum ditetapkan (keputusan platform deployment belum diambil) | Keputusan platform deployment (`14 Deployment Standards`) |
| R — Repudiation | Kehilangan jejak siapa mengubah data | Standar Kolom Audit (`created_by`/`updated_by`) + `audit_log` satu transaksi | `old_value` belum disimpan (menyusul saat ada mutasi — DD §2) | Fase mutasi (assign/status, Sprint-02) |
| D — Denial of Service | Pertumbuhan data tak terkendali (audit/outbox/case) | Belum ada purging/retention terimplementasi | Retensi baru berupa baseline dokumen (CMP-002), job purging belum ada | Fase berikut per `../17 Compliance/ECMP_Data_Retention_Policy_v0.1.md` |

### 2.3 Transactional Outbox
| STRIDE | Ancaman | Kontrol existing | Residual risk | Gate penutupan |
|---|---|---|---|---|
| T — Tampering | Event palsu/dimodifikasi sebelum publish | Outbox ditulis dalam transaksi yang sama dengan data bisnis (ADR-009) — konsistensi event ↔ state terjaga | Publisher/broker belum ada; integritas saat publikasi belum diuji | Saat broker diaktifkan (ADR-009 revisit) |
| I — Information Disclosure | Payload event memuat PII dibaca pihak tak berhak | `/_dev/events` (satu-satunya jalur baca outbox via API) mati default + auth + `cases:read` | Klasifikasi PII per payload event belum direview Compliance (DD Open Items) | Review Compliance klasifikasi PII |
| R — Repudiation | Event hilang tanpa jejak | `published_at` null = belum published; index `(published_at, created_at)` untuk polling terurut | Monitoring lag publish belum ada (broker belum ada) | Saat broker diaktifkan |

### 2.4 AuthN Static Dev-Token (ADR-007 fase slice)
| STRIDE | Ancaman | Kontrol existing | Residual risk | Gate penutupan |
|---|---|---|---|---|
| S — Spoofing | Token bocor dipakai pihak lain | Token dari environment (`ECMP_DEV_TOKEN` / `ECMP_DEV_READONLY_TOKEN`), tidak hardcoded di source; `.env` git-ignored, `.env.example` tanpa secret nyata | Tanpa expiry, tanpa revocation, tanpa issuer — token bocor = akses penuh principal terkait (**L-1**) | Shared UAT: JWT/OIDC (ADR-007 fase target) |
| R — Repudiation | Semua aksi teratribusi ke principal tetap (`cs.agent.1` / `viewer.1`) | Batasan tercatat eksplisit (**L-2**) — bukan diperlakukan sebagai "auth selesai" | Tidak ada identitas individual | Shared UAT: user store / IdP claims |
| E — Elevation of Privilege | Token readonly dipakai untuk write | Pemisahan token per principal; `viewer.1` hanya `cases:read` → `cases:create` ditolak 403 | — (kontrol berfungsi di slice, diverifikasi pytest CI) | — |

### 2.5 Integrasi Customer Master (INT-001)
| STRIDE | Ancaman | Kontrol existing | Residual risk | Gate penutupan |
|---|---|---|---|---|
| S — Spoofing | `customerId` fiktif diterima | By design mode stub: `customerId` non-empty apa pun diterima, tetapi selalu `customerVerified=false` — case tak pernah diklaim terverifikasi; stub dilarang mengarang data pelanggan (INT-001) | Case dapat dibuat untuk pelanggan yang tidak ada (diterima untuk Sprint-01) | Real mode INT-001 (menunggu akses sistem eksternal) |
| T — Tampering | Write-back ke Customer Master | Tidak ada jalur write sama sekali — read-only by design (ADR-002/BR-CRM-01) | — | — |
| I — Information Disclosure | Cache PII melebihi kebutuhan | ECMP bukan SoR pelanggan (ADR-002); kredensial read-only; tidak menyimpan PII melebihi kebutuhan cache (INT-001) | Kebijakan TTL cache / masking rule detail menyusul bersama API-010 | FRD-003 + revisi SEC-RAM-001 |
| D — Denial of Service | Customer Master lambat/down memblokir create | Real mode: timeout 3s + fallback ke perilaku stub (availability > verification, FRD-001 §8) | Perilaku fallback belum teruji terhadap sistem nyata | Real mode INT-001 |

### 2.6 CI GitHub Actions
| STRIDE | Ancaman | Kontrol existing | Residual risk | Gate penutupan |
|---|---|---|---|---|
| S/T — Spoofing/Tampering | Kode berbahaya masuk via merge | CI backend wajib hijau (lint + OpenAPI validate + migrate + pytest coverage ≥90%) sebelum merge (`backend-ci.yml`); kontrak dulu — endpoint tanpa OpenAPI dilarang; dependency audit via job `pip-audit` | SAST (CodeQL/bandit) dan secret scanning belum ada di pipeline | Backlog Secure SDLC (Security Standards §6) |
| I — Information Disclosure | Secret bocor di log/artifact CI | Secrets via GitHub Actions secrets/env — tidak pernah ditulis ke file repo (Security Standards §7) | Vault/secret manager PROD belum dipilih (**L-5**) | PROD: vault/CI secret store (`14 Deployment Standards`) |

## 3. Abuse Cases
| # | Abuse case | Penilaian slice | Mitigasi / catatan |
|---|---|---|---|
| A-1 | **Token bocor** — `ECMP_DEV_TOKEN` tersebar (salah commit, screen-share, log) | Dampak: akses penuh CS Agent tanpa expiry/revocation (L-1) | Diterima hanya untuk DEV lokal + CI; dilarang untuk shared UAT/PROD (ADR-007). Rotasi = ganti nilai env. Gate: JWT/OIDC |
| A-2 | **Mass create** — flood `POST /v1/cases` memenuhi DB (cases + audit_log + outbox tumbuh 3x per request) | Tidak ada rate limiting/quota di slice | Backlog sebelum shared UAT: rate limiting; retensi/purging per CMP-002 mengurangi dampak jangka panjang |
| A-3 | **Enumeration caseId** — iterasi `GET /v1/cases/{caseId}` untuk memanen data case | Format `CASE-<10-hex>` **non-sekuensial** (random hex) → enumeration brute-force tidak praktis (ruang 16^10); 404 tanpa membocorkan keberadaan pola ID | Residual: token sah dapat membaca semua case (tanpa org-scoping, L-3). Gate: G1 `orgUnitId` |

## 4. Pentest Plan (backlog)
Status: **Planned — belum dijadwalkan.** Trigger wajib: **sebelum shared UAT**, bersamaan dengan aktivasi fase target ADR-007 (JWT/OIDC), karena pentest terhadap dev-token statis tidak merepresentasikan permukaan serangan target.

Lingkup minimum saat dijalankan:
1. AuthN/AuthZ: bypass token, semantik 401/403, eskalasi permission antar-role.
2. Injection & input handling pada `POST /v1/cases` (payload, boundary 5000 char).
3. Enumeration & information disclosure (`caseId`, error envelope, header).
4. Verifikasi `/_dev/*` tidak aktif di environment bersama.
5. Integritas audit trail (upaya modifikasi/penghapusan `audit_log`).

Hasil dan remediation dicatat di register ini (revisi berikut) dan `../17 Compliance/ECMP_Compliance_Control_Matrix_v0.1.md`.

## Related
- `ECMP_AuthN_Limitations_Register_v0.1.md` (L-1..L-5)
- `ECMP_Security_Standards_v0.1.md`, `ECMP_Role_Access_Matrix_v0.1.md`
- ADR-002, ADR-007, ADR-008, ADR-009
- `../09 Integration Catalog/ECMP_INT_001_Customer_Master_Read_v0.1.md`
- `../17 Compliance/ECMP_Compliance_Control_Matrix_v0.1.md`, `../17 Compliance/ECMP_Data_Retention_Policy_v0.1.md`
