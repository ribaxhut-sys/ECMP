# ECMP Runbook — Fase Slice (Sprint-01)

| Field | Value |
|---|---|
| ID | OPS-RB-001 |
| Version | 0.1 |
| Owner | Operations Lead |
| Reviewer | DevOps / Tech Lead Backend |
| Approver | Operations Lead |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

Runbook jujur untuk scope slice: environment nyata hanya **DEV lokal + CI** (DEP-001, ADR-010). Prosedur yang membutuhkan shared environment ditandai **Planned** dan baru berlaku saat baseline SIT/UAT ADR-010 aktif.

## 1. Service Inventory & Ownership

| Service | Deskripsi | Cara jalan (DEV) | Owner | Backup/Eskalasi |
|---|---|---|---|---|
| ecmp-case-service | Backend FastAPI slice create/get (FR-001/FR-002) | `uvicorn app.main:app` dari `implementation/backend` | Backend Lead (per OWNERSHIP_MATRIX folder 07) | Tech Lead / Solution Architect |
| Developer Portal | Portal internal RAG/coverage/impact (IMP-PORTAL-001) — bukan frontend produk (ADR-011) | `uvicorn app:app --port 8030` dari `implementation/portal` | Engineering Manager / EA | Tech Lead |
| PostgreSQL 16 | Database DEV via `implementation/infrastructure/docker-compose.yml` (container `ecmp-postgres`) | `docker compose -f implementation/infrastructure/docker-compose.yml up -d` | DevOps Lead (per OWNERSHIP_MATRIX folder 14) | SRE / Operations |

## 2. Health Check

- Endpoint: `GET /health` di root (tanpa prefix `/v1` — operasional, TS-001 §2), tanpa autentikasi.
- Expected response: `{"status": "ok", ...}` — field `status` bernilai `"ok"` adalah kriteria sehat; field lain (`service`, `sprint`) informasional.
- DEV: `curl http://127.0.0.1:8000/health`. Portal: `curl http://127.0.0.1:8030/` (halaman portal termuat).
- Planned (SIT/UAT per ADR-010): health check yang sama dipakai probe container/monitor uptime.

## 3. Playbooks

### P1 — Service tidak start / crash saat boot
1. **Symptom:** `uvicorn` exit saat start, atau proses mati segera setelah request pertama.
2. **Impact:** API create/get case tidak tersedia (DEV: developer terblokir; Planned SIT/UAT: pengguna uji terblokir).
3. **Detection:** `GET /health` gagal/connection refused; traceback di terminal uvicorn.
4. **Diagnosis steps:**
   - Cek env vars: `ECMP_DATABASE_URL` (default SQLite lokal; DEV Postgres perlu di-set), `ECMP_DEV_TOKEN`, `ECMP_ENABLE_DEV_ENDPOINTS` — template di `implementation/backend/.env.example`.
   - Cek dependensi terpasang: `pip install -r requirements.txt` di `implementation/backend`.
   - Cek skema: `alembic upgrade head` sudah dijalankan? Traceback "relation/table does not exist" = migrasi belum jalan.
   - Cek DB hidup (lihat P2) bila `ECMP_DATABASE_URL` menunjuk PostgreSQL.
5. **Mitigation / workaround:** untuk pekerjaan lokal non-DB-spesifik, fallback SQLite (unset `ECMP_DATABASE_URL`) diperbolehkan sementara (ADR-010 butir 1) — PostgreSQL tetap wasit paritas.
6. **Resolution:** perbaiki env var/dependensi, jalankan `alembic upgrade head`, start ulang uvicorn, verifikasi `GET /health`.
7. **Escalation:** L1 → L2 Backend Lead bila traceback berasal dari kode aplikasi (bukan konfigurasi).
8. **Post-incident actions:** bila penyebabnya konfigurasi yang tidak terdokumentasi, update `.env.example` + runbook ini.

