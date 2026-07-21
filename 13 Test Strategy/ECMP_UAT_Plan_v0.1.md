# ECMP UAT Plan

| Field | Value |
|---|---|
| ID | UAT-001 |
| Version | 0.2 |
| Owner | QA Lead |
| Reviewer | BA / Business Owner delegate |
| Approver | Business Owner |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Rencana User Acceptance Testing (UAT) ECMP. Dokumen ini **jujur ter-gate**: UAT belum bisa dieksekusi hari ini karena environment SIT/UAT dan fase target autentikasi belum aktif — rencana ini mendefinisikan prasyarat, peserta, skenario, dan kriteria agar UAT siap jalan begitu gate terpenuhi.

## 1. Prasyarat (gate — wajib terpenuhi sebelum UAT dimulai)

| # | Prasyarat | Status | Owner | Target | Rujukan |
|---|---|---|---|---|---|
| 1 | Environment SIT/UAT tersedia | ⏳ Belum — baseline platform SIT/UAT sudah diputuskan (ADR-010: compose + VM managed, aktif hanya setelah fase target ADR-007); provisioning belum dilakukan | Solution Architect | Sebelum entry UAT gelombang 1 (aktivasi mengikuti fase target ADR-007) | `14 Deployment Standards`; ADR-010 |
| 2 | Fase target autentikasi aktif (JWT/OIDC) — token statis slice **dilarang** untuk shared UAT | ⏳ Belum — arah sudah diputuskan | Security Lead | Sebelum shared UAT dimulai (prasyarat ADR-007) | ADR-007 (fase target sebelum shared UAT) |
| 3 | Scope UAT ter-baseline: FRD terkait berstatus Approved dan TC-nya Implemented + hijau di CI | Sebagian (FRD-001 Approved; FRD-002/003 Draft) | Business Owner | Gelombang 1: terpenuhi (FRD-001); gelombang 2: gate G1 — sebelum Sprint-02 selesai | `03 Functional Requirements`, `ECMP_Test_Strategy_v0.1.md` §3 |
| 4 | Data uji sintetis disiapkan di environment UAT (dilarang data pelanggan nyata) | ⏳ Menunggu environment | QA Lead | Setelah prasyarat #1 terpenuhi, sebelum entry gelombang 1 | Test Strategy §5 |
| 5 | Mode Customer Master ditetapkan untuk UAT (stub vs sandbox real) | ⏳ Stub tersedia; sandbox = open item INT-001A | Integration Lead | Sebelum gelombang 2 (keputusan bersama closure INT-001A) | INT-001, INT-001A |

## 2. Peserta per Persona
Persona dari `../12 UI UX Spec/ECMP_Personas_And_Journeys_v0.1.md`. **UI deferred** (non-goal DEC-002), sehingga UAT slice dieksekusi **via API** (koleksi request terkurasi, mis. Postman/Bruno) atau portal tipis bila sudah ada — bukan screen-based.

| Persona | Peran di UAT | Skenario yang diuji |
|---|---|---|
| P-01 CS Agent | Peserta utama slice | Create case, get case (TC-001, TC-002); Customer 360 saat Sprint-02 (TC-010) |
| P-02 Supervisor | Peserta Sprint-02 | Assign/reassign (TC-003), monitor hasil transisi |
| P-04 Handler | Peserta Sprint-02 | Transisi status penanganan (TC-004) |
| P-03 Administrator | Observer fase awal | Verifikasi audit trail (TC-005) bersama QA; config-driven flow menyusul |
| P-05 Manager / Executive | Belum dilibatkan | Dashboard/KPI (Sprint-03) — di luar scope UAT v0.1 |
| QA Lead | Fasilitator | Menyiapkan skrip API, mencatat hasil & defect |
| BA | Pendamping | Memetakan hasil ke AC FRD |

## 3. Skenario UAT
Skenario UAT = **subset** dari `ECMP_Test_Case_Catalog_v0.1.md` (TC-CAT-001), dijalankan oleh persona bisnis (bukan pytest) terhadap environment UAT.

