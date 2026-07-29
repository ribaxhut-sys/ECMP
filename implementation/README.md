# ECMP Implementation

| Field | Value |
|---|---|
| ID | IMP-000 |
| Version | 0.2 |
| Owner | Engineering Manager / Tech Lead |
| Reviewer | Solution Architect |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2026-10-21 |

## GO Status
**Sprint-01 GO = slice create/get + G0 platform floor (per `../27 Project Decisions/DEC-002_Build_Authorization_G0_v1.0.md`).**
Build-1 features beyond the slice wait for G0 exit sign-off.

## Active slice
- Spec: `../03 Functional Requirements/ECMP_FRD_ECMF_v0.1.md` (FRD-001 v0.2)
- Sprint: `../ai/sprint/Sprint-01.md`
- Stack ADR: ADR-004 · Layering: ADR-005 · Versioning: ADR-006 · Auth: ADR-007
- Backend: `backend/` (FastAPI + SQLAlchemy/Alembic; audit + outbox transactional)

## Structure
```text
implementation/
├── backend/          ← Sprint-01 active (app/, alembic/, tests/)
├── infrastructure/   ← docker-compose.yml (PostgreSQL DEV; optional Keycloak profile auth)
├── portal/           ← Developer Portal (EKR tooling, bukan produk)
├── frontend/         ← deferred (ADR menyusul sebelum sprint UI)
├── tests/            ← e2e lintas-service (belum dipakai)
└── deployment/       ← menunggu keputusan platform (14 Deployment Standards)
```

## Start coding
```bash
docker compose -f implementation/infrastructure/docker-compose.yml up -d
cd implementation/backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
pytest -q
```

### Optional: local IdP (SEC-MIG Phase 1 — no app wiring)

```bash
docker compose -f implementation/infrastructure/docker-compose.yml --profile auth up -d
```

See `infrastructure/keycloak/README.md`. Does **not** change application authentication.
