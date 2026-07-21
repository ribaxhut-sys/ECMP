# AI Platform

| Field | Value |
|---|---|
| ID | EAR-PORTAL-AIP-001 |
| Version | 1.0 |
| Owner | Enterprise Architecture |
| Reviewer | Eng Manager |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

Canonical AI subsystem lives under `ai-platform/`.

```bash
python tools/eos.py orchestrate --task "implement FR-001"
python tools/eos.py packs --domain ECMF
python tools/eos.py eval
python tools/eos.py telemetry
```

See repository root `ai-platform/README.md` for structure (agents, capabilities, memory, prompts, packs, evaluation, telemetry).
