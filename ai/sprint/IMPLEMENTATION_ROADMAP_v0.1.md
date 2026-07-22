# ECMP Implementation Roadmap — Sprint-02 → Sprint-03 → SIT/UAT

| Field | Value |
|---|---|
| ID | AI-SPRINT-RM-001 |
| Version | 0.1 |
| Owner | PMO / Eng Manager |
| Reviewer | Solution Architect / Tech Lead / Domain POs |
| Approver | Business Owner |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2026-08-21 |

> Roadmap maju (forward-looking) berbasis artefak yang sudah Approved: `26 Traceability/traceability.yaml` v0.6,
> gate model DEC-002 + `13 Test Strategy` §3, sprint brief `Sprint-02.md` (governing), draft kontrak di
> `07 API Catalog/openapi/drafts/`, dan trigger ADR-007/009/010/011. Tidak ada scope baru yang diciptakan
> di dokumen ini. Estimasi kompleksitas = T-shirt size (S ≈ 1–2 hari-dev, M ≈ 3–5, L ≈ 6–10, XL = perlu breakdown).
> Urutan memakai gate, bukan tanggal kalender (kapasitas tim belum ditetapkan).

## 1. Posisi Saat Ini (baseline)

- **Sprint-01 (B1) — SELESAI**: slice create/get (FR-001/001c/002) live di backend; G0 exit terpenuhi
  (CI hijau, TC-001/002/005 implemented, envelope terverifikasi, coverage gate 90%).
- **Siap pakai untuk sprint berikut**: draft OpenAPI API-003/004/005/010/040 (tervalidasi), payload EVT-002/003
  di `events.yaml`, transition matrix di `20 Domain Architecture/ECMF/CASE_STATE_MACHINE.md`, baseline
  SLA/NFR (DEC-005), drainer outbox in-process DEV (ADR-009 §2).

## 2. Sprint Breakdown

| Fase | Isi | FR | Prasyarat masuk |
|---|---|---|---|
| **G1** (gate, tanpa kode fitur) | Freeze kontrak lifecycle: merge draft API-003/004 jadi normatif, sepakati matriks transisi + keputusan 400-vs-409, definisikan permission baru | — | Sprint-01 selesai (✅) |
| **Sprint-02 (B2)** | Assign/reassign, status transition, emisi EVT-002/003, Customer 360 read, Notification stub | FR-003, FR-004, FR-010, FR-020 | G1 exit |
| **G2** (mini-gate) | Keputusan broker (revisit ADR-009), mode real Customer Master (INT-001A → INT-001 v0.2), aktivasi observability TS-OBS-001, quality bar | — | Sprint-02 exit |
| **Sprint-03 (B3)** | SLA breach engine (KPI), dashboard queue + list API berpaginasi | FR-030, FR-040 | G2 exit |
| **Jalur platform (paralel, non-fitur)** | JWT/OIDC fase target (ADR-007), provisioning SIT/UAT (ADR-010), perf test vs NFR, pentest, eksekusi UAT | — | Lihat §6 |
| **Ditunda dengan trigger** | Frontend produk (ADR-011), broker fisik (ADR-009) | — | Trigger di ADR masing-masing |

## 3. Epics

| Epic | Nama | Domain | FR/Artefak | Sprint |
|---|---|---|---|---|
| E-01 | ECMF Lifecycle (assign + status) | ECMF | FR-003/004, API-003/004, EVT-002/003, TC-003/004 | Sprint-02 |
| E-02 | Customer 360 Read | CRM | FR-010, API-010, INT-001, TC-010 | Sprint-02 |
| E-03 | Notification Stub | Notification | FR-020, konsumsi EVT-001/002, TC-020 | Sprint-02 |
| E-04 | Eventing Backbone | Core Platform | Relay outbox → keputusan broker (ADR-009), status per-event `events.yaml` | G2 → Sprint-03 |
| E-05 | KPI / SLA Engine | KPI | FR-030, EVT-004, konfigurasi SLA per DEC-005, TC-030 | Sprint-03 |
| E-06 | Dashboard & Case List | Dashboard | FR-040, API-040 + API-005, TC-040 | Sprint-03 |
| E-07 | Platform & Security Hardening | Core Platform | ADR-007 fase target, ADR-010 SIT/UAT, TS-OBS-001, secrets | Paralel |
| E-08 | Quality, Ops & UAT | QA/Ops | Perf test (NFR-001), pentest (Threat Model §backlog), UAT (UAT-001), aktivasi runbook/DR | Paralel/akhir |

