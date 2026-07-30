# ECMP Release Management

| Field | Value |
|---|---|
| ID | REL-001 |
| Version | 0.3 |
| Owner | Release Manager |
| Reviewer | QA / Ops / Security |
| Approver | PMO |
| Status | 🟢 Approved |
| Last Review | 2026-07-30 |
| Next Review | 2027-01-30 |
| Task note | SECMIG-P6-004 — security gate + approval + evidence linked; P6-005 precedence |

**Canonical folder entry:** [`./README.md`](./README.md) (Release Management index).

**Foundation cutover precedence:** REL-SEC-001 → DEP-CHK-V1 → START-CHK-001  
(see [`../docs/deployment/README.md`](../docs/deployment/README.md)). Historical DEP-CHK-001 is not used for foundation production cutover.

Proses rilis ECMP: unit rilis historis = **slice per gate** (G0 → B1 → G1 → B2 …).
Untuk **shared staging / UAT / production** foundation stack, Go/No-Go keamanan
dan operasional mengikuti **Release Security Gate** (REL-SEC-001) di bawah — tidak
digantikan hanya oleh checklist RC internal.

## 1. Versioning kontrak API (semver — ADR-006)

- **MAJOR** = breaking change → prefix path baru (`/v2`) + file katalog baru (`<service>.v2.yaml`).
- **MINOR** = penambahan backward-compatible (field opsional, endpoint baru) — prefix tetap `/v1`, `info.version` naik (mis. `1.1.0`).
- **PATCH** = klarifikasi/perbaikan non-perilaku pada kontrak.
- `info.version` di OpenAPI adalah semver penuh kontrak dan wajib di-bump pada PR yang mengubah kontrak.

## 2. Deprecation policy (ADR-006)

- Versi API lama hidup **minimal 2 minor release** setelah pengumuman deprecation.
- Selama masa deprecation, respons versi lama menyertakan header `Deprecation: true` dan `Sunset: <date>`.
- Pengumuman deprecation dicatat di changelog PR + dikomunikasikan ke konsumen terdaftar (saat ini belum ada konsumen eksternal — kewajiban aktif begitu ada).

## 3. Kriteria Go / No-Go

### 3.1 Rilis slice (engineering gate)

Rilis slice (menutup gate / mengaktifkan build berikutnya) hanya **Go** bila semuanya terpenuhi:

1. **CI hijau** — `backend-ci.yml` lulus penuh pada commit kandidat (ruff, contract, migrate, pytest vs PostgreSQL).
2. **Katalog sinkron** — OpenAPI (`07`), Event SoT (`08`), dan `26 Traceability` mencerminkan perilaku runtime; tidak ada endpoint/event liar (DoD ENG-003).
3. **Exit criteria gate terpenuhi** — checklist gate terkait (contoh: G0 di DEC-002) tercentang dengan bukti.
4. **Sign-off Tech Lead + Solution Architect** — sesuai DEC-002 butir 2; tanpa dua tanda tangan ini statusnya No-Go, sekencang apa pun tekanan jadwal.
5. **Scope bersih** — tidak ada fitur non-goals (DEC-002 butir 3) yang menyelinap ke dalam slice.

No-Go → catat alasan di gate checklist, perbaiki, ulangi. Tidak ada "Go bersyarat".

### 3.2 Shared / staging / UAT / production (Release Security Gate)

Selain §3.1 (jika slice berlaku), promosi ke lingkungan bersama atau production **wajib**:

1. Semua mandatory gates **PASS** per [`./ECMP_Release_Security_Gate_v1.0.md`](./ECMP_Release_Security_Gate_v1.0.md) (REL-SEC-001):
   Configuration, Authentication, Authorization, Audit, Backup, Recovery, Smoke.
