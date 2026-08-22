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
| **DEC-020** | Complaint Implementation SoT & Namespace Remapping | **Accepted** (coexistence Foundation **berakhir setelah M-026**) | Dual SoT historis; runtime Mode A = `/api/v1/cm`; Foundation HTTP retired DEC-026 |
| DEC-020 *(file collision)* | Lab Auth: local JWT now, SSO later | Accepted (ops) | Lab auth phasing — **same ID as SoT remapping**; see collision register |
| DEC-021 *(org O-06)* | Organization Hierarchy Descendant Scope (O-06) | **Proposed** | No silent descendant AuthZ; Mode B not unlocked |
| DEC-021 *(G2 Mode A)* | G2 Mini-Gate Mode A | **Accepted (Mode A lab)** | G2 exit Mode A — **same ID as O-06**; see collision register |
| DEC-022 | Org Restructure / Orphan Remediation (O-07) | **Proposed** | Retain + fail-closed interim; Mode B not unlocked |
| **DEC-023** | Pintu auth: sekarang vs nanti (Mode A → B handoff) | **Accepted (ops)** | Fleksibel di adapter; larangan mall palsu; Mode B tetap CLOSED |
| **DEC-024** | Case List Visibility Matrix Mode A | **Accepted (lab)** | Visibility list Case; bukan Retirement DEC |
| **DEC-025** | CM Target Single SoT + Mode A Complaint Closure | 🟢 **Accepted** (2026-08-13) | Target CM Single SoT; BR-009 auto-close; M-025-1…6 executed; cutover = DEC-026 (executed) |
| **DEC-026** | Foundation `/api/v1/complaints` namespace retirement | 🟢 **Accepted with Conditions** (2026-08-13) | **M-026-1…3 executed**: FE redirect, HTTP unmount, DROP `complaints*` (H1 / Alembic `0072`); CA BC bukan objek retire |
| **DEC-027** | Label persona CRO / Staff KaSatPel / KaSatPel + Viewer ALL | 🟢 **Accepted (lab)** (2026-08-20) | Kode IAM tidak diganti; Viewer baca-semua; bukan Mode B |
| **DEC-028** | Format nomor Case/pengaduan (BQ-004 opsi C) + unit tujuan eskalasi Pusat | 🟢 **Accepted (lab)** (2026-08-22) | Independensi BQ-004 tetap; format `TAB-2608-0001` / `CMTAB-2608-0001`; Pusat tetapkan jam+unit tujuan dan mengabari WP |
| **DEC-MODEA-B2-001** | Mode A Delivery Baseline BQ Lock (CAP-008) | **Accepted** | BQ-002…014 LOCKED; Residual BQ ZERO; FRD Batch-2 prerequisite READY |
| **ECMP-MODEA-INT-001** | Pengaduan Internal Journey Contract | **Accepted (Mode A UI)** | `/internal/*` copy + gerbang tutup; **bukan** Dual-SoT WP / bukan ADR |

> DEC-020 (SoT remapping) closes **OQ-CM-B1-001**. It does **not** Accept ADR-014/015, unlock Mode B, or real-customer production.
> **DEC-MODEA-B2-001** locks Batch-2 Mode A Case Management BQs and registers capability **CAP-008** (former working ID CAP-02 retired). Pack: `../18 Architecture Governance/reviews/ECMP_DEC_ModeA_Delivery_Baseline_BQ_Lock_Pack_v1.0.md`.
> DEC-021 (O-06) / DEC-022 are **Proposed** only — interim fail-closed rules apply until Accepted.
> **DEC-023** clarifies Mode A login vs future Enterprise handoff; it does **not** unlock Mode B.
> **DEC-025** is **Accepted** (2026-08-13) — target CM Single SoT + BR-009 Mode A closure/status. Slices M-025-1…6 executed. Runtime SoT = `/api/v1/cm`. CAP-008 tetap CLOSED.
> **DEC-026** is **Accepted with Conditions** (2026-08-13) — **M-026-1…3 executed** (FE redirect, unmount `/api/v1/complaints`, DROP `complaints*` H1). DEC-020 tubuh tidak di-rewrite. CA BC ticket-nested tetap. Mode B remains CLOSED.
> **DEC-027** is **Accepted (lab)** (2026-08-20) — label persona + Viewer ALL; role code tidak diganti.
> **DEC-028** is **Accepted (lab)** (2026-08-22) — BQ-004 format opsi C + HQ destination unit; independensi nomor Case tidak dibuka. Mode B remains CLOSED.
> **ID collision (P0 governance):** two files share `DEC-020` and two share `DEC-021`. Do **not** renumber without Board/PMO decision. Register: `../deploy/evidence/DEC_ID_Collision_Register_20260801.md`.

## Structure (konvensi aktual — flat)
- `DEC-*.md` di root folder ini — decision records bernomor urut (DEC-001 dst.)
- `OPEN_QUESTIONS.md` — daftar open questions (OQ-xxx) beserta statusnya
- `archive/` — artefak historis yang superseded (lihat `archive/README.md`, DEC-ARCH-001):
  laporan discovery Sprint-0, review senior engineer Sprint-0, dan `Penilaian_ECMP.docx`

> Subfolder terpisah (accepted/rejected/workshops/meeting-notes) tidak dipakai; semua DEC hidup flat di root folder dengan status di metadata masing-masing.

## Template
Gunakan `../24 Templates/DECISION_TEMPLATE.md`