## 4. Stories, Tasks, Dependensi, Kompleksitas

Format: **Story** → tasks. `Dep:` = dependensi. Kompleksitas dalam kurung.

### G1 — Lifecycle Contract Gate (docs/keputusan saja)

- **G1-S1. Finalisasi kontrak assign/status (M)** — Owner: SA + ECMF PO
  - Review draft `case-actions.v1.draft.yaml`; **putuskan 400 vs 409** untuk transisi ilegal (flag terbuka di draft vs FRD-002) → update FRD-002 atau draft, satu PR kontrak.
  - Merge draft → `case-service` v1.4.0 (atau spec terpisah) sebagai normatif; regen API catalog.
  - Definisikan permission `cases:assign`, `cases:status` di Role Access Matrix (aktifkan baris "Planned — Sprint-02").
  - Freeze langkah TC-003/TC-004 di Test Case Catalog.
  - Dep: — (semua bahan sudah ada). **Exit G1**: kontrak merged sebelum kode (Test Strategy §3).

### E-01 — ECMF Lifecycle (Sprint-02)

- **S2-1. Assign/reassign case — FR-003 (L)**
  - Model: kolom `assignee_id`, `unit_id` + migrasi Alembic (revisi 0002).
  - Service `assign_case`: guard BR-002 (supervisor unit induk; unit lain read-only), audit `case.assign` + outbox EVT-002 satu transaksi (pola FR-001c).
  - Route `POST /v1/cases/{caseId}/assign` + permission `cases:assign`; envelope 409/404/403.
  - TC-003 + negatif (unit tak berwenang, case tak ada, state tak valid); update konformansi.
  - Dep: G1-S1.
- **S2-2. Status transition — FR-004 (L)**
  - Implementasi matriks transisi dari CASE_STATE_MACHINE (SoT enum) sebagai tabel data/konfigurasi (ADR-003 configuration-first), bukan hardcode if-else.
  - Service `change_status`: validasi transisi, `reason` wajib untuk override, audit + outbox EVT-003 satu transaksi.
  - Route `POST /v1/cases/{caseId}/status`; perluas enum `CaseStatus` di schemas + OpenAPI (kontrak dari G1).
  - TC-004: transisi ilegal → state tidak berubah (assert DB), authz, audit.
  - Dep: G1-S1. Catatan: S2-1 dan S2-2 bisa paralel setelah migrasi 0002 disepakati bersama.
- **S2-3. Emisi & katalog event — EVT-002/003 (S)**
  - Payload sesuai `events.yaml`; naikkan status event → Implemented; regen event catalog; tes payload-vs-catalog (pola `test_outbox_payload_matches_event_catalog`).
  - Dep: S2-1, S2-2.

### E-02 — Customer 360 Read (Sprint-02)

- **S2-4. Proxy read Customer Master — FR-010 (M)**
  - Merge draft `customer-read.v1.draft.yaml`; service client INT-001 (mode stub, timeout 3s + fallback per INT-001).
  - Masking per Role Access Matrix (`customers:read` masked untuk non-CS).
  - Route `GET /v1/customers/{customerId}`; TC-010 + tes fallback CM down.
  - Dep: G1 (kontrak); **tidak** menunggu mode real CM (stub dulu — keputusan real mode di G2 via INT-001A).

### E-03 — Notification Stub (Sprint-02)

