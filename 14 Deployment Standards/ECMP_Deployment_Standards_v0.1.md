# ECMP Deployment Standards

| Field | Value |
|---|---|
| ID | DEP-001 |
| Version | 0.1 |
| Owner | DevOps Lead |
| Reviewer | Security / SRE |
| Approver | Architecture Board |
| Status | 🟢 Approved (baseline Sprint-01) |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

Standar deployment untuk fase slice. Dokumen ini jujur tentang batasnya: hanya DEV dan CI yang benar-benar ada; environment bersama menunggu keputusan platform.

## 1. Environment yang ada

### DEV (lokal developer)
- Database: PostgreSQL 16 via `implementation/infrastructure/docker-compose.yml`.
- Aplikasi: `uvicorn app.main:app` langsung di host (bukan container) dari `implementation/backend`.
- Skema: `alembic upgrade head` sebelum menjalankan aplikasi.
- Konfigurasi: env vars — template `implementation/backend/.env.example`; file `.env` **di-gitignore**, tidak pernah di-commit.

### CI (GitHub Actions — `backend-ci.yml`)
- PostgreSQL 16 sebagai service container (`ecmp/ecmp_ci@localhost:5432/ecmp_test`).
- Urutan: install deps → ruff → validate OpenAPI → `alembic upgrade head` → pytest.
- CI hijau adalah **gate wajib** untuk PR yang menyentuh `implementation/backend/**` atau `07 API Catalog/openapi/**` (DEC-002).

### SIT / UAT / PROD — diputuskan via **ADR-010**
Baseline platform diputuskan di `../05 Architecture Decision Records/ECMP_ADR_010_Deployment_Platform_Baseline_v1.0.md`:
- **SIT/UAT baseline:** container Docker Compose pada satu VM managed + deploy via GitHub Actions. **Hanya boleh diaktifkan setelah** fase target auth ADR-007 (JWT/OIDC) aktif — dev-token tetap dilarang di shared environment.
- **PROD: ditunda eksplisit** dengan trigger evaluasi (UAT pertama sukses / volume nyata / keputusan budget); kandidat managed container service vs Kubernetes dievaluasi saat itu.
- Sampai SIT/UAT diaktifkan: belum ada Dockerfile aplikasi/registry/tagging standard — deliverable tersebut dikerjakan saat aktivasi baseline (TS-001 §7), dilarang dibangun spekulatif sebelumnya.

## 2. Konfigurasi & Secrets

| Environment | Mekanisme | Aturan |
|---|---|---|
| Lokal | `.env` (git-ignored) dibaca `settings.py` | `.env.example` selalu up-to-date, tanpa nilai rahasia |
| CI | GitHub Actions secrets / env di workflow | Credential CI (mis. `ecmp_ci`) hanya untuk DB ephemeral CI, bukan credential nyata |
| PROD (target) | Vault/secret manager — **TBD bersama keputusan platform** | Tidak ada secret di image, repo, atau log |

Prinsip: satu artefak, banyak konfigurasi — perilaku environment dibedakan hanya oleh env vars (`ECMP_DATABASE_URL`, `ECMP_DEV_TOKEN`, `ECMP_ENABLE_DEV_ENDPOINTS`), bukan oleh branch/build berbeda.

## 3. Promotion & Gates
- Jalur promosi saat ini: PR → CI hijau → merge ke main. Deploy ke environment bersama belum ada; saat ada, promosi mengikuti Go/No-Go `../16 Release Management` (REL-001).
- `ECMP_ENABLE_DEV_ENDPOINTS` wajib `false`/unset di environment mana pun selain lokal/CI.

## 4. Rollback

- **Skema DB:** setiap Alembic revision wajib punya `downgrade()` yang berfungsi. Rollback = `alembic downgrade <rev>` + redeploy versi aplikasi yang kompatibel dengan skema tersebut.
- **Aplikasi:** redeploy artefak/commit sebelumnya (di fase slice: checkout commit sebelumnya + restart uvicorn).
- Urutan aman: turunkan aplikasi dulu ke versi lama, baru downgrade skema bila memang dibutuhkan; downgrade yang menghapus data (drop kolom/tabel berisi data) membutuhkan keputusan eksplisit, bukan otomatis.
- `audit_log` append-only tidak boleh hilang karena rollback — revision yang menyentuh `audit_log` direview ekstra ketat.

## 5. Observability
- Baseline sekarang: endpoint `/health` (tanpa versi) untuk liveness.
- Structured logging + correlation-id = backlog gate G1 (TS-001 §6). Metrics/tracing menunggu platform target — dilarang memasang stack observability spekulatif.

## Related
- `../16 Release Management/ECMP_Release_Management_v0.1.md` (REL-001)
- `../21 Technical Standards/ECMP_Technical_Standards_v0.1.md` (TS-001 §5, §7)
- ADR-004 (stack), ADR-007 (auth gate untuk shared env)
