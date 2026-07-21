# 10 Security and Access Standards


| Field | Value |
|---|---|
| ID | SEC-000 |
| Version | 0.1 |
| Owner | Security Architect |
| Reviewer | Compliance |
| Approver | Architecture Board |
| Status | 🟢 Approved (baseline) |
| Last Review | 2026-07-21 |
| Next Review | 2026-10-21 |

## Purpose
Standar keamanan dan akses ECMP: autentikasi, otorisasi, role matrix, data protection, audit.

## Owner
- Document Owner: Security Architect / InfoSec
- Reviewers: Solution Architect, Compliance, Ops

## Status
Approved — baseline Sprint-01 (diperluas per gate)

## Documents
- [`ECMP_Security_Standards_v0.1.md`](./ECMP_Security_Standards_v0.1.md)
- [`ECMP_Role_Access_Matrix_v0.1.md`](./ECMP_Role_Access_Matrix_v0.1.md) — v0.2: + bagian Planned Sprint-02
- [`ECMP_AuthN_Limitations_Register_v0.1.md`](./ECMP_AuthN_Limitations_Register_v0.1.md)
- [`ECMP_Threat_Model_v0.1.md`](./ECMP_Threat_Model_v0.1.md) — SEC-TM-001, 🟡 Draft (STRIDE scope slice)

## Minimum Contents (v1)
- [x] Authentication standard — ADR-007 + Security Standards §2
- [x] Authorization model (RBAC / org-scoped) — §2–3; org-scope tercatat sebagai limitation L-3 (target G1)
- [x] Role & Access Matrix — `ECMP_Role_Access_Matrix_v0.1.md`
- [x] PII handling standard — Security Standards §4 (baseline; detail di 17 Compliance)
- [x] Audit logging requirements — Security Standards §5 (BR-008 / FR-001c)
- [x] Secure SDLC checklist — Security Standards §6 (backend CI wajib)
- [x] Secrets & credential management — Security Standards §7 + `.env.example`
- [x] Threat model (STRIDE, scope slice) — `ECMP_Threat_Model_v0.1.md` (🟡 Draft; pentest = backlog dengan trigger sebelum shared UAT)

## Template Sections
1. Security Principles
2. Identity & Access Management
3. Role Matrix
4. Data Classification & Protection
5. Logging & Monitoring
6. Secure Development Controls
7. Incident Response (security)
8. Compliance Mapping

## Naming
`ECMP_Security_Standards_vX.Y.docx`  
`ECMP_Role_Access_Matrix_vX.Y.xlsx`

## Related
- `../04 Solution Architecture`
- `../17 Compliance`
- `../18 Architecture Governance`
