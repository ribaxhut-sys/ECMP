# 18 Architecture Governance


| Field | Value |
|---|---|
| ID | GOV-000 |
| Version | 0.1 |
| Owner | Architecture Board Chair |
| Reviewer | PMO |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Tata kelola arsitektur ECMP: proses review, RACI, quality gates, dan pengelolaan ADR/standards.

**Master index (IMS):** [`ECMP_Integrated_Management_System_IMS-001_v1.0.md`](./ECMP_Integrated_Management_System_IMS-001_v1.0.md) — menghubungkan policy→evidence tanpa mengganti dokumen yang sudah approved.

## Owner
- Document Owner: Architecture Board Chair / Chief Architect
- Reviewers: Solution Architects, Security, Product Owners, PMO

## Status
Baseline terisi — RACI, quality gates, dan ADR lifecycle terdefinisi di bawah.

## Minimum Contents (v1)
- [x] Architecture governance process (RACI + gates + ADR lifecycle di bawah)
- [x] RACI matrix (bagian RACI di bawah)
- [x] Review checklist & forms (`reviews/`)
- [x] Review cadence & gates (bagian Quality Gates di bawah)
- [ ] Definition of Done for architecture artifacts (DoD engineering ada di `../22`; DoD artefak arsitektur menyusul)
- [x] Exception request form (`reviews/EXCEPTION_REQUEST.md`)
- [x] Linkage to ADR lifecycle (bagian ADR Lifecycle di bawah)

## RACI

R = Responsible, A = Accountable, C = Consulted, I = Informed.

| Aktivitas | Architecture Board | Solution Architect | Tech Lead | Security | PMO |
|---|---|---|---|---|---|
| ADR (usul → keputusan) | **A** | **R** | **R** | C | I |
| Technical Standards (TS-001) | **A** | C (Reviewer) | **R** (Owner) | C | I |
| Reference Patterns (REF-001) | **A** | **R** | C | C | I |
| Quality gate exit (G0/G1/G2) | I | **R** (sign-off) | **R** (sign-off) | C | I |
| Exception/waiver terhadap standar | **A** | **R** | C | C | I |
| Role/permission matrix (`10`) | I | C | C | **R/A** | I |
| Project Decisions non-arsitektur (`27`) | I | C | C | C | **R** (fasilitasi; Approver sesuai dokumen) |

Aturan dasar: satu **A** per baris; sign-off gate mengikuti DEC-002 (Tech Lead + Solution Architect — Board tidak menandatangani gate, hanya menerima laporan).

## Quality Gates (terhubung lifecycle)

Lifecycle: Idea → Blueprint → Rules → Solution/Domain Architecture → FRD → AI Context sync → Implementation → Test → Deploy → Ops → Feedback. Gate build didefinisikan operasional di `ai/sprint/IMPLEMENTATION_READINESS_ROADMAP.md`:

| Gate | Posisi lifecycle | Exit criteria (ringkas) | SoT |
|---|---|---|---|
| **G0** — Platform floor | FRD → Implementation (slice create/get) | Per DEC-002: compose+`.env.example`, Alembic rev 0, create = 1 transaksi (case+audit+outbox), error envelope = OpenAPI, CI hijau, role matrix minimal, sign-off Tech Lead + SA | `../27 Project Decisions/DEC-002` |
| **G1** — Lifecycle contract | Sebelum kode assign/status (Build-2) | State machine dibekukan: status enum + **transition matrix**, aturan assignment, FRD+OpenAPI+event payload merged sebelum kode, **org-scope authorization** (permission `cases:assign` dkk. + aturan org unit) di role matrix | Roadmap §G1 |
| **G2** — Cross-cutting mini-gate | Sebelum Notification stub / pendalaman CM | Catalog-first untuk Notification + CM; salah satu trigger evaluasi broker (ADR-009) | Roadmap §G2 |

Prinsip: gate = kontrak dibekukan **sebelum** kode; melewati gate tanpa exit criteria = pelanggaran governance, bukan percepatan.

## ADR Lifecycle

`Proposed → Accepted` via Architecture Board; jalur lengkap:

1. **Proposed** — SA/Tech Lead menulis ADR dari template (`../05 Architecture Decision Records/ADR-TEMPLATE.md`) dengan opsi + trade-off.
2. **Review** — dibahas di Architecture Board (form `reviews/ARCHITECTURE_REVIEW_FORM.md`, checklist `reviews/REVIEW_CHECKLIST.md`); Security di-consult bila menyentuh auth/data.
3. **Accepted** — Board menyetujui; status dokumen di-update, index di-regenerate, follow-up actions dicatat di ADR.
4. **Superseded/Deprecated** — ADR baru yang menggantikan wajib merujuk ADR lama; ADR lama tidak dihapus.

Perubahan business rule tanpa ADR dilarang (lihat aturan repo); deviasi standar tanpa ADR lewat `reviews/EXCEPTION_REQUEST.md` hanya untuk waiver sementara ber-tenggat.

## Architecture Review
Review process lives under `reviews/` (not a separate top-level folder):
- `reviews/REVIEW_CHECKLIST.md`
- `reviews/ARCHITECTURE_REVIEW_FORM.md`
- `reviews/EXCEPTION_REQUEST.md`

## Template Sections
1. Governance Principles
2. Roles & RACI
3. Architecture Review Process
4. Decision Rights
5. Quality Gates (by phase)
6. Exception & Waiver Process
7. Metrics (governance health)
8. Meeting Cadence

## Boundary Note
- Governance = proses dan akuntabilitas
- ADR = keputusan arsitektur individual (folder 05)
- Project Decisions = keputusan non-arsitektur (folder 27)

## Naming
`ECMP_Architecture_Governance_vX.Y.md|docx`  
`ECMP_RACI_Matrix_vX.Y.xlsx`

## Related
- `../05 Architecture Decision Records`
- `../00 Repository Guide`
- `../17 Compliance`
- `../24 Templates`
- `../27 Project Decisions`
