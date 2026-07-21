# 21 Technical Standards


| Field | Value |
|---|---|
| ID | STD-000 |
| Version | 0.1 |
| Owner | Tech Lead |
| Reviewer | Solution Architect |
| Approver | Architecture Board |
| Status | 🟢 Approved (baseline) |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Standar teknologi implementasi ECMP. Dipisah dari Solution Architecture agar menjadi acuan teknis yang stabil.

## Owner
- Document Owner: Tech Lead / Platform Lead
- Reviewers: Solution Architect, Security, DevOps

## Status
Approved baseline — `ECMP_Technical_Standards_v0.1.md` (TS-001) berisi standar yang diturunkan dari implementasi aktual + ADR Accepted.

## Contents
- `ECMP_Technical_Standards_v0.1.md` (TS-001)
- `ECMP_Observability_Standard_v0.1.md` (TS-OBS-001 — 🟡 Draft; kontrak logging/correlation-id/metrik yang diaktifkan gate G1; aturan PII berlaku sekarang)

## Planned Standards
- [x] Python Standard (TS-001 §1)
- [x] FastAPI Standard (TS-001 §1)
- [ ] TypeScript Standard (belum ada kode frontend — menunggu frontend dimulai)
- [ ] React Standard (idem)
- [x] Database Standard (TS-001 §5)
- [x] Docker Standard (TS-001 §7)
- [x] API Error Model Standard (TS-001 §2.2)
- [x] Logging / Observability Standard (TS-001 §6 + TS-OBS-001 — structured logging = backlog G1, aturan PII berlaku sekarang)

## Boundary
- Technical Standards = “how we implement with stack X”
- Engineering Handbook (`22`) = “how we collaborate day-to-day”
- Solution Architecture (`04`) = “what the system looks like”

## Naming
`ECMP_Tech_Standard_<Topic>_vX.Y.md`