- **S2-5. Konsumer stub CaseAssigned/CaseCreated — FR-020 (M)**
  - Konsumsi dari outbox via drainer in-process (ADR-009 §2) — belum broker; failure logging tanpa silent drop.
  - Kirim ke sink stub (log/tabel `notification_log`), idempoten per event.
  - TC-020 + tes jalur gagal.
  - Dep: S2-3 (EVT-002 mengalir). **Risiko**: jangan bangun framework generik (out of scope DEC-002).

### G2 — Cross-cutting Mini-Gate (dokumen/keputusan)

- **G2-S1. Keputusan broker — revisit ADR-009 (M)** — konsumer lintas-service nyata pertama (KPI Sprint-03) adalah trigger; pilih broker atau perpanjang in-process + relay; ADR baru bila berubah. Dep: S2-5 berjalan.
- **G2-S2. Mode real Customer Master (M)** — jalankan RFI INT-001A dengan tim CM; hasil → INT-001 v0.2; keputusan tetap stub untuk Sprint-03 bila sandbox belum tersedia. Dep: S2-4.
- **G2-S3. Aktivasi observability (S)** — TS-OBS-001: structured JSON logging + `X-Request-ID` di backend (aktivasi G1 per standar); metrik minimum. Dep: —.
- **G2-S4. Regression pack & dev runbook (S)** — matriks authz, negatif transisi, CM fallback, outbox re-drain; runbook developer (compose→migrate→seed→token→drain). Dep: S2-1..S2-5.

### E-04/E-05 — KPI / SLA Engine (Sprint-03)

- **S3-1. Konsumsi event untuk SLA clock (L)** — konsumer EVT-001/003/005/007 (per TRC-L-007) membangun fakta SLA; transport sesuai keputusan G2-S1. Dep: G2-S1.
- **S3-2. Konfigurasi SLA & deteksi breach — FR-030 (L)** — tabel konfigurasi kategori+prioritas dengan baseline DEC-005 (CRITICAL 30m/4j dst., kalender 24x7); scheduler deteksi due/warning 80%; emisi EVT-004 (idempoten caseId+slaId); TC-030. Dep: S3-1; kontrak EVT-004 sudah ada di events.yaml.

### E-06 — Dashboard & Case List (Sprint-03)

- **S3-3. List API berpaginasi — API-005 (M)** — merge bagian `GET /v1/cases` dari draft dashboard-queues; paginasi TS-001 §3 (page/pageSize/PageMeta), filter status/priority/caseType/assigneeId; index DB pendukung. Dep: S2-1/S2-2 (field assignee/status ada).
- **S3-4. Dashboard queues — FR-040 (M)** — `GET /v1/dashboard/queues` scoped role/org (BR-006/BR-DASH-01), read-only; TC-040. Dep: S3-3; konsumsi agregat SLA opsional menunggu S3-2.

### E-07 — Platform & Security (paralel, tidak memblokir B2)

- **P-1. JWT/OIDC fase target — ADR-007 (L)** — pilih IdP, validasi JWT di `auth.py` (ganti static token), klaim `userId`+`permissions`; wajib **sebelum shared UAT**. Dep: keputusan IdP (Business/IT).
- **P-2. Provisioning SIT/UAT — ADR-010 (M)** — compose di VM managed + deploy via GitHub Actions; aktifkan backup pg_dump+WAL per DR/BCP; secrets via vault/Actions secrets. Dep: P-1 selesai **sebelum dibuka untuk UAT** (token statis dilarang di shared env).
- **P-3. Hubungkan remote git + aktifkan CI nyata (S)** — push ke GitHub/GitLab; verifikasi ketiga workflow jalan; branch protection per CODEOWNERS. Dep: — (bisa hari ini; repo lokal sudah ber-baseline).

### E-08 — Quality, Ops & UAT (setelah SIT/UAT ada)

