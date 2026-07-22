# Decision Record — G1 Contract Freeze (Sprint-02A)

| Field | Value |
|---|---|
| ID | DEC-006 |
| Version | 1.0 |
| Owner | Lead Software Architect |
| Reviewer | ECMF PO / Tech Lead / QA Lead / Security Officer |
| Approver | Solution Architect |
| Status | 🟢 Accepted (contract freeze) |
| Last Review | 2026-07-21 |
| Next Review | 2026-10-21 |

- Type: Project Decision (non-ADR) — contract-level semantics; no architecture deviation (ADR tidak diperlukan)
- Date: 2026-07-21
- Scope: Sprint-02A — freeze seluruh kontrak prasyarat implementasi Sprint-02B (entry gate G1, Test Strategy §3; task G1-S1 roadmap)

## Context

Entry G1 mensyaratkan kontrak API-003/API-004 dan payload EVT-002/EVT-003 **merged sebelum kode**, plus matriks transisi disepakati (sudah: DOM-ECMF-003 Approved). Review kontrak menemukan lima inkonsistensi terbuka yang harus diputuskan sebelum freeze. Sprint-02A adalah fase kontrak; Sprint-02B adalah fase implementasi.

## Review Findings & Frozen Decisions

### D1 — HTTP 400 vs 409 untuk transisi/state ilegal → **409**
- Konflik: draft `case-actions.v1.draft.yaml` mengusulkan 409; AC FRD-002 §6 menulis 400.
- **Putusan: 409** — transisi ilegal adalah **konflik state resource** (request secara sintaksis valid), bukan kesalahan payload. 400 tetap khusus `VALIDATION_ERROR` (payload salah bentuk/enum). Konsisten dengan semantik HTTP dan memudahkan client membedakan "perbaiki request" (400) vs "muat ulang state case" (409).
- Berlaku untuk: API-004 transisi ilegal, dan API-003 saat case tidak berada di status assignable.

### D2 — `cases:status` vs `cases:transition` → **`cases:status`**
- Konflik: SEC-RAM-001 memakai `cases:status`; TC-004 dan FRD-002 §7 menyebut kandidat `cases:transition`.
- **Putusan: `cases:status`** — konsisten dengan pola penamaan permission mengikuti endpoint (`POST /v1/cases/{caseId}/status`), selaras `cases:create`/`cases:read`/`cases:assign`. Alias `cases:transition` dihapus dari semua dokumen delivery.

### D3 — Penamaan permission (keseluruhan) → pola `cases:<action>` dikunci
- Beku: `cases:create`, `cases:read` (implemented); `cases:assign` (Supervisor), `cases:status` (Handler) — definisi final di SEC-RAM-001 v0.3, enforcement menyusul di Sprint-02B.

### D4 — Event payload → EVT-002/EVT-003 dibekukan; `resolutionCode` ditambahkan ke request API-004
- EVT-002 `{caseId, assigneeId, unitId, assignedBy, previousAssigneeId?, assignedAt}` dan EVT-003 `{caseId, fromStatus, toStatus, changedBy, changedAt, reason?}` **frozen** — anotasi freeze + `fr`/`api` ditambahkan di `events.yaml`; perubahan payload selanjutnya butuh keputusan freeze baru.
- Gap yang ditemukan review: transisi →CLOSED wajib Resolution (BR-ECMF-06, guard DOM-ECMF-003) dan payload EVT-005 memuat `resolutionCode`, tetapi draft `StatusChangeRequest` tidak punya field pembawanya. **Putusan:** tambah `resolutionCode` (nullable; MANDATORY untuk →CLOSED) di `StatusChangeRequest` — menyelaraskan API-004 dengan EVT-005 dan BR-ECMF-06.
- Klarifikasi `reason` di EVT-003: mandatory untuk override Administrator **dan** CLOSED→REOPENED (BR-ECMF-07), selaras DOM-ECMF-003.

