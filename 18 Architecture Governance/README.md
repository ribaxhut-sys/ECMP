# 18 Architecture Governance


| Field | Value |
|---|---|
| ID | GOV-000 |
| Version | 0.1 |
| Owner | Architecture Board Chair |
| Reviewer | PMO |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-30 |
| Next Review | 2027-01-21 |

## Purpose
Tata kelola arsitektur ECMP: proses review, RACI, quality gates, dan pengelolaan ADR/standards.

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

Canonical ADR lifecycle statuses (Architecture Board — PROGRAM-ADR-002 BR-001):

`PROPOSED` → `ACCEPTED` → `SUPERSEDED` / `DEPRECATED`

Also recognized: **`REJECTED`** (proposal not adopted; retained for history; not deleted).

Official set (exact): **PROPOSED**, **ACCEPTED**, **SUPERSEDED**, **DEPRECATED**, **REJECTED**.

Jalur operasional:

1. **PROPOSED** — SA/Tech Lead menulis ADR dari template (`../05 Architecture Decision Records/ADR-TEMPLATE.md`) dengan opsi + trade-off.
2. **Review** — dibahas di Architecture Board (form `reviews/ARCHITECTURE_REVIEW_FORM.md`, checklist `reviews/REVIEW_CHECKLIST.md`); Security di-consult bila menyentuh auth/data. *Review is a process step, not an ADR lifecycle status.*
3. **ACCEPTED** — Board menyetujui; status dokumen di-update, index di-regenerate, follow-up actions dicatat di ADR.
4. **REJECTED** — Board menolak proposal; ADR tetap di repository dengan status Rejected dan alasan singkat.
5. **SUPERSEDED / DEPRECATED** — ADR baru yang menggantikan wajib merujuk ADR lama; ADR lama tidak dihapus.

Document bodies may write Title Case (`Proposed`, `Accepted`, …); meaning is identical to the official set above.

**Badge mapping:** tabel metadata repo memakai badge di `../00 Repository Guide/STATUS_BADGES.md` (lifecycle `Accepted` dipetakan ke badge `🟢 Approved`). Badan ADR (`ADR Status:`) = otoritatif untuk lifecycle.

Perubahan business rule tanpa ADR dilarang (lihat aturan repo); deviasi standar tanpa ADR lewat `reviews/EXCEPTION_REQUEST.md` hanya untuk waiver sementara ber-tenggat.

## Architecture Documents Lifecycle

Canonical lifecycle for architecture documents (non-ADR) — Architecture Board PROGRAM-ADR-002 BR-002:

**DRAFT** → **REVIEW** → **BASELINE** → **ARCHIVED**

Official set (exact): **DRAFT**, **REVIEW**, **BASELINE**, **ARCHIVED**.

Applies to architecture artifacts such as FE-ARCH / FE-STD and other architecture baselines under Architecture Board control. Does **not** replace the ADR lifecycle above.

