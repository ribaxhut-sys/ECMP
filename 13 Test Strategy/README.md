# 13 Test Strategy


| Field | Value |
|---|---|
| ID | TST-000 |
| Version | 0.1 |
| Owner | QA Lead |
| Reviewer | BA / Tech Leads |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Strategi pengujian ECMP: scope, jenis test, entry/exit criteria, environments, dan quality gates.

## Owner
- Document Owner: QA Lead
- Reviewers: BA Lead, Tech Leads, Ops

## Status
Approved baseline — `ECMP_Test_Strategy_v0.1.md` (TST-001) berisi strategi aktual fase slice (Sprint-01 → G1).

## Contents
- `ECMP_Test_Strategy_v0.1.md` (TST-001) — 🟢 Approved (baseline Sprint-01)
- `ECMP_Test_Case_Catalog_v0.1.md` (TC-CAT-001) — 🟡 Draft — spesifikasi formal per TC (Implemented + Planned) selaras traceability
- `ECMP_UAT_Plan_v0.1.md` (UAT-001) — 🟡 Draft — rencana UAT ter-gate (prasyarat environment/auth, persona, skenario subset TC)

## Minimum Contents (v1)
- [x] Test objectives & scope (TST-001 §1)
- [x] Test types — unit/API/contract/migration aktif; UI/performance/security = backlog dengan trigger (TST-001 §1, §6)
- [x] Traceability to FR/BR — mapping TC → tes nyata (TST-001 §2)
- [x] Entry & exit criteria per gate G0/G1 (TST-001 §3)
- [x] Defect severity model — untuk konteks UAT (UAT-001 §5); untuk dev harian tetap: defect langsung jadi PR
- [x] Test data strategy (TST-001 §5)
- [x] Environment usage (TST-001 §5)
- [x] UAT approach — rencana ter-gate di UAT-001 (eksekusi menunggu keputusan platform SIT/UAT + fase target ADR-007)

## Template Sections
1. Scope & Objectives
2. Test Levels & Types
3. Roles & Responsibilities
4. Entry / Exit Criteria
5. Traceability Matrix approach
6. Tools
7. Risks & Mitigations
8. Schedule assumptions

## Naming
`ECMP_Test_Strategy_vX.Y.md`

## Related
- `../03 Functional Requirements`
- `../14 Deployment Standards`
- `../16 Release Management`
