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

## Structure (konvensi aktual — flat)
- `DEC-*.md` di root folder ini — decision records bernomor urut (DEC-001 dst.)
- `OPEN_QUESTIONS.md` — daftar open questions (OQ-xxx) beserta statusnya
- `archive/` — artefak historis yang superseded (lihat `archive/README.md`, DEC-ARCH-001):
  laporan discovery Sprint-0, review senior engineer Sprint-0, dan `Penilaian_ECMP.docx`

> Subfolder terpisah (accepted/rejected/workshops/meeting-notes) tidak dipakai; semua DEC hidup flat di root folder dengan status di metadata masing-masing.

## Template
Gunakan `../24 Templates/DECISION_TEMPLATE.md`
