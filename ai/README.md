# AI Context Pack (Compatibility Shim)

| Field | Value |
|---|---|
| ID | AI-000 |
| Version | 1.2 |
| Owner | Enterprise Architecture |
| Reviewer | Engineering Manager |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

> **Canonical AI subsystem is now `ai-platform/`.**  
> This `ai/` folder remains as a compatibility context pack (project notes, sprint briefs, domain digests).

## Prefer AI Platform

| Concern | Canonical path |
|---|---|
| Rules / governance | `ai-platform/policies/` |
| Versioned memory | `ai-platform/memory/vN/` |
| Versioned prompts | `ai-platform/prompts/<name>/vN/` |
| Agents / capabilities | `ai-platform/agents/`, `ai-platform/capabilities/` |
| Orchestrator | `ai-platform/orchestrator/` |
| RAG index | `ai-platform/rag/` |
| Domain packs | `ai-platform/packs/<domain>/` |
| Evaluation / telemetry | `ai-platform/evaluation/`, `ai-platform/telemetry/` |

## What stays in `ai/`
- Compact grounding docs (`00_project.md` … `10_prompts.md`)
- Active sprint briefs (`sprint/`)
- Domain digests (`domain/`)
- Generated memory mirror (`generated/`)

> `ai/rules.md` and `ai/prompts/*` are deprecated pointer stubs — the content lives in
> `ai-platform/policies/ai-rules.md` and `ai-platform/prompts/<name>/v1/prompt.md`.
> `ai/orchestrator/router.yaml` is a deprecated legacy router; canonical is `ai-platform/orchestrator/router.yaml`.

## Commands
```bash
python tools/eos.py orchestrate --task "implement FR-001"
python tools/eos.py packs --domain ECMF
python tools/eos.py eval
python tools/eos.py telemetry
python tools/eos.py --all
```

## Official Lifecycle
See `09_workflow.md` and portal page `docs/lifecycle.md`.