### D5 — Error codes → vocabulary dikunci
| Kondisi | HTTP | `code` |
|---|---|---|
| Payload invalid (enum/field/boundary; resolutionCode/reason hilang saat wajib) | 400 | `VALIDATION_ERROR` |
| Token hilang/salah | 401 | `UNAUTHENTICATED` |
| Tanpa permission / guard per-transisi gagal (termasuk lintas unit non-supervisor) | 403 | `FORBIDDEN` |
| Case tidak ditemukan | 404 | `NOT_FOUND` |
| Status tidak assignable (API-003) | 409 | `INVALID_STATE` |
| Transisi tidak ada di workflow config aktif (API-004) | 409 | `INVALID_TRANSITION` |
| Error tak terduga | 500 | `INTERNAL_ERROR` |

Dua kode 409 dibedakan sengaja: `INVALID_STATE` = aksi tidak berlaku untuk state sekarang; `INVALID_TRANSITION` = pasangan from→to ditolak config. Response 500 ditambahkan ke endpoint baru untuk konsistensi dengan API-001/002.

### D6 — Merge kontrak → **spec normatif terpisah `case-actions.v1.yaml` v1.0.0** (opsi "spec terpisah" roadmap G1-S1)
Awalnya dicoba merge langsung ke `case-service.v1.yaml` v1.4.0, tetapi **conformance suite Sprint-01** (`tests/test_contract_conformance.py`: catalog == runtime — operasi, response codes, enum, field `Case`) langsung gagal 4 tes karena mendeklarasikan endpoint/enum yang belum ada di runtime — diverifikasi dengan menjalankan suite. Karena Sprint-02A **dilarang menyentuh kode backend**, keputusan: kontrak beku hidup sebagai **spec normatif terpisah** (`x-status` normatif, bukan draft; tervalidasi CI). Konsekuensi terencana untuk Sprint-02B: saat endpoint diimplementasikan, spec ini dikonsolidasikan ke `case-service.v1.yaml` (planned v1.4.0) dan conformance suite diperluas membaca kedua spec (lihat U-6). Enum `CaseStatus` penuh + `Case.assigneeId/unitId` terdefinisi di case-actions; case-service tetap jujur terhadap runtime Sprint-01. File draft dihapus (dikonsumsi oleh freeze).

## Changed Documents (semua dalam perubahan ini)
1. `07 API Catalog/openapi/case-actions.v1.yaml` — **BARU, normatif v1.0.0** (contract frozen): API-003, API-004, AssignRequest, StatusChangeRequest (+resolutionCode), CaseStatus enum penuh, Case.assigneeId/unitId, error 409/500; `case-service.v1.yaml` tidak berubah (tetap v1.3.0, jujur terhadap runtime — lihat D6)
2. `07 API Catalog/openapi/drafts/case-actions.v1.draft.yaml` — **dihapus** (dikonsumsi freeze)
3. `07 API Catalog/README.md` — API-003/004 pindah ke inventory utama, status "Contract frozen G1 (DEC-006)"
4. `07 API Catalog/API_CATALOG.generated.md` — regenerated
5. `08 Event Catalog/events/events.yaml` — EVT-002/EVT-003: anotasi FROZEN + `fr`/`api`; klarifikasi `reason`
6. `08 Event Catalog/EVENT_CATALOG.generated.md` — regenerated
7. `10 Security and Access Standards/ECMP_Role_Access_Matrix_v0.1.md` — v0.2 → **v0.3**: nama permission final (D2/D3), caveat penamaan ditutup
8. `03 Functional Requirements/ECMP_FRD_ECMF_Lifecycle_v0.1.md` (FRD-002) — v0.1 → **v0.2**: AC 400→409 + error code, skenario 409 assign, dependensi `cases:status`, banner freeze
9. `13 Test Strategy/ECMP_Test_Case_Catalog_v0.1.md` — TC-003/TC-004: catatan freeze, referensi spec normatif, expected 409, permission final
10. `26 Traceability/traceability.yaml` — v0.6 → **v0.7**: anotasi freeze (link TRC-L-003/004 tidak berubah struktural)
11. `26 Traceability/TRACEABILITY_MATRIX.md` — regenerated (sync)
12. `27 Project Decisions/DEC-006_...` — dokumen ini

