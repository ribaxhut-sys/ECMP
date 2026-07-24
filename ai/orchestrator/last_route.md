# AI Orchestrator Route (Registry-driven)

| Field | Value |
|---|---|
| ID | ORCH-ROUTE-002 |
| Version | 0.1 |
| Owner | Automation |
| Reviewer | PMO / Enterprise Architecture |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | auto |
| Next Review | auto |

> Task: CAPABILITY-008 Complaint SLA Foundation

## Capability: Implement Feature
- ID: `CAP-IMPLEMENT-FEATURE`
- Owner: Tech Lead
- Status: stable
- Input: Sprint + FR IDs
- Output: Code changes + tests + docs sync notes

## Agent: Coding Agent
- ID: `AGENT-CODE`
- Tool role: Claude in Cursor
- Memory: `v1`
- Domain pack: `ecmf`

## Prompt
- Ref: `implement-feature@v1`
- Path: `ai-platform\prompts\implement-feature\v1\prompt.md`

## Context Pack

- `ai-platform/policies/ai-rules.md`
- `ai-platform/memory/v1/memory_global.md`
- `ai/sprint/Sprint-01.md`
- `ai-platform/prompts/implement-feature/v1/prompt.md`
- `ai-platform/packs/ecmf/pack.md`
- `ai-platform/packs/ecmf/pack.md`
- `03 Functional Requirements/ECMP_FRD_ECMF_v0.1.md`

## RAG Top Hits

- `07 API Catalog/README.md` (score=0.2231)
- `07 API Catalog/API_CATALOG.generated.md` (score=0.211)
- `ai/sprint/Sprint-01.md` (score=0.1737)
- `ai/01_business.md` (score=0.1605)
- `ai/generated/memory_global.md` (score=0.1505)

## Next
1. Load prompt + context in the selected tool role
2. Prefer Domain Pack over whole-repo context
3. After run, capture outcome via telemetry/eval gates for prompt changes
