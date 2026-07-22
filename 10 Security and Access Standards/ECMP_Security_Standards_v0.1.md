# ECMP Security Standards v0.1

| Field | Value |
|---|---|
| ID | SEC-STD-001 |
| Version | 0.1 |
| Owner | Security Architect |
| Reviewer | Solution Architect / Compliance |
| Approver | Architecture Board |
| Status | 🟢 Approved (baseline Sprint-01; diperluas per gate) |
| Last Review | 2026-07-21 |
| Next Review | 2026-10-21 |

## 1. Security Principles
1. AuthN wajib untuk semua akses fungsional (BR-007 / BR-CP-01). Endpoint tanpa auth hanya `/health`.
2. AuthZ = role + permission; org-unit scoping menyusul di G1 (BR-CP-02, register L-3).
3. Need-to-know untuk data pelanggan (BR-CRM-02).
4. Audit trail immutable untuk semua write signifikan (BR-008); append-only, tanpa jalur update/delete aplikasi.
5. Tidak ada secret di source/repo — semua via environment (`.env` di-ignore; `.env.example` non-secret).

## 2. Identity & Access Management
- Fase slice & fase target ditetapkan di **ADR-007** (Bearer env-token → JWT/OIDC sebelum shared UAT); desain fase target dielaborasi di **ADR-012** + `ECMP_Target_Authentication_Architecture_v1.0.md` (SEC-AUTH-001).
- Claims slice: `{userId, permissions[]}`; target: token membawa `{sub, roles[], orgUnitId, sid}` — permissions **tidak** di token, diresolusi Core Platform dari Role-Permission matrix (SoT per ADR-008, lihat SEC-AUTH-001 §4).
- Semantik: 401 `UNAUTHENTICATED` (gagal autentikasi), 403 `FORBIDDEN` (tanpa permission).
- Migrasi & rollout: `ECMP_AuthN_Migration_Rollout_Plan_v1.0.md` (SEC-MIG-001); dev-token tetap sah hanya untuk DEV lokal/CI.

## 3. Role Matrix
Lihat `ECMP_Role_Access_Matrix_v0.1.md` (SoT = Core Platform per ADR-008).

## 4. Data Classification & Protection
- PII flag per entitas mengikuti `06 Data Dictionary` (kolom PII).
- `description` case dapat memuat PII pelanggan → dilarang masuk log aplikasi; hanya tersimpan di DB + audit.
- Masking/retention detail = backlog `17 Compliance` (belum menghalangi slice).

## 5. Logging & Monitoring (Audit)
- Write-audit: tabel `audit_log` (actor, action, entity, new_value, occurred_at UTC) ditulis dalam transaksi yang sama dengan write bisnis (FR-001c).
- Read-audit: ditunda (OQ-007) — keputusan tercatat, bukan kelalaian.
- Event durable via outbox (ADR-009) memberi jejak integrasi.

## 6. Secure Development Controls
- CI backend wajib hijau (lint + OpenAPI validate + migrate + pytest) sebelum merge (`backend-ci.yml`).
- Kontrak dulu: endpoint tanpa OpenAPI dilarang (`ai/04_api.md`); `_dev/*` digate `ECMP_ENABLE_DEV_ENDPOINTS`.

## 7. Secrets & Credential Management
- Lokal: `.env` (git-ignored) dari `.env.example`.
- CI: GitHub Actions secrets/env — tidak pernah menulis nilai ke file repo.
- PROD: vault/secret manager — dipilih bersama keputusan platform deployment (lihat `14 Deployment Standards`).

## 8. Compliance Mapping
- BR-CP-01..04, BR-CRM-01..04, BR-008 → dipetakan di bagian terkait di atas; detail regulasi = `17 Compliance`.

## Related
- `ECMP_Role_Access_Matrix_v0.1.md`, `ECMP_AuthN_Limitations_Register_v0.1.md`
- ADR-007, ADR-008
