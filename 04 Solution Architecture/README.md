# 04 Solution Architecture


| Field | Value |
|---|---|
| ID | SA-000 |
| Version | 0.1 |
| Owner | Solution Architect |
| Reviewer | Security / Tech Leads |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Desain solusi teknis ECMP: architecture views, komponen, deployment, integrasi, dan NFR.

## Owner
- Document Owner: Solution Architect
- Reviewers: Tech Leads, Security, Ops, BA Lead

## Status
Draft — v1.0 tersedia, beberapa keputusan teknis masih Open Decision

## Documents
- [`ECMP_Solution_Architecture_v1.0.md`](./ECMP_Solution_Architecture_v1.0.md) — goals, principles, context/component/sequence view (naratif + Mermaid), data/integration/security/deployment architecture, risks, dan open decisions
- [`ECMP_NFR_Specification_v0.1.md`](./ECMP_NFR_Specification_v0.1.md) — NFR-001, non-functional requirements (availability, latency, throughput, kapasitas, RTO/RPO, security, auditability, observability) dengan nilai baseline DEC-005

## Minimum Contents (v1)
- [x] Architecture overview (C4 Context/Container — naratif, diagram formal menyusul di `23 Assets`)
- [x] Domain/module component view
- [x] Integration architecture
- [x] Data architecture
- [x] Security architecture (high-level)
- [x] Deployment view (high-level, teknologi masih Open Decision)
- [x] NFR targets (performance, availability, scalability) — baseline per DEC-005, lihat `ECMP_NFR_Specification_v0.1.md`; verifikasi performance menunggu environment SIT (Test Strategy §6)

## Template Sections
1. Goals & Constraints
2. Architecture Principles (technical)
3. Context Diagram
4. Container / Component Diagram
5. Runtime & Sequence Views
6. Data Architecture
7. Integration Architecture
8. Security Architecture
9. Deployment Architecture
10. Risks & Trade-offs
11. ADR References

## Naming
`ECMP_Solution_Architecture_vX.Y.docx|md`

## Boundary
- Solution Architecture = penerapan end-to-end untuk ECMP
- Reference Architecture (`19`) = pola standar bersama
- Domain Architecture (`20`) = detail per domain

## Related
- `../05 Architecture Decision Records`
- `../07 API Catalog`
- `../08 Event Catalog`
- `../09 Integration Catalog`
- `../19 Reference Architecture`
- `../20 Domain Architecture`
- `../23 Assets`
