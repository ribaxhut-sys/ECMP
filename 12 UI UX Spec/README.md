# 12 UI UX Spec


| Field | Value |
|---|---|
| ID | UX-000 |
| Version | 0.2 |
| Owner | UX Lead |
| Reviewer | BA / Frontend Lead |
| Approver | Business Owner |
| Status | 🟡 Draft |
| Last Review | 2026-08-05 |
| Next Review | 2027-02-05 |
| Revision note | UX-001 Complete Discovery: indeks diarahkan ke paket `docs/ux/` (PDS-001…UX-DISC-001). Screen inventory discovery lengkap di UX-DISC-001 §6; wireframe belum digambar. |

## Purpose
Spesifikasi pengalaman pengguna ECMP Complaint Management Module (Mode A): persona, journey, IA/navigasi, inventori layar, rencana wireframe/prototype, gap analysis.

## Owner
- Document Owner: UX Lead / Product Designer
- Reviewers: BA Lead, Domain POs, Frontend Lead

## Status
**UX Discovery: COMPLETE.** **WF-001 Release 1 LF: COMPLETE (Draft)** — lihat `docs/ux/WF-001-R1-Wireframe-Package.md`. Berikutnya: implementasi FE R1 atau wireframe R2.

## Canonical UX package (`docs/ux/`)

| ID | Artefak | Peran |
|---|---|---|
| UX-FOUNDATION-000 | Complaint Module UX Foundation | Payung baseline |
| PDS-001 | Persona Design Specification | Persona SoT (3 operasional) |
| PWDM-001 | Persona Workflow & Decision Model | Journey / decision SoT |
| IA-001 | Information Architecture | IA / zona / destinasi SoT |
| NAV-001 | Navigation Architecture | Navigasi SoT (+ 4 lapisan) |
| WF-000 | Wireframe Constitution | Aturan layout |
| WF-PLAN-001 | Wireframe Roadmap & Backlog | 21 item WF-001-* |
| **UX-DISC-001** | **Complete UX Discovery** | **Paket one-pass discovery** |
| **WF-001-R1** | **Release 1 Wireframe Package** | **LF specs R1 + nav map + components + FE batches + readiness** |

## Legacy / complementary artifacts (folder ini)

- [x] `ECMP_Personas_And_Journeys_v0.1.md` — journey service-level; pertanyaan “siapa & tujuan” → **PDS-001**
- [x] `ECMP_Screen_Spec_Case_Detail_Workspace_v0.1.md` — screen spec historis Approved; **wajib direkonsiliasi** ke zona IA + persona Complaint Officer sebelum jadi SoT implementasi (lihat UX-DISC-001 UX-B2)

## Discovery checklist (UX-001)

- [x] UX Discovery Summary
- [x] User Personas (reuse PDS-001)
- [x] Business Journey (Customer + Officer + Supervisor + Manager)
- [x] Information Architecture (reuse IA-001)
- [x] Navigation Structure (NAV-001 + empat lapisan)
- [x] Screen Inventory (UX-DISC-001 §6)
- [x] Workspace Inventory (UX-DISC-001 §7)
- [x] Screen Flow Login→Closure (UX-DISC-001 §8)
- [x] Wireframe Planning (reuse WF-PLAN-001)
- [x] Prototype Planning (UX-DISC-001 §10)
- [x] Frontend Redesign Roadmap (UX-DISC-001 §11)
- [x] UX Gap Analysis (UX-DISC-001 §12)
- [x] Implementation Readiness (UX-DISC-001 §13)
- [ ] Wireframe / prototype drawings — **out of discovery; next phase**
- [ ] UX writing guidelines & accessibility baseline — blocker implementasi polish (UX-B3), bukan blocker wireframe P0

## Naming
Artefak kanonik memakai ID `docs/ux/<ID>-….md`.  
Prototype links may be stored as markdown references setelah fase prototype.

## Related
- `../docs/ux/UX-DISC-001-Complete-UX-Discovery.md`
- `../docs/governance/BC-000-Business-Constitution.md` … `BC-003`
- `../docs/business/BW-000-Business-Workflow-Constitution.md`
- `../03 Functional Requirements`
