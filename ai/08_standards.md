# 08 — Engineering Standards Context

| Field | Value |
|---|---|
| ID | AI-CTX-008 |
| Version | 1.0 |
| Owner | Tech Lead |
| Reviewer | Engineering Manager |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Must Follow
- Technical Standards (`21`) — language/framework/platform
- Engineering Handbook (`22`) — Git, PR, review
- Repository Standards (`00`) — metadata, numbering, approval
- AI Rules (`ai-platform/policies/ai-rules.md`)

## PR Minimum
- Linked FR/ADR/Sprint item when relevant
- Tests for behavior changes
- OpenAPI/Event/Traceability updated if contracts change
- No secrets
- Docs synced if design changed

## Approved Stack (ADR-004)
- Backend: Python 3.12+ + FastAPI
- Persistence: PostgreSQL + Alembic — **wajib untuk CI, shared env, dan seterusnya; in-memory tidak lagi diizinkan sejak G0 (DEC-002)**. Pengecualian tunggal: **SQLite fallback hanya untuk eksperimen dev lokal tanpa Docker** (default `settings.py`); bukan acuan skema — skema otoritatif tetap migrasi Alembic (`create_all` di lifespan **hanya dieksekusi bila URL SQLite**; di Postgres skema wajib dari Alembic). Test suite membangun skema via `alembic upgrade head`, bukan `create_all`. DoD/CI selalu jalan di Postgres.
- Contracts: OpenAPI (`/v1`, ADR-006) + Event YAML (outbox, ADR-009)
- Layering minimal per ADR-005 (routes → service → models; service bebas FastAPI)
- Error envelope `{code, message, details?}` untuk semua 4xx/5xx
- Frontend: deferred (React + TypeScript candidate later)
- Detail: ADR-004/005/006/007 di `05 Architecture Decision Records/`
- Backend rule pack: `.cursor/rules/ecmp-backend.mdc`
