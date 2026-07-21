# Engineering OS / Platform Roadmap

| Field | Value |
|---|---|
| ID | EOS-RM-001 |
| Version | 3.0 |
| Owner | Enterprise Architecture |
| Reviewer | PMO / Eng Manager |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Eight-Phase Journey
1. Documentation ✅  
2. Repository ✅  
3. Enterprise Repository ✅  
4. Knowledge Repository ✅  
5. Engineering Operating System ✅  
6. Engineering Intelligence ✅ (Wave A)  
7. Engineering Platform ✅ (Wave B)  
8. AI Platform Subsystem ✅ (Wave C1–C3)

## Product Vision
Make ECMP EKR a smart Engineering Platform: understand artifact relationships, retrieve relevant context, coordinate human+AI work through a governed AI Platform, and measure whether development speed/quality/docs consistency improve.

## Wave A — Engineering Intelligence ✅
- Semantic Knowledge Layer (now `ai-platform/ontology`)
- Enriched Knowledge Graph generator
- RAG/Vector Search MVP (`ai-platform/rag`, TF-IDF local index)
- Feedback Metrics Loop (`feedback_metrics.py`)

## Wave B — Engineering Platform ✅
- AI Orchestrator (now registry-driven)
- Developer Portal (`implementation/portal`) combining docs, RAG, dashboards, impact, EOS actions, orchestrator

## Wave C — AI Platform Subsystem ✅
### C1 Agent & Capability Architecture
- `ai-platform/agents/` registry
- `ai-platform/capabilities/registry.yaml`
- Orchestrator routes by capability ID (`orchestrator/router.yaml` v2)

### C2 Memory / Prompt Versioning + Domain Packs
- Versioned memory `ai-platform/memory/vN/`
- Versioned prompts `ai-platform/prompts/<name>/vN/`
- Domain Knowledge Packs `ai-platform/packs/<domain>/`

### C3 Evaluation, Telemetry, Governance
- Golden questions + `python tools/eos.py eval`
- Telemetry runs/reports + `python tools/eos.py telemetry`
- Policies under `ai-platform/policies/`

## Capability Entry Points

| Capability | Command / URL |
|---|---|
| DX Launcher | `python tools/eos.py` |
| RAG Index/Search | `python tools/eos.py rag-index` / `rag --query "..."` |
| Orchestrator | `python tools/eos.py orchestrate --task "..."` |
| Domain Pack | `python tools/eos.py packs --domain ECMF` |
| Evaluation | `python tools/eos.py eval` |
| Telemetry | `python tools/eos.py telemetry` |
| Feedback Metrics | `python tools/eos.py feedback` |
| Developer Portal | `uvicorn app:app --app-dir implementation/portal --port 8030` |
| Run all | `python tools/eos.py --all` |

## Next (post Wave C)
- Embedding-based vector DB
- Multi-agent collaboration runtime
- Portal auth + persisted action history
- Digital Agent product reuse of this platform kernel