- **Q-1. Perf smoke vs NFR (M)** — k6/locust terhadap SIT: p95 <300ms read / <800ms write / 10 rps (DEC-005). Dep: P-2.
- **Q-2. Pentest scope slice (M)** — backlog Threat Model §pentest (boundary, authz, injection). Dep: P-1, P-2.
- **Q-3. Eksekusi UAT wave-1 (M)** — per UAT-001: TC-001/002/005 dengan persona P-01..P-05; lalu wave-2 (TC-003/004/010) setelah Sprint-02. Dep: P-1, P-2, FRD terkait Approved.

## 5. Urutan Implementasi (ringkas)

```text
   SEKARANG ──► P-3 (remote git + CI nyata)  [bisa langsung]
      │
      ▼
   G1 (freeze kontrak assign/status, keputusan 400/409, permission)
      │
      ▼
   Sprint-02: [S2-1 Assign ∥ S2-2 Status] ─► S2-3 Events ─► S2-5 Notif stub
              [S2-4 Customer 360 — paralel penuh]
      │                                   (paralel: P-1 JWT dimulai)
      ▼
   G2: G2-S1 broker ∥ G2-S2 CM real ∥ G2-S3 observability ∥ G2-S4 regression pack
      │
      ▼
   Sprint-03: S3-1 konsumsi event ─► S3-2 SLA engine
              S3-3 list API ─► S3-4 dashboard   (paralel dengan S3-1/2)
      │                                   (paralel: P-2 SIT/UAT)
      ▼
   Q-1 perf ∥ Q-2 pentest ─► Q-3 UAT ─► sign-off Business Owner
```

## 6. Critical Path

**G1 → S2-2 (status) → S2-3 (EVT-003) → G2-S1 (broker) → S3-1 → S3-2 (SLA engine) → Q-3 (UAT wave-2/3)**

Alasan: SLA engine (FR-030) adalah konsumen hilir terjauh — butuh event lifecycle lengkap (EVT-003 dari S2-2),
keputusan transport (G2-S1), dan konfigurasi DEC-005; dashboard & UAT penuh bergantung padanya untuk nilai bisnis
BP-005. Jalur samping yang bisa menjadi critical bila terlambat dimulai: **P-1 (JWT)** — satu-satunya pemblokir
keras untuk semua aktivitas shared environment (UAT, pentest, perf); mulai paralel sejak Sprint-02.

Slack terbesar (aman digeser): E-02 Customer 360 (tidak ada hilir kecuali UAT wave-2), S3-4 dashboard
(konsumen akhir), frontend (ditunda ADR-011).

## 7. Ringkasan Kompleksitas

| Fase | Story | Total indikatif |
|---|---|---|
| G1 | 1×M | ± 1 minggu kalender (review + keputusan) |
| Sprint-02 | 2×L + 2×M + 1×S | ± 1 sprint penuh untuk 2–3 dev |
| G2 | 2×M + 2×S | ± 1 minggu, mayoritas non-dev (keputusan/eksternal) |
| Sprint-03 | 2×L + 2×M | ± 1 sprint penuh untuk 2–3 dev |
| Platform (paralel) | 1×L + 1×M + 1×S | JWT = jalur terpanjang; mulai dini |
| Quality/UAT | 3×M | Setelah SIT/UAT tersedia |

## 8. Risiko Utama Terhadap Roadmap

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Keputusan 400-vs-409 tertunda | G1 tidak exit, seluruh Sprint-02 tertahan | Agendakan di review G1 pertama; kedua opsi sudah terdokumentasi di draft |
| IdP/JWT (P-1) tidak dimulai paralel | UAT/pentest/perf semua mundur | Jadikan P-1 komitmen Sprint-02 non-fitur |
| Tim CM tidak responsif (INT-001A) | FR-010 tetap stub; UAT wave-2 sebagian | Keputusan eksplisit di G2: lanjut stub, bukan menunggu |
| Broker dipilih terlalu dini/berat di G2-S1 | Over-engineering (ADR-009 anti-goal) | Default: perpanjang in-process relay bila konsumen masih 1 proses |
| Scope creep notification jadi framework | Membengkakkan Sprint-02 | Batas tegas: stub konsumer + log, per DEC-002 out-of-scope list |
