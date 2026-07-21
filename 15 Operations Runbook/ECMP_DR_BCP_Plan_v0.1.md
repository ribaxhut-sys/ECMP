# ECMP Disaster Recovery & Business Continuity Plan

| Field | Value |
|---|---|
| ID | OPS-DR-001 |
| Version | 0.1 |
| Owner | Operations Lead |
| Reviewer | DevOps Lead / Solution Architect |
| Approver | Operations Lead |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

Rencana DR/BCP fase slice. Jujur tentang batas: belum ada shared environment (ADR-010) — sebagian besar mekanisme di bawah **Planned** dan baru aktif bersama baseline SIT/UAT. DEV lokal **tidak di-backup** (data sintetis, disposable).

## 1. Sasaran Pemulihan (baseline)

| Sasaran | Nilai | Catatan |
|---|---|---|
| RTO | **4 jam** | Baseline resmi per `../27 Project Decisions/DEC-005_SLA_NFR_Baseline_Targets_v1.0.md` (selaras NFR-001) |
| RPO | **15 menit** | Baseline resmi per DEC-005 — mensyaratkan WAL archiving saat shared env ada |

Nilai berlaku untuk shared environment (SIT/UAT/PROD per ADR-010); DEV tidak punya RTO/RPO.

## 2. Strategi Backup PostgreSQL

| Mekanisme | Cakupan | Status |
|---|---|---|
| `pg_dump` harian (full logical dump) | Seluruh database `ecmp` | **Planned** — aktif saat shared env ADR-010 ada |
| WAL archiving (continuous) | Point-in-time recovery ≤ 15 menit (RPO) | **Planned** — aktif saat shared env ada |
| DEV lokal (`ecmp_pgdata` volume) | — | **Tidak di-backup** — data sintetis; recreate + `alembic upgrade head` bila korup |

Aturan Planned: dump disimpan di storage terpisah dari VM aplikasi; retensi dan enkripsi ditetapkan saat aktivasi SIT/UAT (review trigger §6).

## 3. Restore Procedure (outline)

1. Deklarasikan insiden; hentikan aplikasi (cegah write ke DB inkonsisten).
2. Provision/verifikasi instance PostgreSQL 16 target.
3. Restore: dump terakhir (`pg_restore`/`psql`) + replay WAL sampai titik terdekat sebelum insiden (bila WAL archiving aktif).
4. **Verifikasi `audit_log`** — lihat §5 sebelum membuka layanan.
5. Jalankan `alembic current` — pastikan skema hasil restore sesuai versi aplikasi yang akan dijalankan (DEP-001 §4).
6. Start aplikasi, verifikasi `GET /health` + smoke test create/get case.
7. Buka layanan; catat data gap (antara titik restore dan insiden) untuk rekonsiliasi.

## 4. Prioritas Pemulihan

| Urutan | Komponen | Alasan |
|---|---|---|
| 1 | Database (PostgreSQL) | Sumber kebenaran case + audit_log + outbox |
| 2 | Aplikasi (case-service) | Layanan inti create/get case |
| 3 | Developer Portal | Internal tooling — bukan jalur layanan pelanggan |

## 5. Perlindungan Khusus `audit_log` (append-only)

- `audit_log` bersifat append-only/immutable (**BR-CP-03**, delivery BR-008) — **tidak boleh hilang atau terpangkas saat restore**.
- Aturan restore: bila titik restore lebih tua dari `audit_log` yang masih bisa diselamatkan (mis. dari WAL/replika), record audit yang lebih baru **wajib direkonsiliasi/dilampirkan**, bukan dibuang.
- Verifikasi pasca-restore: bandingkan `max(occurred_at)` dan jumlah baris `audit_log` terhadap catatan backup terakhir; selisih dilaporkan ke Security Officer.
- Revision Alembic yang menyentuh `audit_log` direview ekstra ketat (DEP-001 §4) — berlaku juga untuk skrip restore.

## 6. Business Continuity (singkat)

- **Planned (proses bisnis, di luar sistem):** saat outage panjang (> RTO), unit CS mencatat case secara **manual** (form/spreadsheet standar berisi field minimal: customerId, caseType, priority, subject, description, waktu terima) lalu meng-entry ulang ke ECMP setelah pulih — entry ulang menghasilkan audit trail normal.
- Prosedur manual detail (form, penanggung jawab, batas waktu entry ulang) disusun bersama Business Owner saat shared env pertama aktif — belum ada sekarang.
- Komunikasi outage: eskalasi per matrix OPS-RB-001 §4; pemberitahuan stakeholder oleh Operations Lead.

## 7. Trigger Review

Dokumen ini **wajib direview dan dinaikkan dari Draft** saat baseline SIT/UAT ADR-010 diaktifkan (fase target auth ADR-007 aktif) — saat itu seluruh item Planned di §2, §3, §6 harus menjadi prosedur nyata yang teruji (restore drill minimal 1x sebelum UAT).

## Related
- `./ECMP_Runbook_Slice_v0.1.md` (OPS-RB-001)
- `../14 Deployment Standards/ECMP_Deployment_Standards_v0.1.md` (DEP-001 §4 rollback)
- `../05 Architecture Decision Records/ECMP_ADR_010_Deployment_Platform_Baseline_v1.0.md`
- `../02 Business Rules/` (BR-CP-03), `../27 Project Decisions/DEC-004_BR_Baseline_Defaults_v1.0.md`