2. Evidence pack lengkap per [`./ECMP_Release_Evidence_Template_v1.0.md`](./ECMP_Release_Evidence_Template_v1.0.md) (REL-EVID-001).
3. Sign-off **Tech Lead + Security Officer/Architect + Operations Lead + Release Manager**
   per [`./ECMP_Release_Approval_Matrix_v1.0.md`](./ECMP_Release_Approval_Matrix_v1.0.md) (REL-APR-001).

Internal DEV RC tetap memakai [`./ECMP_RC_Release_Checklist_v0.1.md`](./ECMP_RC_Release_Checklist_v0.1.md);
RC **tidak** boleh diklaim sebagai shared/prod ready tanpa REL-SEC-001.

## 4. Changelog

- **Repository release notes** hidup di root `CHANGELOG.md` (Keep a Changelog) per
  `ECMP_Repository_Versioning_Policy_v0.1.md` — wajib diisi sebelum tag RC/release.
- PR descriptions tetap mencatat BR/FR/ADR/API/EVT ID dan **Contract impact**
  (none / minor / breaking) sebagai input ke keputusan versi API (§1) dan deprecation (§2).
- Ringkasan per versi boleh dipublikasikan sebagai `ECMP_Release_Notes_<Version>.md`
  atau di `docs/releases/`.

## 5. Rollback decision

- Mekanik: `../14 Deployment Standards` (DEP-001 §4) dan
  [`../docs/releases/ROLLBACK_v1.0.0.md`](../docs/releases/ROLLBACK_v1.0.0.md).
- DB restore: [`../15 Operations Runbook/ECMP_Restore_Verification_Procedure_v0.1.md`](../15%20Operations%20Runbook/ECMP_Restore_Verification_Procedure_v0.1.md).
- **Approvers:** lihat REL-APR-001 §4 (app-only vs secret-only vs destructive DB).
- Rollback skema DB: Solution Architect; integritas `audit_logs` / `audit_logs_legacy`: Security Officer.

## 6. Repository versioning & RC

- App/repo SemVer: `ECMP_Repository_Versioning_Policy_v0.1.md` (REL-VER-001)
- Annotated git tags: `ECMP_Git_Tag_Convention_v0.1.md` (REL-TAG-001)
- RC cut checklist: `ECMP_RC_Release_Checklist_v0.1.md` (REL-RC-001)
- Shared/prod Go: REL-SEC-001 + REL-APR-001 + REL-EVID-001 (+ ADR-010/ADR-012 as applicable)

## 7. Companion index

| Topic | Document |
|---|---|
| Documentation hub | `../docs/deployment/README.md` |
| Deployment | `../docs/deployment/PRODUCTION_DEPLOYMENT_GUIDE.md` |
| Startup | `../docs/deployment/STARTUP_CHECKLIST.md` |
| Deploy checklist (DEP-CHK-V1) | `../docs/deployment-checklist.md` |
| Secure config (P6-001) | `../docs/deployment/ENVIRONMENT_VARIABLE_REFERENCE.md` |
| Security operations | `../15 Operations Runbook/ECMP_Security_Operations_Runbook_v1.0.md` |
| Backup | `../15 Operations Runbook/ECMP_Backup_Operations_Guide_v1.0.md` |
| Restore | `../15 Operations Runbook/ECMP_Restore_Verification_Procedure_v0.1.md` |
| Recovery | `../15 Operations Runbook/ECMP_Recovery_Validation_Checklist_v1.0.md` |
| Rollback | `../docs/releases/ROLLBACK_v1.0.0.md` |
| Security tests (manual gate evidence) | `../docs/deployment/SECURITY_TEST_SUITE.md` |

## Related

- ADR-006 (`../05 Architecture Decision Records`)
- `../27 Project Decisions/DEC-002_Build_Authorization_G0_v1.0.md`
- `../14 Deployment Standards/ECMP_Deployment_Standards_v0.1.md` (DEP-001)
- `../13 Test Strategy/ECMP_Test_Strategy_v0.1.md` (TST-001)
- `../CHANGELOG.md`
- `./README.md`
