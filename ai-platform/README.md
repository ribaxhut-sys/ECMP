# ECMP AI Platform

| Field | Value |
|---|---|
| ID | AIP-000 |
| Version | 1.0 |
| Owner | Enterprise Architecture |
| Reviewer | Eng Manager / Architecture Board |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

AI Platform is a **subsystem**, not a set of helper scripts.

```text
ai-platform/
├── orchestrator/
├── agents/                 # Agent Registry
├── capabilities/           # Capability Registry
├── memory/vN/              # Versioned AI memory
├── rag/
├── prompts/<name>/vN/      # Versioned prompts
├── policies/               # AI rules & governance policies
├── packs/<domain>/         # Domain Knowledge Packs
├── evaluation/             # Golden set + benchmark
├── telemetry/              # Run logs + reports
└── ontology/               # Semantic types (shared)
```

## Compatibility
Legacy folder `ai/` remains as compatibility shim pointing here.
Engineering OS deterministic tools remain in `tools/`.

## Quick commands
```bash
python tools/eos.py orchestrate --task "implement FR-001"
python tools/eos.py packs --domain ECMF
python tools/eos.py eval
python tools/eos.py telemetry
```