### P2 — Database down / connection refused
1. **Symptom:** aplikasi error `connection refused` / `could not connect to server` ke PostgreSQL.
2. **Impact:** semua operasi tulis/baca case gagal (500); DEV terblokir.
3. **Detection:** traceback SQLAlchemy/psycopg di log aplikasi; `GET /health` bisa tetap ok (health belum cek DB — known limitation).
4. **Diagnosis steps:**
   - `docker compose -f implementation/infrastructure/docker-compose.yml ps` — container `ecmp-postgres` running & healthy?
   - `docker logs ecmp-postgres` — error start (mis. port 5432 bentrok, volume korup)?
   - Cek `ECMP_DATABASE_URL` menunjuk host/port/credential yang benar (`ecmp@localhost:5432/ecmp` di DEV).
5. **Mitigation / workaround:** restart container: `docker compose ... up -d`. Port bentrok → hentikan proses lain di 5432 atau ubah mapping lokal.
6. **Resolution:** container healthy (healthcheck `pg_isready` hijau), aplikasi bisa query. Volume `ecmp_pgdata` korup di DEV → boleh di-recreate (data DEV tidak di-backup — OPS-DR-001); **Planned SIT/UAT:** restore dari backup, JANGAN recreate volume begitu saja.
7. **Escalation:** L1 → L2 DevOps Lead bila masalah pada Docker/host, L2 Backend Lead bila connection string/driver.
8. **Post-incident actions:** catat penyebab; bila berulang di shared env (Planned), pertimbangkan alerting DB di review ADR-010.

### P3 — Outbox backlog menumpuk
1. **Symptom:** baris `outbox` dengan `published_at IS NULL` menua terus (tidak pernah terpublikasi).
2. **Impact:** event `CaseCreated` (EVT-001) tidak sampai ke consumer. **Catatan konteks:** per ADR-009 broker/publisher lintas-service memang **belum ada** — backlog `published_at NULL` adalah kondisi normal fase slice, BUKAN insiden, selama belum ada consumer nyata.
3. **Detection:** query contoh:

```sql
SELECT count(*), min(created_at)
FROM outbox
WHERE published_at IS NULL;
```

   Backlog baru menjadi insiden bila publisher/relay sudah aktif (pasca trigger ADR-009) dan `min(created_at)` menua melebihi interval publish yang disepakati.
4. **Diagnosis steps:** cek apakah publisher/relay berjalan (pasca ADR-009); cek error publisher di log; cek broker (bila sudah ada) menerima koneksi.
5. **Mitigation / workaround:** fase slice — tidak ada aksi (by design). Pasca broker: restart publisher; jangan menghapus baris outbox.
6. **Resolution:** backlog terkuras (`published_at` terisi) setelah publisher pulih.
7. **Escalation:** L2 Backend Lead (pemilik pola outbox); keputusan skema/relay → L3 Solution Architect.
8. **Post-incident actions:** bila backlog karena payload invalid, tambahkan tes relay (backlog TST-001 §6 — outbox relay test).

### P4 — Migrasi Alembic gagal
1. **Symptom:** `alembic upgrade head` error (lokal, CI step "Run migrations", atau deploy Planned SIT/UAT).
2. **Impact:** skema DB tidak sinkron dengan kode; deploy/CI terblokir.
3. **Detection:** exit code non-zero pada perintah alembic; CI merah di step migrasi.
4. **Diagnosis steps:**
   - Baca error: konflik revision (multiple heads), DDL gagal, atau koneksi DB (→ P2).
   - `alembic current` dan `alembic history` untuk melihat posisi revision.
   - Cek apakah revision baru menyentuh `audit_log` — revision seperti ini wajib review ekstra ketat (DEP-001 §4) karena `audit_log` append-only (BR-CP-03/BR-008) tidak boleh hilang.
5. **Mitigation / workaround:** rollback per Deployment Standards §4: turunkan aplikasi ke versi kompatibel dulu, lalu `alembic downgrade <rev>` bila dibutuhkan. Downgrade yang menghapus data (drop kolom/tabel berisi data) memerlukan keputusan eksplisit — tidak otomatis.
6. **Resolution:** revision diperbaiki (setiap revision wajib punya `downgrade()` berfungsi — DEP-001 §4), `alembic upgrade head` hijau di CI.
7. **Escalation:** L2 Backend Lead; revision menyentuh `audit_log` atau butuh keputusan hapus data → L3 Solution Architect.
8. **Post-incident actions:** tambahkan kasus gagal ke review checklist migrasi bila polanya baru.

