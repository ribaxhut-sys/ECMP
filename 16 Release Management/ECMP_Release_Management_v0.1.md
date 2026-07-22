# ECMP Release Management

| Field | Value |
|---|---|
| ID | REL-001 |
| Version | 0.2 |
| Owner | Release Manager |
| Reviewer | QA / Ops |
| Approver | PMO |
| Status | 🟢 Approved (Sprint-10 release mechanics) |
| Last Review | 2026-07-22 |
| Next Review | 2027-01-22 |

Proses rilis ECMP fase slice: unit rilis adalah **slice per gate** (G0 → B1 → G1 → B2 …), bukan release train berkala. Cadence kalender baru ditetapkan saat ada environment bersama.

## 1. Versioning kontrak API (semver — ADR-006)

- **MAJOR** = breaking change → prefix path baru (`/v2`) + file katalog baru (`<service>.v2.yaml`).
- **MINOR** = penambahan backward-compatible (field opsional, endpoint baru) — prefix tetap `/v1`, `info.version` naik (mis. `1.1.0`).
- **PATCH** = klarifikasi/perbaikan non-perilaku pada kontrak.
- `info.version` di OpenAPI adalah semver penuh kontrak dan wajib di-bump pada PR yang mengubah kontrak.

## 2. Deprecation policy (ADR-006)

- Versi API lama hidup **minimal 2 minor release** setelah pengumuman deprecation.
- Selama masa deprecation, respons versi lama menyertakan header `Deprecation: true` dan `Sunset: <date>`.
- Pengumuman deprecation dicatat di changelog PR + dikomunikasikan ke konsumen terdaftar (saat ini belum ada konsumen eksternal — kewajiban aktif begitu ada).

## 3. Kriteria Go / No-Go rilis slice

Rilis slice (menutup gate / mengaktifkan build berikutnya) hanya **Go** bila semuanya terpenuhi:

1. **CI hijau** — `backend-ci.yml` lulus penuh pada commit kandidat (ruff, contract, migrate, pytest vs PostgreSQL).
2. **Katalog sinkron** — OpenAPI (`07`), Event SoT (`08`), dan `26 Traceability` mencerminkan perilaku runtime; tidak ada endpoint/event liar (DoD ENG-003).
3. **Exit criteria gate terpenuhi** — checklist gate terkait (contoh: G0 di DEC-002) tercentang dengan bukti.
4. **Sign-off Tech Lead + Solution Architect** — sesuai DEC-002 butir 2; tanpa dua tanda tangan ini statusnya No-Go, sekencang apa pun tekanan jadwal.
5. **Scope bersih** — tidak ada fitur non-goals (DEC-002 butir 3) yang menyelinap ke dalam slice.

No-Go → catat alasan di gate checklist, perbaiki, ulangi. Tidak ada "Go bersyarat".

## 4. Changelog

- **Repository release notes** hidup di root `CHANGELOG.md` (Keep a Changelog) per
  `ECMP_Repository_Versioning_Policy_v0.1.md` — wajib diisi sebelum tag RC/release.
- PR descriptions tetap mencatat BR/FR/ADR/API/EVT ID dan **Contract impact**
  (none / minor / breaking) sebagai input ke keputusan versi API (§1) dan deprecation (§2).
- Saat rilis ke environment bersama dimulai (masa depan), ringkasan per versi juga
  boleh dipublikasikan sebagai `ECMP_Release_Notes_<Version>.md` dari CHANGELOG.

## 5. Rollback decision

Kriteria dan mekanik rollback ada di `../14 Deployment Standards` (DEP-001 §4). Keputusan rollback pasca-rilis diambil oleh Tech Lead + Release Manager; rollback yang menyentuh skema DB membutuhkan konfirmasi Solution Architect.

## 6. Repository versioning & RC (Sprint-10)

- App/repo SemVer: `ECMP_Repository_Versioning_Policy_v0.1.md` (REL-VER-001)
- Annotated git tags: `ECMP_Git_Tag_Convention_v0.1.md` (REL-TAG-001)
- RC cut checklist: `ECMP_RC_Release_Checklist_v0.1.md` (REL-RC-001)
- Shared-environment Go tetap mengikuti §3 + ADR-010/ADR-012; RC1 = internal DEV only.

## Related
- ADR-006 (`../05 Architecture Decision Records`)
- `../27 Project Decisions/DEC-002_Build_Authorization_G0_v1.0.md`
- `../14 Deployment Standards/ECMP_Deployment_Standards_v0.1.md` (DEP-001)
- `../13 Test Strategy/ECMP_Test_Strategy_v0.1.md` (TST-001)
- `../CHANGELOG.md`
