# 27 Project Decisions


| Field | Value |
|---|---|
| ID | DEC-000 |
| Version | 0.2 |
| Owner | PMO |
| Reviewer | Stakeholders |
| Approver | Business Owner |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Menyimpan keputusan proyek non-arsitektur, hasil workshop, open questions, dan catatan keputusan operasional.

## Owner
- Document Owner: PMO / Product Owner
- Reviewers: Stakeholders terkait

## Status
Draft

## What Belongs Here
- Meeting notes (keputusan)
- Workshop outcomes
- Open questions
- Accepted project decisions (non-ADR)
- Rejected ideas (dengan alasan)

## What Does NOT Belong Here
- Architecture decisions → `05 Architecture Decision Records`
- Architecture review forms → `18 Architecture Governance/reviews`

## Implementation Baseline (active Project Decisions)

| DEC | Title | Status | Binding for |
|---|---|---|---|
| DEC-019 | Engineering Foundation Canonical Trees | Accepted | `backend/` + `frontend/` production trees |
| **DEC-020** | Complaint Implementation SoT & Namespace Remapping | **Accepted** | Dual SoT; `/api/v1/cm` Aggregate vs `/api/v1/complaints` foundation; coexistence; cutover policy |
| DEC-020 *(file collision)* | Lab Auth: local JWT now, SSO later | Accepted (ops) | Lab auth phasing — **same ID as SoT remapping**; see collision register |
| DEC-021 *(org O-06)* | Organization Hierarchy Descendant Scope (O-06) | **Proposed** | No silent descendant AuthZ; Mode B not unlocked |
| DEC-021 *(G2 Mode A)* | G2 Mini-Gate Mode A | **Accepted (Mode A lab)** | G2 exit Mode A — **same ID as O-06**; see collision register |
| DEC-022 | Org Restructure / Orphan Remediation (O-07) | **Proposed** | Retain + fail-closed interim; Mode B not unlocked |
| **DEC-MODEA-B2-001** | Mode A Delivery Baseline BQ Lock (CAP-008) | **Accepted** | BQ-002…014 LOCKED; Residual BQ ZERO; FRD Batch-2 prerequisite READY |

> DEC-020 (SoT remapping) closes **OQ-CM-B1-001**. It does **not** Accept ADR-014/015, unlock Mode B, or real-customer production.
> **DEC-MODEA-B2-001** locks Batch-2 Mode A Case Management BQs and registers capability **CAP-008** (former working ID CAP-02 retired). Pack: `../18 Architecture Governance/reviews/ECMP_DEC_ModeA_Delivery_Baseline_BQ_Lock_Pack_v1.0.md`.
> DEC-021 (O-06) / DEC-022 are **Proposed** only — interim fail-closed rules apply until Accepted.
> **ID collision (P0 governance):** two files share `DEC-020` and two share `DEC-021`. Do **not** renumber without Board/PMO decision. Register: `../deploy/evidence/DEC_ID_Collision_Register_20260801.md`.

## Structure (konvensi aktual — flat)
- `DEC-*.md` di root folder ini — decision records bernomor urut (DEC-001 dst.)
- `OPEN_QUESTIONS.md` — daftar open questions (OQ-xxx) beserta statusnya
- `archive/` — artefak historis yang superseded (lihat `archive/README.md`, DEC-ARCH-001):
  laporan discovery Sprint-0, review senior engineer Sprint-0, dan `Penilaian_ECMP.docx`

> Subfolder terpisah (accepted/rejected/workshops/meeting-notes) tidak dipakai; semua DEC hidup flat di root folder dengan status di metadata masing-masing.

## Template
Gunakan `../24 Templates/DECISION_TEMPLATE.md`
