# ECMP Enterprise Architecture Portal

| Field | Value |
|---|---|
| ID | EAR-PORTAL-001 |
| Version | 0.2 |
| Owner | Enterprise Architecture |
| Reviewer | PMO |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

Portal utama untuk **Enterprise Knowledge Repository (EKR)** dan **AI Development Platform** ECMP.

## Dua Lapisan

```text
Enterprise Knowledge Repository (EKR)
├── Business / Architecture / Standards / Governance
├── AI Context Pack
└── Templates

ECMP Implementation
├── Backend / Frontend / Infrastructure
├── Tests
└── Deployment
```

Saat ini keduanya masih dalam satu monorepo:
- EKR = folder `00`–`27` + `ai-platform/` (canonical) + `ai/` (compatibility) + `docs/`
- Implementation = `implementation/`

## Official Lifecycle

Lihat [Lifecycle](lifecycle.md):

`Idea → Blueprint → Rules → Solution/Domain Architecture → FRD → AI Context sync → Cursor/Claude → Implementation → Test → Deploy → Ops → Feedback (multi-target)`

## Pintu Masuk Cepat

| Role | Start |
|---|---|
| Business / BA | Business → Blueprint / Glossary |
| Architect | Architecture → Patterns / Knowledge Graph |
| Engineer | AI Workflow → Rules + Sprint + Cursor Integration |
| QA | Traceability + Events/API catalogs |
| All | Governance → Dashboard / Health Report · Lifecycle |

## AI Development Platform

Layer AI **kanonik = `ai-platform/`** (policies, memory versioned, prompts versioned, domain packs); `ai/` tetap sebagai compatibility context pack (lihat `.cursor/rules/ecmp-ai-platform.mdc`). Urutan konteks:

1. `ai-platform/policies/ai-rules.md` (fallback: `ai/rules.md`)
2. `ai-platform/memory/v1/memory_global.md` + domain memory (kompatibilitas: `ai/generated/memory_global.md`)
3. `ai/00_project.md` … `10_prompts.md`
4. `ai/domain/*`, `ai/sprint/*`, `ai-platform/prompts/*`
5. `ai/knowledge-graph/` (generated)

## Engineering Platform (Wave A/B)

```bash
python tools/eos.py
python tools/eos.py rag --query "create case"
python tools/eos.py orchestrate --task "implement FR-001"
```

Developer Portal:
```bash
cd implementation/portal
uvicorn app:app --reload --port 8030
```

Capabilities:
- Ontology + enriched Knowledge Graph
- RAG search (local TF-IDF MVP)
- Feedback metrics loop
- AI Orchestrator v1
- Impact / Coverage / Trends / EOS actions in one UI
