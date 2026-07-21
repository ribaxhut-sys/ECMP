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

## Two Layers (in one monorepo for now)

```text
EKR (source of truth)
├── 00–27 knowledge/governance folders
├── ai-platform/ ← canonical AI layer (policies, memory, prompts, packs)
├── ai/          ← legacy compatibility context pack (project/sprint notes)
├── docs/        ← MkDocs portal
└── tools/       ← self-governance automation

implementation/  ← ECMP code (backend/frontend/infra/portal/tests/deployment)
```

> Layer AI kanonik = `ai-platform/` (lihat `.cursor/rules/ecmp-ai-platform.mdc`); `ai/` dipertahankan sebagai compatibility pack — sprint brief tetap di `ai/sprint/`.

## Development Status
**Sprint-01 = GO untuk slice create/get + G0 platform floor (per DEC-002)** — Build-1 di luar slice menunggu G0 exit sign-off.  
**Engineering Platform Wave A/B = live** (ontology, RAG, orchestrator, developer portal, feedback loop)

### Start coding (Sprint-01)
Jalur kanonik (Postgres + Alembic — lihat `implementation/backend/README.md`):

```bash
cd implementation/infrastructure && docker compose up -d
cd ../backend
pip install -r requirements.txt
cp .env.example .env   # isi ECMP_DATABASE_URL + token dev
alembic upgrade head
uvicorn app.main:app --reload
pytest -q
```

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
