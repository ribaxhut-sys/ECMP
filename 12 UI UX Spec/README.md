# 12 UI UX Spec


| Field | Value |
|---|---|
| ID | UX-000 |
| Version | 0.1 |
| Owner | UX Lead |
| Reviewer | BA / Frontend Lead |
| Approver | Business Owner |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Spesifikasi pengalaman pengguna ECMP: journey, screen inventory, wireframe/mockup references, UX rules.

## Owner
- Document Owner: UX Lead / Product Designer
- Reviewers: BA Lead, Domain POs, Frontend Lead

## Status
Draft

## Current Artifacts
- [x] `ECMP_Personas_And_Journeys_v0.1.md` (UX-001 — persona CS Agent/Supervisor/Administrator; journey Sprint-01 API-first + target G1)
- [x] `ECMP_Screen_Spec_Case_Detail_Workspace_v0.1.md` (UX-SCR-001 — Sprint-04, first product screen spec per ADR-011 trigger; stack locked by ADR-013, Approved and ready for Cursor implementation)

## Minimum Contents (v1)
- [x] Persona & key journeys (`ECMP_Personas_And_Journeys_v0.1.md`)
- [~] Screen inventory by role/module — first screen spec landed (Case Detail Workspace); inventory still incomplete (queue/list, create-case, dashboard screens not yet specified)
- [ ] Wireframe / prototype links
- [ ] UX writing guidelines (status labels, actions)
- [ ] Accessibility baseline
- [ ] UI states (loading/empty/error/permission denied)

## Template Sections (per screen)
1. Screen ID & Name
2. Actor / Role
3. Purpose
4. Entry points
5. Fields & actions
6. Validations
7. Empty/error states
8. Permissions
9. Related FR / BR

## Naming
`ECMP_UIUX_<Module>_vX.Y.docx`  
Prototype links may be stored as markdown references.

## Related
- `../03 Functional Requirements`
- `../10 Security and Access Standards`
