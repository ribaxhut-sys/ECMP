# ECMP Runbook — Foundation + Slice Companion

| Field | Value |
|---|---|
| ID | OPS-RB-001 |
| Version | 0.3 |
| Owner | Operations Lead |
| Reviewer | DevOps / Tech Lead Backend |
| Approver | Operations Lead |
| Status | 🟡 Draft |
| Last Review | 2026-07-30 |
| Next Review | 2027-01-21 |
| Related | OPS-SEC-RB-001 (security playbooks), SECMIG-P6-002 |

Runbook untuk operasi harian. **Stack kanonis produksi / SEC-MIG:** root `backend/`, `frontend/`, Compose di root repo. Prosedur shared-env mendalam masih bertanda **Planned** hingga baseline SIT/UAT ADR-010 penuh.

Security-specific incidents (auth, lockout, secret compromise, config AuthN) → [`./ECMP_Security_Operations_Runbook_v1.0.md`](./ECMP_Security_Operations_Runbook_v1.0.md).

## 1. Service Inventory & Ownership

| Service | Deskripsi | Cara jalan | Owner | Backup/Eskalasi |
|---|---|---|---|---|
| ecmp-backend | Foundation FastAPI (`backend/`) | `docker compose up backend` atau `uvicorn app.main:app` dari `backend/` | Backend Lead | Tech Lead / Solution Architect |
| ecmp-frontend | Next.js UI (`frontend/`) | Compose `frontend` / local Node | Frontend Lead | Tech Lead |
| PostgreSQL 16 | DB foundation | Root `docker-compose.yml` / `docker-compose.prod.yml` service `postgres` | DevOps Lead | SRE / Operations |
| Reverse proxy | Caddy (prod) / Nginx alt | `docker-compose.prod.yml` | DevOps Lead | SRE |
| Keycloak (optional DEV) | Local IdP baseline realm `ecmp` — SEC-MIG Phase 1 pack | **Historical/pack path:** `implementation/infrastructure/docker-compose.yml --profile auth` (OPS-IDP-001) | DevOps Lead / Security Architect | Tech Lead |
| Developer Portal | Internal RAG/coverage (ADR-011) — not product UI | **Historical/pack path:** `implementation/portal` | Engineering Manager / EA | Tech Lead |

> **Historical (Sprint-01 slice):** `implementation/backend` (`ecmp-case-service`) was the early create/get case pack. Do not use it for production SEC-MIG operations.

## 2. Health Check

- Probes (foundation): `GET /live`, `GET /ready`, `GET /health` (no auth).
- Expected: `/live` 200; `/ready` 200 when startup + DB ok (503 when not).
- Local: `curl http://127.0.0.1:8000/ready`.
- Production: `curl https://<ECMP_DOMAIN>/ready` (host :8000 not published on prod compose).
- Planned (SIT/UAT per ADR-010): same probes for uptime monitors.

## 3. Playbooks

### P1 — Service tidak start / crash saat boot
1. **Symptom:** Backend container exit / uvicorn mati; `/ready` gagal.
2. **Impact:** API tidak tersedia.
3. **Detection:** Compose unhealthy; logs `Configuration validation failed`; connection errors.
4. **Diagnosis steps:**
   - Cek env: `.env` / `.env.example` di **repo root**; `JWT_SECRET_KEY`, `POSTGRES_*`, dan untuk staging/production `ECMP_AUTH_MODE=jwt` + `OIDC_*` (P6-001).
   - `python scripts/validate-production-config.py --env-file .env`
   - Migrasi: entrypoint menjalankan `alembic upgrade head` dari `backend/`.
   - Security config incidents → SEC-P4 in OPS-SEC-RB-001.
5. **Mitigation / workaround:** Perbaiki konfigurasi; jangan set `ECMP_AUTH_MODE=dev` di production.
6. **Resolution:** Backend healthy; log `application started` dengan `env` / `auth_mode` yang diharapkan.
7. **Escalation:** L1 → L2 Backend Lead / DevOps.
8. **Post-incident actions:** Update `.env.example` / deployment docs bila footgun baru.

### P2 — Database down / connection refused
1. **Symptom:** connection refused / could not connect ke PostgreSQL.
2. **Impact:** API 500 / `/ready` 503.
3. **Detection:** SQLAlchemy/psycopg errors; postgres healthcheck merah.
4. **Diagnosis steps:**
   - `docker compose ps` (root) — service `postgres` healthy?
   - `docker logs` for postgres service.
   - Credential / `POSTGRES_HOST` (compose injects `postgres`).
5. **Mitigation / workaround:** restart postgres; jangan `down -v` di shared/prod.
6. **Resolution:** `pg_isready` hijau; `/ready` 200.
7. **Escalation:** L2 DevOps (infra) / Backend (DSN).
8. **Post-incident actions:** Shared env → pertimbangkan alerting (Planned ADR-010).