**Badge mapping:** `DRAFT` → `🟡 Draft`; `REVIEW` → `🔵 Under Review`; `BASELINE` → `🟢 Approved` (or `🟢 BASELINE`); `ARCHIVED` → `🔴 Deprecated` / archived pointer.

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
- CAP-006 evaluation mechanism: [`../05 Architecture Decision Records/ADR-CAP006-001_Evaluation_Mechanism.md`](../05%20Architecture%20Decision%20Records/ADR-CAP006-001_Evaluation_Mechanism.md) (**Accepted** v2.0 — Hybrid). Time Source: [`../05 Architecture Decision Records/ARC-CAP006-001_Time_Source.md`](../05%20Architecture%20Decision%20Records/ARC-CAP006-001_Time_Source.md) (**Accepted** requirement concept). Runtime Architecture: [`../05 Architecture Decision Records/ARC-CAP006-002_Runtime_Architecture.md`](../05%20Architecture%20Decision%20Records/ARC-CAP006-002_Runtime_Architecture.md) (B2-21). B2-22 Non-Invent Gate: **ADDITIONAL ARCHITECTURE REQUIRED**. B2-23: [`../deploy/evidence/B2-23_CAP-006_Time_Source_Fulfillment_Pattern_Decision_20260801.md`](../deploy/evidence/B2-23_CAP-006_Time_Source_Fulfillment_Pattern_Decision_20260801.md) — **FULFILLMENT PATTERN NOT SPECIFIED**.
- `../00 Repository Guide`
- `../17 Compliance`
- `../24 Templates`
- `../27 Project Decisions`
- [`ECMP_CONSTITUTION_001_Complaint_Management_Module_Constitution_v1.1.md`](./ECMP_CONSTITUTION_001_Complaint_Management_Module_Constitution_v1.1.md) — **LOCKED** Operating Constitution / Mission / North Star (subordinat Board; Mode B CLOSED)
- [`ECMP_MASTER_PROMPT_001_Complaint_Management_Module_Engineering_Assistant_v1.1.md`](./ECMP_MASTER_PROMPT_001_Complaint_Management_Module_Engineering_Assistant_v1.1.md) — **LOCKED** runtime instruction (turunan CONSTITUTION-001)
- [`ECMP_PROGRAM_ADR_002_Board_Resolutions_v1.0.md`](./ECMP_PROGRAM_ADR_002_Board_Resolutions_v1.0.md) — PROGRAM-ADR-002 BR-001…BR-008 traceability
- [`ECMP_PROGRAM_BOARD_004_Architecture_Board_Resolution_v1.0.md`](./ECMP_PROGRAM_BOARD_004_Architecture_Board_Resolution_v1.0.md) — **Recorded** — BR-009 / BR-010 Accept With Conditions (ADR-014/015); Mode B CLOSED (C-7)
- [`ECMP_PROGRAM_BOARD_005_Architecture_Board_Review_v1.0.md`](./ECMP_PROGRAM_BOARD_005_Architecture_Board_Review_v1.0.md) — **Recorded** — Board Review CONVENED; outcome **Ready for Resolution** (resolved by BOARD-006)
- [`ECMP_PROGRAM_BOARD_005_Architecture_Board_Review_Pending_v1.0.md`](./ECMP_PROGRAM_BOARD_005_Architecture_Board_Review_Pending_v1.0.md) — **Superseded** — historical pending stub
- [`ECMP_PROGRAM_BOARD_006_Architecture_Board_Resolution_v1.0.md`](./ECMP_PROGRAM_BOARD_006_Architecture_Board_Resolution_v1.0.md) — **Recorded** — BR-011 / BR-012 / BR-013 Accept With Conditions (ADR-016/017/018); Mode B CLOSED (C-B6-1)
- [`ECMP_PROGRAM_BOARD_006_Architecture_Board_Resolution_Pending_v1.0.md`](./ECMP_PROGRAM_BOARD_006_Architecture_Board_Resolution_Pending_v1.0.md) — **Superseded** — historical pending stub
- [`ECMP_PROGRAM_BOARD_007_ADR007_012_Relationship_Disposition_Brief_v0.1.md`](./ECMP_PROGRAM_BOARD_007_ADR007_012_Relationship_Disposition_Brief_v0.1.md) — **Draft** — closes REC-01 / F-7 / C-B6-6 packaging (no Mode B unlock; Board decision pending)
- [`ECMP_PROGRAM_BOARD_008_EA_TARGET_PLATFORM_Draft_Pack_v0.1.md`](./ECMP_PROGRAM_BOARD_008_EA_TARGET_PLATFORM_Draft_Pack_v0.1.md) — **Draft** — Board intake: EA-TARGET-CM-001 + EA-PLATFORM-001 + HOST Gate; **not** implementation tickets; Mode B CLOSED; companion DTM-001
- [`ECMP_PROGRAM_ADR_004_Board_Readiness_Revision_Package_v1.0.md`](./ECMP_PROGRAM_ADR_004_Board_Readiness_Revision_Package_v1.0.md) — historical Board Readiness package (ADR-014 v1.4 / ADR-015 v1.3)
- [`ECMP_PROGRAM_ENTERPRISE_001_PHASE0_Alignment_Findings_v1.0.md`](./ECMP_PROGRAM_ENTERPRISE_001_PHASE0_Alignment_Findings_v1.0.md) — historical PHASE-0
- [`ECMP_PROGRAM_ENTERPRISE_001_PHASE1A_Authoring_Specification_v1.0.md`](./ECMP_PROGRAM_ENTERPRISE_001_PHASE1A_Authoring_Specification_v1.0.md) — historical PHASE-1A
- [`ECMP_PROGRAM_DOC_001_Documentation_Sync_Record_v1.0.md`](./ECMP_PROGRAM_DOC_001_Documentation_Sync_Record_v1.0.md) — DEC-020 documentation sync
- [`ECMP_PROGRAM_IMPLEMENTATION_001_Implementation_Authorization_Posture_v1.0.md`](./ECMP_PROGRAM_IMPLEMENTATION_001_Implementation_Authorization_Posture_v1.0.md) — coexistence / cutover-by-Decision posture
- [`ECMP_GOVERNANCE_BASELINE_REFRESH_REPORT_v1.0.md`](./ECMP_GOVERNANCE_BASELINE_REFRESH_REPORT_v1.0.md) — PROGRAM-GOVERNANCE-001 hygiene report
- [`ECMP_PROGRAM_SAFE_NEXT_001_Prioritized_Safe_Work_Queue_v1.0.md`](./ECMP_PROGRAM_SAFE_NEXT_001_Prioritized_Safe_Work_Queue_v1.0.md) — post–BOARD-006 safe work priority (P1–P4)
- [`ECMP_PROGRAM_ORG_GAP_DELIVERY_PLAN_v0.1.md`](./ECMP_PROGRAM_ORG_GAP_DELIVERY_PLAN_v0.1.md) — org-gap delivery plan Draft (C-B6-3; no Mode B unlock)
- [`ECMP_PROGRAM_EP_BILATERAL_PROFILE_REVIEW_PACK_v0.1.md`](./ECMP_PROGRAM_EP_BILATERAL_PROFILE_REVIEW_PACK_v0.1.md) — EP bilateral review pack (awaiting countersign)
- [`ECMP_PROGRAM_MODE_A_NEXT_WORK_PRIORITY_v0.1.md`](./ECMP_PROGRAM_MODE_A_NEXT_WORK_PRIORITY_v0.1.md) — Mode A engineering priority note
- [`ECMP_PROGRAM_MODE_A_M3C_Module_Lab_COMPLETE_Evidence_Pack_v1.0.md`](./ECMP_PROGRAM_MODE_A_M3C_Module_Lab_COMPLETE_Evidence_Pack_v1.0.md) — Mode A Batch-1 **lab COMPLETE** evidence (GOV-MODEA-M3C-001; not Mode B / real-customer prod)
- [`ECMP_PROGRAM_CAP008_000_Program_Closure_Index_v1.0.md`](./ECMP_PROGRAM_CAP008_000_Program_Closure_Index_v1.0.md) — **CAP-008 Mode A PROGRAM CLOSED** (GOV-CAP008-CLOSE-*; lab RC + SoT; not Production / Mode B)
- B2-07 Repository & Capability Alignment — [`../deploy/evidence/B2-07_Repository_Capability_Alignment_20260801.md`](../deploy/evidence/B2-07_Repository_Capability_Alignment_20260801.md) (GOV-B2-07-ALIGN-001; metadata sync only)
- B2-08 Capability Portfolio Rationalization — [`../deploy/evidence/B2-08_Capability_Portfolio_Rationalization_20260801.md`](../deploy/evidence/B2-08_Capability_Portfolio_Rationalization_20260801.md) (GOV-B2-08-PORTFOLIO-001; dispositions + roadmap; no code)
- B2-09 Queue Architecture Rationalization — [`../deploy/evidence/B2-09_Queue_Architecture_Rationalization_20260801.md`](../deploy/evidence/B2-09_Queue_Architecture_Rationalization_20260801.md) (GOV-B2-09-QUEUE-001; CAP-007 SoT = API-040; multi-lane KEEP)
- B2-10 CAP-007 Definition of Ready — [`../deploy/evidence/B2-10_CAP-007_Definition_of_Ready_20260801.md`](../deploy/evidence/B2-10_CAP-007_Definition_of_Ready_20260801.md) (GOV-B2-10-DOR-001; **NOT READY** — Continue Draft)
- B2-11 CAP-007 Business Decision Closure — [`../deploy/evidence/B2-11_CAP-007_Business_Decision_Closure_20260801.md`](../deploy/evidence/B2-11_CAP-007_Business_Decision_Closure_20260801.md) (GOV-B2-11-BQ-001 / DEC-CAP007-BQ-001; **BUSINESS DECISION READY**)
- B2-12 CAP-007 FRD Lock & Governance Closure — [`../deploy/evidence/B2-12_CAP-007_FRD_Lock_Governance_Closure_20260801.md`](../deploy/evidence/B2-12_CAP-007_FRD_Lock_Governance_Closure_20260801.md) (GOV-B2-12-LOCK-001; FRD **LOCKED**; eng **NOT READY**)
- B2-13 API-040 Normative Closure — [`../deploy/evidence/B2-13_API-040_Normative_Closure_20260801.md`](../deploy/evidence/B2-13_API-040_Normative_Closure_20260801.md) (GOV-B2-13-API040-001; API-040 **NORMATIVE** 1.0.0)
- [`ECMP_PROGRAM_ENTERPRISE_PROFILES_001_Subordinate_Profiles_Draft_Pack_v0.1.md`](./ECMP_PROGRAM_ENTERPRISE_PROFILES_001_Subordinate_Profiles_Draft_Pack_v0.1.md) — Draft pack: Binding / Entitlement / Org-Sync profiles (Mode B CLOSED)
- [`ECMP_PROGRAM_MODE_B_ORG_GAP_PREREQUISITE_v1.0.md`](./ECMP_PROGRAM_MODE_B_ORG_GAP_PREREQUISITE_v1.0.md) — audit **K-7**: three-level org gap = Mode B unlock prerequisite
- [`ECMP_PROGRAM_AUDIT_K5_FailClosed_Subordination_v1.0.md`](./ECMP_PROGRAM_AUDIT_K5_FailClosed_Subordination_v1.0.md) — audit **K-5**: ADR-016/017/018 fail-closed subordination (Accepted with Conditions under BOARD-006)
