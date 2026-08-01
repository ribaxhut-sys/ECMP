# 19 Reference Architecture


| Field | Value |
|---|---|
| ID | REF-000 |
| Version | 0.1 |
| Owner | Chief Architect |
| Reviewer | Tech Leads |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Standar pola arsitektur yang dipakai seluruh tim ECMP. Ini bukan desain satu modul, melainkan referensi bersama.

## Owner
- Document Owner: Solution Architect / Chief Architect
- Reviewers: Tech Leads, Security Architect

## Status
Approved baseline — `PATTERNS.md` (REF-001 v0.2) memuat pola dipakai vs pola berkondisi adopsi.

## Contents
- `PATTERNS.md` (REF-001) — termasuk aturan dependensi ADR-005, transactional outbox (ADR-009), ACL Customer Master (ADR-002), business action pattern
- `ECMP_RA_CAP008_Mode_A_v1.0.md` (REF-CAP008-001) — **Baseline** as-built CAP-008 Mode A (program CLOSED; lab)

## Minimum Contents (v1)
- [x] Layered Architecture — dengan aturan dependensi + diagram (PATTERNS §1)
- [x] Clean Architecture guidance — diwujudkan sebagai minimal split ADR-005; full layering berkondisi (PATTERNS §1)
- [x] Hexagonal (Ports & Adapters) — PATTERNS §5, kasus khusus ACL §4
- [x] Repository Pattern — PATTERNS §6 (eksplisit: belum dipakai, kondisi adopsi G1)
- [x] Event Driven Pattern — PATTERNS §7 via outbox
- [x] CQRS (optional / when adopted) — PATTERNS §8 (ditunda per ADR-005)
- [x] When-to-use / when-not-to-use matrix — PATTERNS §9

## Boundary
- Reference Architecture = pola generik yang disetujui
- Solution Architecture (`04`) = penerapan pola untuk ECMP end-to-end
- Domain Architecture (`20`) = penerapan per domain

## Related
- `../04 Solution Architecture`
- `../20 Domain Architecture`
- `../05 Architecture Decision Records`
- `../23 Assets`
