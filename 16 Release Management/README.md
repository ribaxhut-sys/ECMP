# 16 Release Management


| Field | Value |
|---|---|
| ID | REL-000 |
| Version | 0.1 |
| Owner | Release Manager |
| Reviewer | QA / Ops |
| Approver | PMO |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Proses release ECMP: perencanaan, checklist, approval, komunikasi, dan post-release validation.

## Owner
- Document Owner: Release Manager / PMO
- Reviewers: QA Lead, Ops, Product Owners, Architecture

## Status
Approved baseline — `ECMP_Release_Management_v0.1.md` (REL-001): unit rilis = slice per gate.

## Contents
- `ECMP_Release_Management_v0.1.md` (REL-001)

## Minimum Contents (v1)
- [x] Release cadence & freeze policy — rilis per slice/gate, bukan kalender (REL-001 pembuka)
- [x] Release checklist — Go/No-Go 5 butir (REL-001 §3)
- [x] Go/No-Go criteria (REL-001 §3 — CI hijau, katalog sinkron, sign-off Tech Lead+SA per DEC-002)
- [ ] Stakeholder communication template (belum ada konsumen eksternal; aktif saat environment bersama ada)
- [x] Rollback decision criteria (REL-001 §5 → DEP-001 §4)
- [ ] Post-release verification (menunggu environment bersama pertama)
- [x] Release notes/changelog — changelog di deskripsi PR (REL-001 §4)

## Template Sections
1. Release Objectives
2. Scope (features/fixes)
3. Risk Assessment
4. Test Evidence
5. Deployment Plan
6. Rollback Plan
7. Approvals
8. Communication Plan
9. Post-Release Review

## Naming
`ECMP_Release_<YYYYMMDD|Version>_Plan_vX.Y.docx`  
`ECMP_Release_Notes_<Version>.md`

## Related
- `../13 Test Strategy`
- `../14 Deployment Standards`
- `../15 Operations Runbook`
