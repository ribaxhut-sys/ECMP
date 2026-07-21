# Enterprise Numbering Standard

| Field | Value |
|---|---|
| ID | EAR-STD-002 |
| Version | 1.0 |
| Owner | Enterprise Architecture |
| Reviewer | BA Lead / Solution Architect |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Memberi identitas stabil pada artefak, tidak hanya mengandalkan nama file.

## Prefix Registry

| Prefix | Artifact Type | Folder |
|---|---|---|
| EAR-IDX | Repository Index | 00 |
| EAR-STD | Repository Standards | 00 |
| BP | Business Blueprint item/capability | 01 |
| BR | Business Rule | 02 |
| FRD / FR | Functional Requirements Document / Requirement | 03 |
| SA | Solution Architecture | 04 |
| ADR | Architecture Decision Record | 05 |
| DD | Data Dictionary entity/doc | 06 |
| API | API operation/service contract | 07 |
| EVT | Domain Event | 08 |
| INT | Integration | 09 |
| SEC | Security standard/control | 10 |
| SLA / KPI | SLA rule / KPI metric | 11 |
| UX | UI/UX spec | 12 |
| TS | Test Strategy / Test Suite doc | 13 |
| TC | Test Case | 13 / QA repo |
| DEP | Deployment standard | 14 |
| OPS | Operations runbook | 15 |
| REL | Release plan/notes | 16 |
| CMP | Compliance control/doc | 17 |
| GOV | Governance doc | 18 |
| AR | Architecture Review | 18/reviews |
| EX | Exception Request | 18/reviews |
| REF | Reference Architecture pattern | 19 |
| DOM | Domain Architecture doc | 20 |
| STD | Technical Standard (stack) | 21 |
| ENG | Engineering Handbook item | 22 |
| AST | Asset pack/doc | 23 |
| TPL | Template | 24 |
| GLS | Glossary term/doc | 25 |
| TRC | Traceability matrix/doc | 26 |
| DEC | Project Decision | 27 |
| OQ | Open Question | 27 |

## Format
```text
<PREFIX>-<NNN>
```
Contoh: `BP-001`, `SA-001`, `FRD-001`, `API-001`, `ADR-001`, `STD-001`, `TC-001`

## Rules
1. Nomor unik per prefix.
2. Nomor tidak dipakai ulang meski dokumen deprecated.
3. Nama file boleh berubah; ID tidak boleh berubah.
4. Traceability memakai ID ini sebagai kunci relasi.
5. Jangan campur `TS` (Test Strategy) dengan `STD` (Technical Standard).

## Example Chain
`BP-001 → BR-001 → FR-001 → API-001 / EVT-001 → TC-001`
