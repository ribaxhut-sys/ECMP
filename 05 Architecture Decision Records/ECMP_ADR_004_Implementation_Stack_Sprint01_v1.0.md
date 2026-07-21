# ECMP_ADR_004_Implementation_Stack_Sprint01_v1.0

| Field | Value |
|---|---|
| ID | ADR-004 |
| Version | 1.0 |
| Owner | Solution Architect / Tech Lead |
| Reviewer | Engineering Manager / Security |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

- ADR Status: Accepted
- Date: 2026-07-21
- Decision Owners: Tech Lead, Solution Architect
- Related Domains: Core Platform, ECMF, Implementation

## Context
Sprint-01 membutuhkan keputusan stack agar implementasi tidak tertahan. Candidate stack sudah disebut di AI standards, tetapi belum dikunci sebagai ADR.

## Decision Drivers
- Kecepatan bootstrap untuk thin-slice API
- Kesesuaian dengan AI coding workflow (Cursor/Claude)
- Kontrak OpenAPI-first
- Operational simplicity untuk fase awal

## Options Considered
### Option A — Python + FastAPI + PostgreSQL
- Pros: cepat untuk API, OpenAPI native, ekosistem matang, cocok untuk iterasi
- Cons: concurrency model perlu disiplin untuk workload besar (bukan blocker Sprint-01)

### Option B — Node/TypeScript + NestJS + PostgreSQL
- Pros: satu bahasa dengan frontend TS
- Cons: bootstrap & opini framework lebih berat untuk slice pertama

### Option C — Java + Spring Boot + PostgreSQL
- Pros: enterprise-ready
- Cons: kecepatan awal lebih lambat untuk tim yang belum distandarkan

## Decision
Untuk Sprint-01 dan fondasi awal ECMP Implementation:
- **Backend:** Python 3.12+ dengan **FastAPI**
- **Persistence:** **PostgreSQL**
- **Migrations:** Alembic
- **API Contract:** OpenAPI 3 (source di `07 API Catalog/openapi`)
- **Events:** contract-first via `08 Event Catalog/events/events.yaml` (broker tech follow-up)
- **Auth (slice):** Bearer token validated at API gateway/app middleware; role claims include `cases:create`, `cases:read`
- **Frontend:** deferred (API-first). Future default candidate React + TypeScript (separate ADR when UI sprint starts)
- **Code location:** `implementation/backend`

## Consequences
### Positive
- Tim dapat mulai coding segera dengan kontrak yang jelas
- AI assistants memiliki stack target yang eksplisit

### Negative / Trade-offs
- Frontend stack belum dikunci
- Message broker technology masih follow-up (in-process/outbox acceptable for local Sprint-01)

### Follow-up Actions
- [ ] Bootstrap FastAPI project under `implementation/backend`
- [ ] Add ADR for message broker when moving beyond local/dev stub
- [ ] Add ADR for frontend stack before UI sprint
