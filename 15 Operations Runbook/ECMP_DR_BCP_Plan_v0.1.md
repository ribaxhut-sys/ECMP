# ECMP Disaster Recovery & Business Continuity Plan

| Field | Value |
|---|---|
| ID | OPS-DR-001 |
| Version | 1.0.1 |
| Date | 2026-07-30 |
| Owner | Operations Lead |
| Reviewer | DevOps Lead / Solution Architect |
| Approver | Operations Lead |
| Status | 🟢 Active (plan) — automation / WAL / shared drill still gated |
| Last Review | 2026-07-30 |
| Next Review | 2027-01-21 |
| Task | TASK-PLATFORM-SECMIG-P6-003 |
| Revision | P6-003 review: `audit_logs` / `created_at`; `audit_logs_legacy` explicit |
| Stack | Foundation: root `backend/`, `frontend/`, `docker-compose.prod.yml` |

Honest boundaries: **no** backup scheduler, WAL, PITR, Vault, KMS, HA, or replication
in this task. DEV lokal **tidak di-backup** (data sintetis). Shared-env restore drill
sebelum UAT tetap **wajib** (lihat OPS-RCV-001).

## 1. Sasaran pemulihan

| Sasaran | Target (DEC-005) | Kapabilitas saat ini |
|---|---|---|
| **RTO** | **4 jam** | Manual restore + Compose redeploy foundation; ukur tiap drill |
| **RPO** | **15 menit** (butuh WAL — **belum ada**) | **= selang sejak logical dump terakhir** (OPS-BAK-001). Jangan klaim 15 menit. |

Nilai target berlaku untuk staging/production / shared env; DEV tidak punya RTO/RPO.

## 2. Backup (ringkas)

Sumber prosedur lengkap: [`./ECMP_Backup_Operations_Guide_v1.0.md`](./ECMP_Backup_Operations_Guide_v1.0.md).

| Mekanisme | Status |
|---|---|
| Manual logical `pg_dump` (pre-upgrade / ad-hoc) | **Aktif (prosedur)** — foundation Compose |
| Config sealed copy + secret sealed store | **Aktif (prosedur)** — OPS-BAK-001 / OPS-SEC-SEC-001 |
| Daily automated dump / WAL / PITR | **Future — out of scope P6-003** |
| DEV volume | **Tidak di-backup** |

## 3. Prosedur restore (outline)

Detail: [`./ECMP_Restore_Verification_Procedure_v0.1.md`](./ECMP_Restore_Verification_Procedure_v0.1.md).

1. Deklarasikan insiden; hentikan writers (OPS-SHDN-001).
2. Verifikasi checksum dump; provision/verify Postgres 16.
3. Restore logical dump (`pg_restore` / `psql`). **Jangan** asumsikan WAL replay.
4. Selaraskan sealed `.env` + secrets; jalankan `validate-production-config.py`.
5. Verifikasi **`audit_logs`** (`created_at`) — dan **`audit_logs_legacy`** (`occurred_at`) bila relevan — (§5) sebelum buka traffic.
6. `alembic current` harus cocok dengan tag aplikasi (`backend/` entrypoint migrations).
7. Start stack: `docker compose -f docker-compose.prod.yml` (postgres → backend → frontend → caddy).
8. Verifikasi **`GET /live`** dan **`GET /ready`** (HTTPS di production), lalu smoke auth + critical path.
9. Buka layanan; catat data gap (RPO aktual) untuk rekonsiliasi.

**Legacy note:** dokumen lama menyebut `GET /health` / `/health/ready`. Foundation stack memakai **`/live`** dan **`/ready`**. Keycloak management `/health/ready` hanya untuk IdP DEV pack — bukan probe aplikasi ECMP.

## 4. Prioritas pemulihan

| Urutan | Komponen | Alasan |
|---|---|---|
| 1 | Database (PostgreSQL) | SoT case/complaint + `audit_logs` (+ `audit_logs_legacy`) + outbox |
| 2 | Secrets + configuration (sealed) | App tidak boleh start dengan kredensial salah |
| 3 | Aplikasi (`backend/` API) | Layanan inti |
| 4 | Frontend | UI konsumen API |
| 5 | TLS proxy (Caddy) | HTTPS edge |
| 6 | Local DEV IdP pack (`implementation/infrastructure`) | **Historical / DEV-only** — bukan jalur recovery production |