### P5 — SLA breach response (operasional) — baseline
1. **Symptom:** case melewati ambang SLA — target numerik baseline per `../11 SLA and KPI Matrix/ECMP_SLA_Matrix_v0.1.md` (SLA-MTX-001, ditutup via DEC-005; warning 80%, breach = melewati due).
2. **Impact:** komitmen layanan ke pelanggan terlanggar; risiko eskalasi bisnis.
3. **Detection:** **Planned** — deteksi otomatis menunggu event SLA breach (EVT-004) yang belum diimplementasikan; fase sekarang deteksi manual (query/laporan supervisor).
4. **Diagnosis steps:** identifikasi case terdampak (`caseId`, prioritas, unit); verifikasi jam SLA — baseline kalender **24x7** (BR-ECMF-05, DEC-004).
5. **Mitigation / workaround:** prioritaskan penanganan case terdampak oleh unit pemilik.
6. **Resolution:** case ditangani; breach dicatat untuk pelaporan KPI.
7. **Escalation:** ke **supervisor** unit terkait — baseline BR-NOTIF-04 (DEC-004: eskalasi email ke supervisor). **Planned:** eskalasi otomatis saat Notification domain dibangun.
8. **Post-incident actions:** review penyebab breach; masukan untuk penetapan target numerik SLA (workshop Business Owner — folder 11).

### P6 — Notification failure handling — Planned
1. **Symptom:** notifikasi (email/kanal lain) gagal terkirim.
2. **Impact:** stakeholder tidak menerima informasi case/SLA.
3. **Detection / Diagnosis / Mitigation / Resolution:** **Planned** — domain Notification **belum dibangun** (non-goal DEC-002; menunggu sprint domain Notification). Baseline perilaku yang akan diimplementasikan: retry maksimal **3x interval 5 menit**, setelah max retry eskalasi via **email ke supervisor** (BR-NOTIF-04, DEC-004).
7. **Escalation:** saat domain dibangun: L2 Backend Lead; kebijakan retry berubah → DEC baru (kewenangan BO per DEC-004).
8. **Post-incident actions:** lengkapi playbook ini menjadi prosedur penuh saat implementasi Notification dimulai.

## 4. Escalation Matrix

| Level | Peran | Kapan |
|---|---|---|
| L1 | Support / on-duty operations | Triage awal semua insiden; jalankan playbook |
| L2 | Backend Lead (aplikasi/DB logic) atau DevOps Lead (infra/Docker/CI) | Playbook tidak menyelesaikan; akar masalah di kode/infra |
| L3 | Solution Architect / Operations Lead | Dampak arsitektur (skema, audit_log, keputusan hapus data), insiden lintas tim, keputusan darurat |

## 5. Berlaku sekarang vs Planned

| Item | Status |
|---|---|
| P1, P2, P4 (DEV/CI) | Berlaku sekarang |
| P3 | Berlaku sebagai monitoring; menjadi insiden nyata pasca trigger ADR-009 |
| P5 | Baseline manual berlaku; deteksi otomatis Planned (EVT-004) |
| P6 | Planned (domain belum dibangun) |
| Prosedur shared env (probe, restore, alerting) | Planned — aktif bersama baseline SIT/UAT ADR-010 |

## Related
- `../14 Deployment Standards/ECMP_Deployment_Standards_v0.1.md` (DEP-001)
- `../05 Architecture Decision Records/ECMP_ADR_009_Message_Broker_Deferral_v1.0.md`, `ECMP_ADR_010_Deployment_Platform_Baseline_v1.0.md`
- `./ECMP_DR_BCP_Plan_v0.1.md` (OPS-DR-001)
- `../11 SLA and KPI Matrix/`
