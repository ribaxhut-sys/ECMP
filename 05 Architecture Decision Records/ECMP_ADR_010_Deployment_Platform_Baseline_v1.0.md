# ECMP_ADR_010_Deployment_Platform_Baseline_v1.0

| Field | Value |
|---|---|
| ID | ADR-010 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | DevOps Lead / Security |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2026-10-21 |

- ADR Status: Accepted (Architecture Board, 2026-07-21 — gap remediation)
- Date: 2026-07-21
- Decision Owners: Solution Architect, DevOps Lead
- Related Domains: All (deployment platform)

## Context
Deployment Standards (DEP-001) jujur bahwa hanya DEV dan CI yang benar-benar ada; SIT/UAT/PROD tercatat sebagai **open decision** dengan larangan environment bersama sebelum (a) ADR platform dan (b) fase target auth ADR-007 (JWT/OIDC) aktif. Membiarkan seluruh rantai environment "open" menghambat perencanaan UAT — padahal memilih platform PROD sekarang adalah keputusan tanpa data beban (pola yang sama dengan penundaan broker di ADR-009).

## Decision
Keputusan bertahap (pola deferral ADR-009): formalkan yang sudah nyata, putuskan baseline yang dibutuhkan UAT, tunda eksplisit yang belum punya data.

1. **DEV — formalisasi status quo.** PostgreSQL 16 via `implementation/infrastructure/docker-compose.yml`; aplikasi jalan via `uvicorn` di host (bukan container). Fallback lokal tanpa Docker: SQLite file (default `ECMP_DATABASE_URL` di `settings.py`) — hanya untuk bootstrap lokal; PostgreSQL tetap wasit paritas (TST-001 §5).
2. **CI — formalisasi status quo.** GitHub Actions `backend-ci.yml` dengan PostgreSQL 16 service container; urutan ruff → validate OpenAPI → `alembic upgrade head` → pytest tetap gate wajib PR (DEC-002).
3. **SIT/UAT — baseline diputuskan.** Container via Docker Compose pada **satu VM managed** + deploy via GitHub Actions. **Hanya boleh diaktifkan setelah fase target auth ADR-007 (JWT/OIDC) aktif** — selaras larangan DEP-001 §1 (dev-token dilarang di shared environment). Aktivasi baseline ini sekaligus memicu deliverable yang selama ini dilarang spekulatif: Dockerfile aplikasi, registry, tagging standard (TS-001 §7).
4. **PROD — ditunda eksplisit.** Bukan open question lagi, melainkan deferral yang diputuskan. **Trigger evaluasi** (mana yang lebih dulu): (a) UAT pertama sukses, (b) ada data volume/beban nyata, (c) keputusan budget/procurement dari sponsor. Kandidat dievaluasi saat itu: **managed container service** (mis. ECS/Cloud Run/App Service) vs **Kubernetes** — tidak dipilih sekarang.

## Consequences
- Bagian "SIT / UAT / PROD — open decision" di DEP-001 §1 berubah menjadi rujukan ke ADR ini; larangan shared env sebelum fase target ADR-007 tetap berlaku tanpa perubahan.
- Rencana UAT dapat disusun terhadap baseline compose-on-VM tanpa menunggu keputusan platform PROD.
- Migrasi SIT/UAT → platform PROD adalah keputusan terpisah saat trigger tersentuh; definisi service di compose tetap berguna sebagai sumber migrasi (bukan perombakan).
- Sampai SIT/UAT aktif: tetap dilarang membangun Dockerfile/registry/observability stack spekulatif (DEP-001 §5, TS-001 §7).

## Compliance / Follow-up
- [x] Update DEP-001 §1 agar merujuk ADR-010
- [ ] Dockerfile aplikasi + registry/tagging standard — dikerjakan saat aktivasi SIT/UAT (bukan sekarang)
- [ ] Mekanisme secret shared env (vault/secret manager, DEP-001 §2) — bersamaan aktivasi SIT/UAT
- [ ] ADR platform PROD — saat trigger evaluasi butir 4 tersentuh