## Unresolved Issues (tidak menahan freeze; ditugaskan)
| # | Isu | Pemilik | Target |
|---|---|---|---|
| U-1 | **Subset transisi Sprint-02B**: Sprint-02.md menyebut "configured subset" — konfirmasi PO apakah CLOSED→REOPENED (dan emisi EVT-005/EVT-007 pada closure/reopen) masuk Sprint-02B atau menunggu. Kontrak sudah superset (configuration-first, ADR-003) — keputusan ini isi workflow config, bukan perubahan kontrak | ECMF PO | Planning Sprint-02B |
| U-2 | **Keputusan L-3 (org-unit scoping)**: mekanisme enforcement BR-002 lintas unit dengan principal slice (mis. `orgUnitId` di fixture principal dev) — prasyarat guard 403 lintas unit TC-003 | Security Architect + Tech Lead | Sebelum S2-1 dimulai |
| U-3 | **Evidence untuk COMPLAINT closure** (BR-ECMF-06 baseline DEC-004): di luar scope Sprint-02 (hanya `resolutionCode`); mekanisme evidence menunggu FRD revisi | BA / ECMF PO | FRD-002 revisi berikut |
| U-4 | **EVT-007 masih Proposed** di katalog — harus di-approve sebelum reopen flow diimplementasikan (terkait U-1) | Integration Lead | Bersamaan U-1 |
| U-5 | **DoR FRD-002 + sign-off G0** — freeze kontrak ini memenuhi prasyarat teknis; tanda tangan manusia (BO untuk DoR; Tech Lead + SA untuk G0 exit) tetap wajib per DEC-002 | BO / Tech Lead / SA | Sebelum kode Sprint-02B |
| U-6 | **Konsolidasi spec + perluasan conformance suite** (konsekuensi D6): merge case-actions → case-service v1.4.0 dan extend `test_contract_conformance.py` untuk membaca kedua spec — dikerjakan bersama implementasi endpoint | Tech Lead | Sprint-02B (S2-1/S2-2) |

## Declaration
**Entry gate G1 terpenuhi secara kontrak**: API-003/API-004 normatif (merged), payload EVT-002/EVT-003 beku, matriks transisi disepakati (DOM-ECMF-003), permission final, error semantics terkunci, seluruh dokumen turunan selaras.

**Sprint-02B implementation MAY START** setelah dua tanda tangan yang tersisa (U-5): (a) sign-off G0 exit oleh Tech Lead + Solution Architect (DEC-002), (b) DoR FRD-002 v0.2 oleh Business Owner. Tidak ada blocker kontrak yang tersisa; U-1..U-4 dikerjakan paralel tanpa mengubah kontrak beku.

## Addendum — Sprint-03A (2026-07-22, governance sync)
U-6 resolved: `case-actions.v1.yaml` merged into `case-service.v1.yaml` v1.4.0;
`test_contract_conformance.py` now reads the single consolidated spec (not "kedua
spec" as U-6 originally described — one spec was sufficient once merged).
`case-actions.v1.yaml` kept on disk as an `x-status: superseded` stub (not deleted)
rather than removed, per repository file-retention constraint; it carries no
normative content. No contract or payload change — see `implementation/backend/ACR_SPRINT02B.md`
ACR-001/ACR-003 for the resolution record and Sprint-03A test evidence.
U-5 (human sign-off) remains open; not addressed by this addendum.

## Links
- Test Strategy §3 (entry/exit G1), `ai/sprint/IMPLEMENTATION_ROADMAP_v0.1.md` G1-S1
- DEC-002 (build authorization), DOM-ECMF-003 (state machine), ADR-003/006/008/009