## 5. Perlindungan khusus audit (append-only)

### 5.1 Platform `audit_logs` (canonical)

- Tabel **`audit_logs`** immutable untuk platform AuditService (**BR-CP-03**, BR-008) — **tidak boleh** dipangkas saat restore.
- Timestamp verifikasi: **`created_at`** (`SELECT COUNT(*), MAX(created_at) FROM audit_logs`).
- Pasca-restore: bandingkan jumlah baris dan `max(created_at)` vs catatan backup; laporkan selisih ke Security Officer.
- Revision Alembic yang menyentuh `audit_logs` direview ketat — berlaku juga untuk skrip restore.

### 5.2 Legacy `audit_logs_legacy` (eksplisit)

- Writer domain Complaint/Auth/Resolution memakai **`audit_logs_legacy`** (bukan `audit_log`).
- Timestamp verifikasi: **`occurred_at`** (`SELECT COUNT(*), MAX(occurred_at) FROM audit_logs_legacy`).
- Jangan menyamakan dengan gate platform `audit_logs`; verifikasi keduanya bila dump mencakup keduanya.
- Jika fragmen audit lebih baru masih bisa diselamatkan (future WAL/replika): rekonsiliasi/lampirkan, jangan buang.

## 6. Application & deployment recovery

| Skenario | Acuan |
|---|---|
| Redeploy / upgrade gagal | `../docs/deployment/UPGRADE_PROCEDURE.md`, `../docs/deployment/STARTUP_CHECKLIST.md` |
| Rollback rilis | `../docs/releases/ROLLBACK_v1.0.0.md` |
| Secret compromise / bad rotate | OPS-SEC-SEC-001 + OPS-SEC-RB-001 |
| Config AuthN gagal start | P6-001 validator; jangan turunkan ke `dev` mode di staging/production |
| Restore validation / RTO-RPO evidence | OPS-RCV-001 |

Startup validation minimum setelah recovery:

```powershell
python scripts\validate-production-config.py --env-file .env --require-production
curl.exe -fsS https://$env:ECMP_DOMAIN/live
curl.exe -fsS https://$env:ECMP_DOMAIN/ready
```

## 7. Business Continuity (singkat)

- **Planned (proses bisnis):** outage > RTO → unit CS catat case manual (field minimal: customerId, caseType, priority, subject, description, waktu terima) lalu entry ulang setelah pulih (audit trail normal).
- Detail form/owner disusun bersama Business Owner saat shared env penuh — belum wajib di P6-003.
- Komunikasi: eskalasi OPS-RB-001 / OPS-SEC-RB-001; Operations Lead memberitahu stakeholder.

## 8. Trigger review & drills

- Review wajib saat shared SIT/UAT ADR-010 diaktifkan penuh, atau saat otomasi/WAL diotorisasi terpisah.
- Sprint-09 DEV scratch restore drill **PASS** (OPS-RST-001 §9) — **tidak** menggantikan shared-env drill.
- Checklist operasional: [`./ECMP_Recovery_Validation_Checklist_v1.0.md`](./ECMP_Recovery_Validation_Checklist_v1.0.md).

## 9. Companion documents

| ID | Document |
|---|---|
| OPS-BAK-001 | `./ECMP_Backup_Operations_Guide_v1.0.md` |
| OPS-RST-001 | `./ECMP_Restore_Verification_Procedure_v0.1.md` |
| OPS-RCV-001 | `./ECMP_Recovery_Validation_Checklist_v1.0.md` |
| OPS-RB-001 | `./ECMP_Runbook_Slice_v0.1.md` |
| DEP / deploy | `../docs/deployment/`, `../14 Deployment Standards/` |

## Related

- `../27 Project Decisions/DEC-005_SLA_NFR_Baseline_Targets_v1.0.md`
- `../05 Architecture Decision Records/ECMP_ADR_010_Deployment_Platform_Baseline_v1.0.md`
- `../02 Business Rules/` (BR-CP-03), `../27 Project Decisions/DEC-004_BR_Baseline_Defaults_v1.0.md`