### Gelombang 1 — slice Sprint-01 (siap begitu prasyarat §1 terpenuhi)
| Skenario | TC | Persona | Ringkas |
|---|---|---|---|
| UAT-S1 | TC-001 | P-01 | Registrasi complaint via `POST /v1/cases` → 201, status `REGISTERED`; coba juga jalur gagal 400/401/403 |
| UAT-S2 | TC-002 | P-01 | Ambil detail case via `GET /v1/cases/{caseId}` → 200 field lengkap; 404 untuk id salah |
| UAT-S3 | TC-005 | P-03 + QA | Verifikasi audit record `case.create` + outbox EVT-001 tercipta satu transaksi dengan create |

### Gelombang 2 — saat Sprint-02 selesai (TC Implemented per gate G1)
| Skenario | TC | Persona | Ringkas |
|---|---|---|---|
| UAT-S4 | TC-003 | P-02 | Assign case → status `ASSIGNED`, EVT-002 + EVT-003 |
| UAT-S5 | TC-004 | P-04 | Transisi valid diterima; transisi ilegal ditolak 400 tanpa perubahan state |
| UAT-S6 | TC-010 | P-01 + role non-CS | Customer 360 read-only; masking kontak untuk non-CS (BR-CRM-02) |

TC-020/TC-030 (Notification, SLA breach) menyusul di gelombang berikutnya sesuai sprint traceability; tidak dijadwalkan di plan v0.1.

## 4. Entry / Exit Criteria

**Entry criteria (per gelombang)**
1. Seluruh prasyarat §1 terpenuhi untuk gelombang tersebut.
2. Semua TC dalam gelombang berstatus ✅ Implemented di TC-CAT-001 dan hijau di CI (`backend-ci.yml`).
3. Skrip/koleksi API UAT direview BA terhadap AC FRD.
4. Peserta persona terkonfirmasi dan mendapat kredensial UAT (bukan token dev).

**Exit criteria (per gelombang)**
1. 100% skenario gelombang dieksekusi; hasil tercatat (pass/fail + evidence).
2. Tidak ada defect Severity 1/2 yang open (lihat §5).
3. Defect Severity 3/4 open memiliki disposisi tertulis (fix sekarang / defer) yang disetujui Business Owner.
4. Sign-off §6 ditandatangani.

## 5. Defect Triage

| Severity | Definisi | Contoh | Keputusan disposisi oleh |
|---|---|---|---|
| Sev-1 | Fungsi inti gagal total / data korup / keamanan | Create case selalu gagal; audit tidak tercatat | Business Owner + Tech Lead (blokir exit) |
| Sev-2 | Fungsi inti salah perilaku tanpa workaround | Status awal bukan `REGISTERED`; 403 untuk permission yang benar | Business Owner + Tech Lead (blokir exit) |
| Sev-3 | Perilaku salah dengan workaround / kasus tepi | Pesan error kurang jelas; field opsional tidak tersimpan | QA Lead + BA (boleh defer dengan persetujuan Business Owner) |
| Sev-4 | Kosmetik / dokumentasi | Typo pesan, inkonsistensi label | QA Lead (defer default) |

Alur: penemu mencatat defect (skenario, langkah, expected vs actual, evidence) → QA Lead menetapkan severity awal → triage harian bersama BA + Tech Lead → disposisi per tabel di atas. Defect yang mengubah kontrak API/event wajib lewat jalur contract-first (bukan hotfix langsung).

## 6. Sign-off
- **Penandatangan:** Business Owner (approver), didampingi QA Lead (kelengkapan eksekusi) dan BA (kesesuaian AC).
- **Objek sign-off:** per gelombang — daftar skenario + hasil + daftar defect beserta disposisinya.
- Sign-off gelombang 1 menjadi salah satu masukan keputusan rilis (lihat `16 Release Management`).

## Related
- `ECMP_Test_Case_Catalog_v0.1.md` (TC-CAT-001) — sumber skenario
- `ECMP_Test_Strategy_v0.1.md` (TST-001) — gate G0/G1
- `../12 UI UX Spec/ECMP_Personas_And_Journeys_v0.1.md` (UX-001) — persona
- `../05 Architecture Decision Records/ECMP_ADR_007_Authentication_Model_v1.0.md` — prasyarat auth fase target
- `../14 Deployment Standards` — environment; baseline platform SIT/UAT per `../05 Architecture Decision Records/ECMP_ADR_010_Deployment_Platform_Baseline_v1.0.md`
- `../26 Traceability/traceability.yaml` — sprint per TC