### P3 — Outbox backlog menumpuk
1. **Symptom:** baris `outbox` dengan `published_at IS NULL` menua terus.
2. **Impact:** event tidak terpublikasi. Per ADR-009 broker lintas-service belum ada — backlog sering **by design** sampai publisher ada.
3. **Detection:** SQL count `published_at IS NULL`.
4. **Diagnosis / Mitigation / Resolution:** Fase tanpa broker — bukan insiden. Pasca broker: restart publisher; jangan hapus outbox.
5. **Escalation:** L2 Backend Lead; skema → L3 Solution Architect.
6. **Post-incident actions:** relay tests saat publisher aktif.

### P4 — Migrasi Alembic gagal
1. **Symptom:** `alembic upgrade head` error (entrypoint / CI / deploy).
2. **Impact:** skema tidak sinkron; container exit.
3. **Detection:** non-zero alembic; CI merah.
4. **Diagnosis steps:** `alembic current` / `history` dari `backend/`; review bila menyentuh `audit_logs` (DEP-001 §4).
5. **Mitigation:** rollback aplikasi per [`../docs/releases/ROLLBACK_v1.0.0.md`](../docs/releases/ROLLBACK_v1.0.0.md); downgrade hanya dengan approval.
6. **Resolution:** upgrade hijau; `/ready` 200.
7. **Escalation:** L2 Backend; audit_logs / hapus data → L3.
8. **Post-incident actions:** catat pola ke checklist migrasi.

### P5 — SLA breach response (operasional) — baseline
1. **Symptom:** case melewati ambang SLA — target numerik baseline per `../11 SLA and KPI Matrix/ECMP_SLA_Matrix_v0.1.md`.
2. **Impact:** komitmen layanan terlanggar.
3. **Detection:** **Planned** otomatis (EVT-004); saat ini manual.
4. **Mitigation / Resolution:** prioritaskan penanganan; eskalasi supervisor (BR-NOTIF-04 baseline).
5. **Escalation / Post-incident:** supervisor unit; review penyebab.

### P6 — Notification failure handling — Planned
1. **Symptom:** notifikasi gagal terkirim.
2. **Impact / Detection / Resolution:** **Planned** — domain Notification belum dibangun (DEC-002). Baseline masa depan: retry 3× / 5 menit lalu email supervisor (BR-NOTIF-04).

## 4. Escalation Matrix

| Level | Peran | Kapan |
|---|---|---|
| L1 | Support / on-duty operations | Triage awal; jalankan playbook |
| L2 | Backend Lead atau DevOps Lead | Kode/infra/config |
| L2-SEC | Security Architect / Security Officer | Compromise, abuse, audit integrity (OPS-SEC-RB-001) |
| L3 | Solution Architect / Operations Lead | Arsitektur, restore destruktif, lintas tim |

## 5. Berlaku sekarang vs Planned

| Item | Status |
|---|---|
| P1, P2, P4 (foundation DEV/CI/prod compose) | Berlaku sekarang |
| Security playbooks OPS-SEC-RB-001 | Berlaku sekarang (foundation) |
| P3 | Monitoring; insiden nyata pasca ADR-009 publisher |
| P5 / P6 | Baseline manual / Planned |
| Backup / restore / DR docs (P6-003) | Berlaku sekarang (manual; no scheduler/WAL) |
| Shared-env restore drill & WAL | Drill Planned — ADR-010; WAL = Future |

## 6. Companion procedures

| ID | Document | Use when |
|---|---|---|
| OPS-SEC-RB-001 | `./ECMP_Security_Operations_Runbook_v1.0.md` | Security incidents |
| OPS-SEC-SEC-001 | `./ECMP_Secret_Operations_Guide_v1.0.md` | Secret rotate / compromise |
| OPS-SEC-AUD-001 | `./ECMP_Audit_Investigation_Guide_v1.0.md` | Investigate `security.*` |
| OPS-BAK-001 | `./ECMP_Backup_Operations_Guide_v1.0.md` | Backup policy / pre-upgrade dump |
| OPS-RST-001 | `./ECMP_Restore_Verification_Procedure_v0.1.md` | Restore procedure |
| OPS-DR-001 | `./ECMP_DR_BCP_Plan_v0.1.md` | Disaster recovery / BCP |
| OPS-RCV-001 | `./ECMP_Recovery_Validation_Checklist_v1.0.md` | Restore drill validation / RPO-RTO evidence |
| OPS-SHDN-001 | `./ECMP_Shutdown_Procedure_v0.1.md` | Orderly stop |
| OPS-LOG-001 | `./ECMP_Log_Inspection_Procedure_v0.1.md` | Log + request id lookup |

## Related
- `../14 Deployment Standards/ECMP_Deployment_Standards_v0.1.md` (DEP-001)
- `../docs/deployment/`
- `./ECMP_DR_BCP_Plan_v0.1.md` (OPS-DR-001)
