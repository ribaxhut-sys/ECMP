# ECMP Enterprise Knowledge Repository (EKR)
## + AI Development Platform

Living knowledge hub and AI context platform for **Enterprise Complaint Management Platform (ECMP)**.

> Official expansion of ECMP per Blueprint v2.1 (business Source of Truth, DEC-001): **Enterprise Complaint Management Platform** — end-to-end complaint & inquiry management. ECMP is **not** a Customer Master system of record (BR-003 / BR-CRM-01).

| Field | Value |
|---|---|
| ID | EAR-IDX-000 |
| Version | 2.1 |
| Owner | Enterprise Architecture |
| Reviewer | PMO / Solution Architect |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Local stack foundation (v1.0.0)

Application foundation Production release: authentication, complaints, assignments,
escalations, timelines, reporting, user management, and dashboard.

```text
backend/     FastAPI + SQLAlchemy 2 + Alembic + PostgreSQL
frontend/    Next.js (App Router) + TypeScript + Tailwind CSS
database/    Postgres init scripts
docs/        MkDocs portal + stack notes + release artifacts
```

```bash
cp .env.example .env
docker compose up --build
```

| Service  | URL                          |
|----------|------------------------------|
| Frontend | http://localhost:3000        |
| Login    | http://localhost:3000/login  |
| Backend  | http://localhost:8000        |
| Liveness | http://localhost:8000/live   |
| Readiness| http://localhost:8000/ready  |
| Postgres | localhost:5433               |

### Operator docs (foundation — security / release / deploy)

```text
Release → Deployment → Startup → Security Operations → Backup/Restore/Recovery → Rollback
```

| Step | Entry |
|---|---|
| Release | [16 Release Management](./16%20Release%20Management/README.md) (REL-SEC-001) |
| Deployment hub | [docs/deployment/README.md](./docs/deployment/README.md) |
| Deploy checklist | [docs/deployment-checklist.md](./docs/deployment-checklist.md) (DEP-CHK-V1) |
| Startup | [docs/deployment/STARTUP_CHECKLIST.md](./docs/deployment/STARTUP_CHECKLIST.md) |
| Security / backup ops | [15 Operations Runbook](./15%20Operations%20Runbook/README.md) |
| Rollback | [docs/releases/ROLLBACK_v1.0.0.md](./docs/releases/ROLLBACK_v1.0.0.md) |

**Precedence:** REL-SEC-001 → DEP-CHK-V1 → START-CHK-001.  
Historical Sprint-08 DEP-CHK-001 is **not** for foundation production cutover.

Release notes: [docs/releases/v1.0.0.md](./docs/releases/v1.0.0.md)  
Local details: [docs/local-stack.md](./docs/local-stack.md)

## Two Layers (in one monorepo for now)

```text
EKR (source of truth)
├── 00–27 knowledge/governance folders
├── ai-platform/ ← canonical AI layer (policies, memory, prompts, packs)
├── ai/          ← legacy compatibility context pack (project/sprint notes)
├── docs/        ← MkDocs portal
└── tools/       ← self-governance automation

backend/ frontend/ database/  ← ECMP foundation stack (canonical app SoT)
implementation/               ← Historical / optional packs (slice, IdP, portal)
```

> Layer AI kanonik = `ai-platform/` (lihat `.cursor/rules/ecmp-ai-platform.mdc`); `ai/` dipertahankan sebagai compatibility pack — sprint brief tetap di `ai/sprint/`.

## Development Status
**Foundation stack** = canonical application path for SEC-MIG / shared / production docs.  
**Sprint-01 slice packs** under `implementation/` = Historical / optional (see [implementation/README.md](./implementation/README.md)).  
**Engineering Platform Wave A/B = live** (ontology, RAG, orchestrator, developer portal, feedback loop)

### Start coding (foundation)

```bash
cp .env.example .env
docker compose up --build
# or host: backend/ + frontend/ per docs/local-stack.md
```

### Optional Historical pack (Sprint-01 case-service)

Only when deliberately running the legacy pack — not production SoT:

```bash
cd implementation/infrastructure && docker compose up -d
cd ../backend
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

See [implementation/README.md](./implementation/README.md).
### Start Developer Portal (Wave B)
```bash
python tools/eos.py rag-index
python tools/eos.py feedback
cd implementation/portal
pip install -r requirements.txt
uvicorn app:app --reload --port 8030
```
Open http://127.0.0.1:8030

## Start Here

1. Active Sprint (GO = slice + G0 floor, DEC-002): [ai/sprint/Sprint-01.md](./ai/sprint/Sprint-01.md)
2. FRD ECMF: [03 Functional Requirements/ECMP_FRD_ECMF_v0.1.md](./03%20Functional%20Requirements/ECMP_FRD_ECMF_v0.1.md)
3. Stack ADR: [ADR-004](./05%20Architecture%20Decision%20Records/ECMP_ADR_004_Implementation_Stack_Sprint01_v1.0.md)
4. Developer Portal: `implementation/portal`
5. MkDocs: `python -m mkdocs serve`
6. DX Launcher: `python tools/eos.py`
7. AI Rules: [ai-platform/policies/ai-rules.md](./ai-platform/policies/ai-rules.md)

## AI Tool Roles

| Tool | Role |
|---|---|
| ChatGPT | Chief Enterprise Architect |
| Claude (in Cursor) | Senior Software Engineer |
| Cursor | Development workspace (`.cursor/rules` enforced) |

## Official Lifecycle

```text
Idea → Blueprint → Rules → Solution/Domain Architecture → FRD
    → AI Context sync → Cursor/Claude → Implementation
    → Test → Release → Deploy → Ops → Feedback (multi-target)
```

Detail: `ai/09_workflow.md` · portal: `docs/lifecycle.md`

## AI Startup Sequence

```text
rules.md → 00_project → 01_business → 02_architecture
        → domain/<name> → sprint/Sprint-XX → implement → sync docs
```

## Engineering OS (v4+)

Treat this repository as an internal product. Roadmap: `00 Repository Guide/ENGINEERING_OS_ROADMAP.md`

### Developer Experience (one door)

```bash
python tools/eos.py
```

Or non-interactive:

```bash
python tools/eos.py --all
python tools/eos.py impact --id BR-001
python tools/eos.py domain --name ECMF
python tools/eos.py trends
```

| Capability | Command |
|---|---|
| DX Menu | `python tools/eos.py` |
| Impact Analysis | `python tools/eos.py impact --id BR-001` |
| AI Memory | `python tools/eos.py memory` |
| Domain Navigator | `python tools/eos.py domain --name ECMF` |
| Doc Coverage | `python tools/eos.py coverage` |
| Knowledge Graph | `python tools/eos.py graph` |
| Repo Metrics | `python tools/eos.py metrics` |
| Repo Trends | `python tools/eos.py trends` |
| RAG Index/Search | `python tools/eos.py rag-index` / `rag --query "..."` |
| AI Orchestrator | `python tools/eos.py orchestrate --task "..."` |
| Feedback Metrics | `python tools/eos.py feedback` |
| AI Reviewer | `python tools/eos.py review` |
| Developer Portal | http://127.0.0.1:8030 |

## Quick Commands

```bash
pip install -r requirements-docs.txt
python tools/eos.py --all
python -m mkdocs serve
```

## Prompt Library
See `ai-platform/prompts/<name>/v1/prompt.md` (architecture-review, code-review, frd-generator, implement-feature, ...). `ai/prompts/` berisi pointer stub kompatibilitas.
